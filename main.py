# coding: utf-8

import wx
import re
from http import *
from util import *
from collections import OrderedDict
import urllib

class GreenMulti2(wx.Frame, Http, Utility):

	currentMenu = ''

	def __init__(self, cookie=''):
		wx.Frame.__init__(self, None, -1, u'초록멀티 2.0', wx.DefaultPosition, wx.Size(500, 500))
		Http.__init__(self, 'han.kbuwel.or.kr', cookie=cookie)
		Utility.__init__(self)

		# 메뉴바
		menuBar = wx.MenuBar()
		fileMenu = wx.Menu()

		self.loginMI = wx.MenuItem(fileMenu, -1, u"로그인\tCtrl+L")
		fileMenu.AppendItem(self.loginMI)
		self.Bind(wx.EVT_MENU, self.OnLogin, self.loginMI)

		self.xxxMI = wx.MenuItem(fileMenu, -1, u"메뉴관리")
		fileMenu.AppendItem(self.xxxMI)
		self.Bind(wx.EVT_MENU, self.OnMenuManage, self.xxxMI)

		quitMI = wx.MenuItem(fileMenu, -1, u"종료")
		fileMenu.AppendItem(quitMI)
		self.Bind(wx.EVT_MENU, self.OnClose, quitMI)

		menuBar.Append(fileMenu, u'파일(&F)')
		self.SetMenuBar(menuBar)

		panel = wx.Panel(self, -1)
		panel.SetAutoLayout(True)

		self.listCtrl = wx.ListCtrl(panel, -1, wx.Point(10, 10), wx.Size(480, 480), wx.LC_REPORT | wx.LC_SINGLE_SEL)
		self.listCtrl.InsertColumn(0, u'메뉴', width=430)
		self.listCtrl.InsertColumn(1, u'Code', width=50)
		self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

		self.Centre()
		self.Show()

		self.LoadTreeMenu()
		self.Display()
		self.Login()


	def OnClose(self, e):
		self.Close()

	def OnMenuManage(self, e):
		mgr = MenuManager(self)
		mgr.ShowModal()
		mgr.Destroy()


	def OnLogin(self, e):
		if self.loginMI.GetText() == u'로그인\tCtrl+L':
			self.Login()
		else:
			self.Logout()

	def Login(self):
		try:
			kbuid = self.Decrypt(self.ReadReg('kbuid'))
			if not kbuid: kbuid = InputBox(self, u'넓은마을 로그인', u'아이디')

			kbupw = self.Decrypt(self.ReadReg('kbupw'))
			if not kbupw: kbupw = InputBox(self, u'넓은마을 로그인', u'비밀번호', pwd=1) 
			if not kbuid or not kbupw: return MsgBox(self, u'알림', u'사용자 아이디와 비밀번호는 필수 입력사항입니다.')

			params = 'url=http%3A%2F%2Fweb.kbuwel.or.kr&mb_id=' + kbuid + '&mb_password=' + kbupw

			self.Post('/bbs/login_check.php', params)
			if self.response.getheader('Location') and 'web.kbuwel.or.kr' in self.response.getheader('Location'):
				self.cookie = self.response.getheader('set-cookie')
			else:
				self.Logout(u'넓은마을 로그인에 실패했습니다. 아이디와 비밀번호를 정확하게 입력해 주세요.')
				return

			# 초록등대 정회원 확인
			self.Get('/bbs/board.php?bo_table=green61&cl=green')
			title = self.soup.head.title.getText()
			if not title.startswith(u'오류')			:
				self.WriteReg('kbuid', self.Encrypt(kbuid))
				self.WriteReg('kbupw', self.Encrypt(kbupw))
				self.loginMI.SetText(u'로그아웃\tCtrl+L')
				self.Play("start.wav")
			else:
				self.Logout(u'초록등대 정회원이 아닙니다. 회원 가입 및 등급 관련 문의는 초록등대 운영자에게 해 주세요.')
				return

		except:
			pass


	def Logout(self, msg=u'로그아웃하였습니다. 로그인 정보를 삭제했습니다.'):
		try:
			self.WriteReg('kbuid', '')
			self.WriteReg('kbupw', '')
			self.cookie = ''
			self.loginMI.SetText(u'로그인')
			MsgBox(self, u'알림', msg)
		except:
			pass

	def Display(self, menucode='top'):
		if not menucode in self.dTree: return
		(title, mommy, submenu) = self.dTree[menucode]
		if submenu.startswith('/'):
			listDialog = ArticleList(self, menucode, self.cookie)
			listDialog.ShowModal()
			return False

		self.currentMenu = menucode
		self.listCtrl.DeleteAllItems()
		for c in submenu.split('|'):
			if not c in self.dTree: continue
			(name, mother, sub) = self.dTree[c]
			index = self.listCtrl.InsertStringItem(sys.maxint, name)
			self.listCtrl.SetStringItem(index, 1, c)
		self.listCtrl.Focus(0)
		self.listCtrl.Select(0)
		return True

	def OnKeyDown(self, e):
		key = e.GetKeyCode()
		if key == wx.WXK_RETURN:
			self.KeyReturn()
		elif key == wx.WXK_ESCAPE or (e.GetModifiers() == wx.MOD_ALT and key == wx.WXK_LEFT):
			self.KeyEscape()
		elif key == wx.WXK_UP:
			self.KeyUpArrow()
			e.Skip()
		elif key == wx.WXK_DOWN:
			self.KeyDownArrow()
			e.Skip()
		else:
			e.Skip()

	def KeyReturn(self):
		index = self.listCtrl.GetFocusedItem()
		if index == -1: return
		code = self.listCtrl.GetItemText(index, 1)
		r = self.Display(code)
		if r: self.Play('pageNext.wav')

	def KeyEscape(self):
		mother = self.dTree[self.currentMenu][1]
		if not mother: return self.Play('beep.wav')
		self.Display(mother)
		self.Play('pagePrev.wav')


	def KeyUpArrow(self):
		index = self.listCtrl.GetFocusedItem()
		if index <= 0:
			self.Play('beep.wav')

	def KeyDownArrow(self):
		count = self.listCtrl.GetItemCount()
		index = self.listCtrl.GetFocusedItem()
		if index == count - 1:
			self.Play('beep.wav')





