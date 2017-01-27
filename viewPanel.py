﻿# coding: utf-8

import wx
import re
from http import *
from util import *
from collections import OrderedDict
from writePanel import WritePanel
from multiprocessing import Process, Queue


class ViewPanel(wx.Panel, Utility, Http):

	currentArticle = ''
	title = ''
	info = ''
	content = ''
	files = OrderedDict()
	comments = OrderedDict()
		
	def __init__(self, parent, url):
		wx.Panel.__init__(self, parent, -1, (0, 0), (500, 500))
		Http.__init__(self, parent)
		Utility.__init__(self)

		self.parent = parent

		self.textCtrl1 = wx.TextCtrl(self, -1, '', (10, 10), (480, 280), wx.TE_MULTILINE | wx.TE_READONLY)
		self.textCtrl1.Bind(wx.EVT_KEY_DOWN, self.OnTextCtrl1KeyDown)

		# 댓글 표시창
		self.listCtrl = wx.ListCtrl(self, -1, wx.Point(10, 300), wx.Size(480, 140), wx.LC_REPORT | wx.LC_SINGLE_SEL)
		self.listCtrl.InsertColumn(0, u'댓글', width=480)
		self.listCtrl.Bind(wx.EVT_RIGHT_DOWN, self.OnListCtrlRightDown)
		self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.OnListCtrlKeyDown)

		wx.StaticText(self, -1, u'댓글', (10, 450), (40, 40))
		self.textCtrl2 = wx.TextCtrl(self, -1, '', (60, 450), (380, 40), wx.TE_MULTILINE)
		self.button = wx.Button(self, -1, u'저장', (350, 450), (40, 40))
		self.button.Bind(wx.EVT_BUTTON, self.OnButton)

		# ESC 키를 위한 더미
		self.Cancel = wx.Button(self, wx.ID_CANCEL, u'닫기', (500, 500), (1,1))
		self.Cancel.Hide()
		self.Cancel.Bind(wx.EVT_BUTTON, self.BackToBBS)

		# 알트 다음글 넘어가는 키: 페이지다운
		idAltPgDn = wx.NewId()
		self.AltPgDn = wx.Button(self, idAltPgDn, u'다음글', (500, 500), (1,1))
		self.AltPgDn.Hide()
		self.AltPgDn.Bind(wx.EVT_BUTTON, self.OnNextArticle)



		self.GetInfo(url)
		self.Display()
		self.textCtrl1.SetFocus()
		self.Play('pageNext.wav')

		accel = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CANCEL), 
			(wx.ACCEL_ALT, wx.WXK_LEFT, wx.ID_CANCEL), 
			(wx.ACCEL_ALT, wx.WXK_PAGEDOWN, idAltPgDn)
			])

		self.SetAcceleratorTable(accel)
		


	def OnTextCtrl1KeyDown(self, e):
		key = e.GetKeyCode()
		if key == ord('W'):
			self.WriteArticle()
		elif key == ord('E'):
			self.EditArticle()
		elif key == wx.WXK_DELETE:
			self.DeleteArticle()
		elif key == ord('D'):
			self.OnDownFiles('')

		else:
			e.Skip()


	def OnListCtrlRightDown(self, e):
		pass


	def OnListCtrlKeyDown(self, e):
		key = e.GetKeyCode()
		if key == wx.WXK_DELETE:
			self.DeleteComment()

		else:
			e.Skip()


	def GetInfo(self, selector):
		self.currentArticle = url = selector
		self.Get(url)
		self.title = self.soup.head.title.getText()
		# 글쓴이 등등 정보 추출
		infoSection = self.soup.find('section', id='bo_v_info')
		self.info = infoSection.getText()
		# 첨부파일 추출
		self.files.clear()
		fileLinks = self.soup('a', href=re.compile('download.php'))
		if fileLinks is not None:
			for link in fileLinks:
				descript = ' '.join(link.getText().split())
				self.files[link.strong.getText()] = (descript, link['href'])
		# 본문 내용 추출
		div = self.soup.find('div', id='bo_v_con')
		self.content = self.GetTextFromTag(div)
		
		# 댓글 수집
		self.comments.clear()
		replies = self.soup('article', id=re.compile('^c_'))
		for reply in replies:
			name = reply.header.getText()
			body = self.GetTextFromTag(reply.p)

			# 수정, 삭제 링크가 있다면 추출하여 value로 저장. 없으면 빈 터플로 저장
			delete = ''
			if reply.footer.ul.li: 
				delete = reply.footer.ul.li.nextSibling.nextSibling.a['href']
			key = name + body
			key = re.sub(r'[\t ]+', ' ', key)
			self.comments[key] = delete


	def Display(self):
		self.textCtrl1.Clear()
		self.listCtrl.DeleteAllItems()

		# 만약 첨부파일이 있다면 문자열로 정리
		fileList = ''
		if self.files:
			fileList = ''.join([u'\r\n첨부파일:%s' % descript for filename, (descript, url) in self.files.items()])
		body = self.title + self.info + fileList + '\r\n' + self.content + u'\r\n게[시물의 끝입니다.]'
		body = body.replace('\t', ' ')
		self.textCtrl1.SetValue(body)

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
		self.Get(deleteUrl)
		self.GetInfo(self.currentArticle)
		self.Display()
		self.Play('delete.wav')


	def OnButton(self, e):
		form = self.soup.find('form', attrs={'name': 'fviewcomment'})
		if form is None: return
		selector = form['action']

		paramDict = {}
		hiddens = self.soup('input', type='hidden')
		if hiddens is None: return

		for tag in hiddens:
			try:
				paramDict[tag['name']] = tag['value']
			except:
				pass

		content = self.textCtrl2.GetValue()
		if not content: return MsgBox(self, u'오류', u'댓글 편집창이 비어 있습니다.')
		paramDict['wr_content'] = content.encode('utf-8')
		self.Post(selector, paramDict)
		if self.response.getheader('Location'):
			self.textCtrl2.Clear()
			self.Play('up.wav')
			self.GetInfo(self.currentArticle)
			self.Display()
			n = self.listCtrl.GetItemCount()
			if n == 0: return
			self.listCtrl.Focus(n-1)
			self.listCtrl.Select(n-1)
			self.listCtrl.SetFocus()
		else:
			self.GetInfo(self.currentArticle)
			MsgBox(self, u'경고', u'댓글을 올리는 속도가 너무 빠릅니다. 잠시 후에 다시 실행해 주세요.')
			self.textCtrl2.SetFocus()



	def DeleteArticle(self):
		deleteUrl = self.soup.find('a', href=re.compile('/bbs/delete.php?'))
		if deleteUrl is None: return
		href = deleteUrl['href']
		if MsgBox(self, u'삭제 경고', u'이 게시물을 삭제할까요?', True):
			self.Get(href)
			url =  self.response.getheader('Location')
			self.parent.bbs.GetList(url)
			self.parent.bbs.Display()
			self.parent.bbs.Show()
			self.parent.bbs.listCtrl.SetFocus()
			self.parent.bbs.Play('delete.wav')
			self.Destroy()


	def WriteArticle(self):
		link = self.soup.find('a', href=re.compile(r'/bbs/write.php\?bo_table='))
		if link is None: return
		href = link['href']
		self.Hide()
		self.parent.write = WritePanel(self.parent, href, before='view')


	def EditArticle(self):
		link = self.soup.find('a', href=re.compile(r'/bbs/write.php\?w=u'))
		if link is None: return
		href = link['href']
		self.Hide()
		self.parent.write = WritePanel(self.parent, href, before='view')


	def BackToBBS(self, e):
		self.parent.bbs.Show()
		self.parent.bbs.SetFocus()
		self.parent.bbs.Play('pagePrev.wav')
		self.Destroy()


	def OnNextArticle(self, e):
		links = self.soup('a')
		if links is None: return
		url = ''
		for link in links:
			if link.getText() == u'다음글':
				url = link['href']
				break

		if not url: return
		print url
		self.GetInfo(url)
		self.Display()
		self.textCtrl1.SetFocus()
		self.Play('pageNext.wav')


	def OnDownFiles(self, e):
		if not self.files: return
		downloadFolder = self.ReadReg('downloadfolder')
		if not downloadFolder : downloadFolder = 'c:\\'
		for fileName, (descript, url) in self.files.items():
			filePath = os.path.join(downloadFolder, fileName)
			p = Process(target=Download, args=(filePath, url, self.parent.transQueue))
			p.start()
