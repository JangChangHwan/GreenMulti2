# coding: utf-8

import wx
import re
from http import *
from util import *
from viewPanel import ViewPanel
from writePanel import WritePanel
from mailWritePanel import MailWritePanel
import urllib



class BBSPanel(wx.Panel, Utility, Http):

	lArticles = []
	currentList = ''

	def __init__(self, parent, url):
		wx.Panel.__init__(self, parent, -1, (0, 0), (500, 500))
		Http.__init__(self, parent)
		Utility.__init__(self)
		self.parent = parent
		self.currentList = url

		self.listCtrl = wx.ListCtrl(self, -1, (10, 10), (480, 480), wx.LC_REPORT | wx.LC_SINGLE_SEL)
		self.listCtrl.InsertColumn(0, u'제목', width=400)
		self.listCtrl.InsertColumn(1, u'이름', width=80)
		self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.listCtrl.Bind(wx.EVT_RIGHT_DOWN, self.OnPopupMenu)

		self.BackTo = wx.Button(self, wx.ID_CANCEL, u'뒤로', (500, 500), (1,1))
		self.BackTo.Hide()
		self.BackTo.Bind(wx.EVT_BUTTON, self.BackToMenu)

		accel = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CANCEL), 
			(wx.ACCEL_NORMAL, wx.WXK_BACK, wx.ID_CANCEL), 
			(wx.ACCEL_ALT, wx.WXK_LEFT, wx.ID_CANCEL)
			])
		self.SetAcceleratorTable(accel)


		self.GetList(url)
		self.Display()
		self.listCtrl.SetFocus()
		self.parent.Play('pageNext.wav')


	def OnPopupMenu(self, e):
		self.result = ''
		menuList = [u'열기\tEnter',
			u'작성\t&W',
			u'다음 페이지로\tPageDown',
			u'이전 페이지로\tPageUp',
			u'다운로드\t&D',
			u'검색\tCtrl+F',
			u'초기화면\tCtrl+Home', 
			u'코드 바로가기\tCtrl+G',
			u'다운로드 폴더 열기\tCtrl+O',
			u'파일 전송 정보\tCtrl+J'
			]
		self.PopupMenu(MyMenu(self, menuList), e.GetPosition())
		if self.result == u'열기\tEnter':
			self.OpenArticle()
		elif self.result == u'작성\t&W':
			self.WriteArticle()
		elif self.result == u'다음 페이지로\tPageDown':
			self.NextPage()
		elif self.result == 			u'이전 페이지로\tPageUp':
			self.PreviousPage()
		elif self.result == u'다운로드\t&D':
			self.DownFile()
		elif self.result == u'검색\tCtrl+F':
			self.Searching()
		elif self.result == u'초기화면\tCtrl+Home':
			self.parent.OnHome(e)
		elif self.result == u'코드 바로가기\tCtrl+G':
			self.parent.OnGoTo(e)
		elif self.result == u'다운로드 폴더 열기\tCtrl+O':
			self.parent.OnOpenFolder(e)
		elif self.result == u'파일 전송 정보\tCtrl+J':
			self.parent.OnTransInfo(e)


	def KeyUpArrow(self):
		index = self.listCtrl.GetFocusedItem()
		if index <= 0:
			self.parent.Play('beep.wav')

	def KeyDownArrow(self):
		count = self.listCtrl.GetItemCount()
		index = self.listCtrl.GetFocusedItem()
		if index == count - 1:
			self.parent.Play('beep.wav')


	def OnKeyDown(self, e):
		key = e.GetKeyCode()
		if key == wx.WXK_F5:
			self.Refresh()
		elif key == wx.WXK_PAGEDOWN:
			self.NextPage()
		elif key == wx.WXK_PAGEUP:
			self.PreviousPage()
		elif key == wx.WXK_RETURN:
			self.OpenArticle()
		elif key == ord('D'):
			self.DownFile()
		elif key == ord('W'):
			self.WriteArticle()
		elif key == wx.WXK_UP:
			self.KeyUpArrow()
			e.Skip()
		elif key == wx.WXK_DOWN:
			self.KeyDownArrow()
			e.Skip()
		elif e.GetModifiers() == wx.MOD_CONTROL and key == ord('F'):
			self.Searching()

		else:
			e.Skip()


	def Refresh(self):
		index = self.listCtrl.GetFocusedItem()
		if index == -1: index = 0
		self.GetList(self.currentList)
		self.Display()
		self.listCtrl.Select(index)
		self.listCtrl.Select(index)
		self.parent.Play('refresh.wav')


	def WriteArticle(self):
		link = self.soup.find('a', href=re.compile(r'/bbs/write.php\?bo_table='))
		if link is None: return
		href = link['href']
		self.Hide()
		if 'write.php?bo_table=rmail' in href:
			self.parent.wmail = MailWritePanel(self.parent, href, before='bbs')
		else:
			self.parent.write = WritePanel(self.parent, href, before='bbs')





	def GetList(self, selector):
		self.lArticles = []
		self.Get(selector)
		if not self.soup: return

		tbody = self.soup.find('tbody')
		if tbody is None: return
		trs = tbody('tr')
		if trs is None or (len(trs) == 1 and trs[0].td['class'][0] == 'empty_table'): return

		for tr in trs:
			title = name = href = ''
			tdSubs = tr('td', attrs={'class': re.compile('td_subject')})
			title = tdSubs[0].a.getText()
			href = tdSubs[0].a['href']
			tdNames = tr('td', attrs={'class': re.compile('td_name')})
			if tdNames: name = tdNames[0].getText()
			self.lArticles.append((title, name, href))

		self.parent.CheckMailMemo(self.parent, self.soup)


	def Display(self):
		try:
			if not self.soup: return
			pageTitle = self.soup.head.title.string
		except:
			pageTitle = ''
		self.parent.sb.SetStatusText(pageTitle, 0)

		self.listCtrl.DeleteAllItems()
		for text, author, href in self.lArticles:
			index = self.listCtrl.InsertStringItem(sys.maxint, text)
			self.listCtrl.SetStringItem(index, 1, author)
		self.listCtrl.Focus(0)
		self.listCtrl.Select(0)


	def NextPage(self):
		if not self.soup: return self.parent.Play('beep.wav')

		# 다음 검색 링크가 있으면 곧바로 작동
		links = self.soup('a')
		for link in links:
			if link.getText() == u'다음검색':
				self.GetList(link['href'])
				self.Display()
				self.parent.Play('pageNext.wav')
				return

		currentPage = self.soup.find('strong', attrs={'class':'pg_current'})
		if currentPage is None: return self.parent.Play('beep.wav')
		nextPage = currentPage.next.next.next.next.next
		if nextPage.name != 'a': return self.parent.Play('beep.wav')
		href = nextPage['href']
		if href.startswith('./'): href = '/bbs' + href[1:]
		self.currentList = href
		self.GetList(href)
		self.Display()
		self.parent.Play('pageNext.wav')


	def PreviousPage(self):
		if not self.soup: return self.parent.Play('beep.wav')

		# 이전검색 링크가 있으면 곧바로 작동
		links = self.soup('a')
		for link in links:
			if link.getText() == u'이전검색':
				self.GetList(link['href'])
				self.Display()
				self.parent.Play('pageNext.wav')
				return

		currentPage = self.soup.find('strong', attrs={'class':'pg_current'})
		if currentPage is None or currentPage.getText() == '1': return self.parent.Play('beep.wav')
		prevPage = currentPage.previous.previous.previous.previous.previous
		if prevPage.getText() != u'이전':
			prevPage = currentPage.previous.previous.previous.previous.previous.previous.previous
		href = prevPage['href']
		if href.startswith('./'): href = '/bbs' + href[1:]
		self.currentList = href
		self.GetList(href)
		self.Display()
		self.parent.Play('pagePrev.wav')


	def OpenArticle(self):
		index = self.listCtrl.GetFocusedItem()
		if index == -1: return self.parent.Play('beep.wav')
		self.Hide()
		url = self.lArticles[index][2]
		self.parent.view = ViewPanel(self.parent, url)


	def BackToMenu(self, e):
		self.parent.menu.Show()
		self.parent.menu.SetFocus()
		self.parent.Play('pagePrev.wav')
		self.Destroy()


	def Searching(self):
		searchDialog = Search(self)
		if searchDialog.ShowModal() == wx.ID_OK: 
			sfl = searchDialog.sfl[searchDialog.choice.GetStringSelection()]
			stx = searchDialog.textCtrl.GetValue()
			searchDialog.Destroy()			
			if not stx: return
			stx = stx.encode('utf-8', 'ignore')

			form = self.soup.find('form', attrs={'name': 'fsearch'})
			if form is None: return
			hiddens = form('input', type='hidden')
			if hiddens is None: return
			d = {}
			for h in hiddens:
				d[h['name']] = h['value']
			d['sfl'] = sfl
			d['stx'] = stx
			params = urllib.urlencode(d)
			self.GetList('/bbs/board.php?' + params)
			self.Display()
			self.parent.Play('search.wav')

		searchDialog.Destroy()			


	def DownFile(self):
		index = self.listCtrl.GetFocusedItem()
		if index == -1: return self.parent.Play('beep.wav')

		if len(self.parent.dFileInfo) >= self.parent.limit: return MsgBox(self, u'알림', u'동시에 전송할 수 있는 파일이 수는 %s개입니다.\n전송을 취소하거나 전송을 마칠 때까지 기다려 주세요.' % self.parent.limit)

		url = self.lArticles[index][2]
		down = DownloadFromList(self.parent, url)