class ArticleList(wx.Dialog, Utility, Http):

	currentMenu = ''
	lArticles = []

	def __init__(self, parent, code, cookie=''):
		Utility.__init__(self)
		wx.Dialog.__init__(self, parent, -1, '', wx.DefaultPosition, (500, 500))
		Http.__init__(self, 'han.kbuwel.or.kr', cookie=cookie)
		self.currentMenu = code

		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.listCtrl = wx.ListCtrl(self, -1, wx.Point(10, 10), wx.Size(480, 480), wx.LC_REPORT | wx.LC_SINGLE_SEL)
		self.listCtrl.InsertColumn(1, u'제목', width=400)
		self.listCtrl.InsertColumn(2, u'작성자', width=80)
		self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

		self.GetList(self.dTree[self.currentMenu][2])
		self.Display()
		self.Play('pageNext.wav')


	def OnClose(self, e):
		self.Play('pagePrev.wav')
		self.Destroy()

	def OnKeyDown(self, e):
		key = e.GetKeyCode()
		if key == wx.WXK_ESCAPE or (e.GetModifiers() == wx.MOD_ALT and key == wx.WXK_LEFT):
			self.OnClose(e)
		elif key == wx.WXK_PAGEDOWN:
			self.NextPage()
		elif key == wx.WXK_PAGEUP:
			self.PreviousPage()
		elif key == wx.WXK_RETURN:
			self.OpenArticle()

		else:
			e.Skip()


	def GetList(self, selector):
		self.lArticles = []
		self.Get(selector)

		links = self.soup('a', href=re.compile('wr_id='))
		for link in links:
			self.lArticles.append((link.getText(), link.parent.nextSibling.nextSibling.string, link['href']))


	def Display(self):
		self.listCtrl.DeleteAllItems()
		self.SetTitle(self.soup.head.title.string)
		for text, author, href in self.lArticles:
			index = self.listCtrl.InsertStringItem(sys.maxint, text)
			self.listCtrl.SetStringItem(index, 1, author)
		self.listCtrl.Focus(0)
		self.listCtrl.Select(0)


	def NextPage(self):
		if not self.soup: return self.Play('beep.wav')
		currentPage = self.soup.find('strong', attrs={'class':'pg_current'})
		if currentPage is None: return self.Play('beep.wav')
		nextPage = currentPage.next.next.next.next.next
		if nextPage.name != 'a': return self.Play('beep.wav')
		href = nextPage['href']
		self.GetList(href)
		self.Display()
		self.Play('pageNext.wav')


	def PreviousPage(self):
		if not self.soup: return self.Play('beep.wav')
		currentPage = self.soup.find('strong', attrs={'class':'pg_current'})
		if currentPage is None or currentPage.getText() == '1': return self.Play('beep.wav')
		prevPage = currentPage.previous.previous.previous.previous.previous
		if prevPage.getText() != u'이전':
			prevPage = currentPage.previous.previous.previous.previous.previous.previous.previous
		href = prevPage['href']
		self.GetList(href)
		self.Display()
		self.Play('pagePrev.wav')


	def OpenArticle(self):
		index = self.listCtrl.GetFocusedItem()
		if index == -1: return self.Play('beep.wav')
		url = self.lArticles[index][2]
		viewDialog = ArticleView(self, url, self.cookie)
		viewDialog.ShowModal()



class ArticleView(wx.Dialog, Utility, Http):

	currentArticle = ''
	title = ''
	info = ''
	content = ''
	files = OrderedDict()
	comments = OrderedDict()
		
	def __init__(self, parent, url, cookie=''):
		Utility.__init__(self)
		wx.Dialog.__init__(self, parent, -1, '', wx.DefaultPosition, (500, 500))
		Http.__init__(self, 'han.kbuwel.or.kr', cookie=cookie)
		self.currentArticle = url
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.textCtrl = wx.TextCtrl(self, -1, '', (10, 10), (480, 330), wx.TE_MULTILINE | wx.TE_READONLY)
		self.textCtrl.Bind(wx.EVT_KEY_DOWN, self.OnTextCtrlKeyDown)

		# 댓글 표시창
		self.listCtrl = wx.ListCtrl(self, -1, wx.Point(10, 350), wx.Size(480, 140), wx.LC_REPORT | wx.LC_SINGLE_SEL)
		self.listCtrl.InsertColumn(0, u'댓글', width=480)
		self.listCtrl.Bind(wx.EVT_RIGHT_DOWN, self.OnListCtrlRightDown)
		self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.OnListCtrlKeyDown)

		self.GetInfo(url)
		self.Display()
		self.Play('pageNext.wav')


	def OnClose(self, e):
		self.Play('pagePrev.wav')
		self.Destroy()


	def OnTextCtrlKeyDown(self, e):
		key = e.GetKeyCode()
		if key == wx.WXK_ESCAPE or (e.GetModifiers() == wx.MOD_ALT and key == wx.WXK_LEFT):
			self.OnClose(e)
		else:
			e.Skip()



	def OnListCtrlRightDown(self, e):
		pass


	def OnListCtrlKeyDown(self, e):
		key = e.GetKeyCode()
		if key == wx.WXK_ESCAPE or (e.GetModifiers() == wx.MOD_ALT and key == wx.WXK_LEFT):
			self.OnClose(e)
		elif key == wx.WXK_DELETE:
			self.DeleteComment()
		elif key == ord('W'):
			self.WriteComment()

		else:
			e.Skip()



	def GetInfo(self, selector):
		self.Get(selector)
		self.title = self.soup.head.title.getText()
		# 글쓴이 등등 정보 추출
		infoSection = self.soup.find('section', id='bo_v_info')
		self.info = infoSection.getText()
		# 첨부파일 추출
		self.files.clear()
		fileLinks = self.soup('a', href=re.compile('^/download.php'))
		if fileLinks is not None:
			for link in fileLinks:
				self.files[link.strong.getText()] = link['href']
		# 본문 내용 추출
		div = self.soup.find('div', id='bo_v_con')
		self.content = div.getText()
		# 댓글 수집
		self.comments.clear()
		replies = self.soup('article', id=re.compile('^c_'))
		for reply in replies:
			name = reply.header.getText()
			body = reply.p.getText()
			# 수정, 삭제 링크가 있다면 추출하여 value로 저장. 없으면 빈 터플로 저장
			delete = ''
			if reply.footer.ul.li: 
				delete = reply.footer.ul.li.nextSibling.nextSibling.a['href']
			key = name + body
			key = re.sub(r'[\t ]+', ' ', key)
			self.comments[key] = delete


	def Display(self):
		self.textCtrl.Clear()
		self.listCtrl.DeleteAllItems()

		self.SetTitle(self.title)
		# 만약 첨부파일이 있다면 문자열로 정리
		fileList = ''
		if self.files:
			fileList = ''.join([u'\r\n<첨부파일:%s>' % filename for filename, url in self.files.items()])
		body = self.title + self.info + fileList + '\r\n' + self.content + u'\r\n게[시물의 끝입니다.]'
		body = body.replace('\t', ' ')
		self.textCtrl.SetValue(body)

		# 댓글 표시
		for reply in self.comments.keys():
			self.listCtrl.InsertStringItem(sys.maxint, reply)

	def DeleteComment(self):
		index = self.listCtrl.GetFocusedItem()
		if index == -1: return
		key = self.listCtrl.GetItemText(index)
		deleteUrl = self.comments[key]
		if not deleteUrl: return
		if not MsgBox(self, u'댓글 삭제', u'다음 댓글을 삭제할까요?\n' + key, True): return
		self.Get('/bbs' + deleteUrl[1:])
		if not '/board.php?' in self.response.getheader('Location'): return
		self.GetInfo(self.currentArticle)
		self.Display()
		self.Play('delete.wav')


	def WriteComment(self):
		selector = '/bbs/write_comment_update.php'
		paramDict = {}
		hiddens = self.soup('input', type='hidden')
		for tag in hiddens:
			paramDict[tag['name']] = tag['value']

		# 댓글 입력 대화상자
		content = ''
		mEditor = MultilineEditor(self, u'댓글 입력')
		if mEditor.ShowModal() == wx.ID_OK:
			content = mEditor.textCtrl.GetValue()
		mEditor.Destroy()
		if not content: return
		data = urllib.urlencode(paramDict, 'utf8')
		s = repr(content.encode('utf-8', 'ignore'))[1:-1].replace(r'\x', '%')
		data += '&wr_content=' + s
		self.Post(selector, data)
		self.Play('up.wav')
		self.GetInfo(self.currentArticle)
		self.Display()
		n = self.listCtrl.GetItemCount()
		if n == 0: return
		self.listCtrl.Focus(n-1)
		self.listCtrl.Select(n-1)
