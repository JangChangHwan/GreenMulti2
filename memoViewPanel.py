# coding: utf-8

import wx
import re
from http import *
from util import *
from memoWritePanel import MemoWritePanel


class MemoViewPanel(wx.Panel, Utility, Http):

	content = ''
	
	def __init__(self, parent, url):
		wx.Panel.__init__(self, parent, -1, (0, 0), (500, 500))
		Http.__init__(self, parent)
		Utility.__init__(self)

		self.parent = parent
		self.url = url
		self.textCtrl = wx.TextCtrl(self, -1, '', (10, 10), (480, 480), wx.TE_MULTILINE | wx.TE_READONLY)
		self.textCtrl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.textCtrl.Bind(wx.EVT_RIGHT_DOWN, self.OnPopupMenu)

		# 알트 다음글 넘어가는 키: 페이지다운
		idAltPgDn = wx.NewId()
		self.AltPgDn = wx.Button(self, idAltPgDn, u'다음글', (500, 500), (1,1))
		self.AltPgDn.Hide()
		self.AltPgDn.Bind(wx.EVT_BUTTON, self.OnNextMemo)

		# 알트 페이지업 이전글 넘어가는 키: 
		idAltPgUp = wx.NewId()
		self.AltPgUp = wx.Button(self, idAltPgUp, u'이전글', (500, 500), (1,1))
		self.AltPgUp.Hide()
		self.AltPgUp.Bind(wx.EVT_BUTTON, self.OnPrevMemo)

		self.BackTo = wx.Button(self, wx.ID_CANCEL, u'뒤로', (500, 500), (1,1))
		self.BackTo.Hide()
		self.BackTo.Bind(wx.EVT_BUTTON, self.BackToMemoList)

		accel = wx.AcceleratorTable([(wx.ACCEL_ALT, wx.WXK_PAGEDOWN, idAltPgDn),
			(wx.ACCEL_ALT, wx.WXK_PAGEUP, idAltPgUp),
			(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CANCEL), 
			(wx.ACCEL_NORMAL, wx.WXK_BACK, wx.ID_CANCEL), 
			(wx.ACCEL_ALT, wx.WXK_LEFT, wx.ID_CANCEL)
			])

		self.SetAcceleratorTable(accel)
	

		self.GetInfo(url)
		self.Display()
		self.textCtrl.SetFocus()
		self.Play('pageNext.wav')


	def OnKeyDown(self, e):
		key = e.GetKeyCode()
		if key == ord('W'):
			self.WriteMemo()
		elif key == ord('R'):
			self.ReplyMemo()
		elif key == wx.WXK_DELETE:
			self.DeleteMemo()

		else:
			e.Skip()


	def GetInfo(self, selector):
		self.Get(selector)

		# 쪽지 내용 추출
		article = self.soup.find('article', id='memo_view_contents')
		self.content = self.GetTextFromTag(article)
		self.content = self.Date(self.content)


	def Display(self):
		self.parent.sb.SetStatusText(self.soup.head.title.string, 0)
		self.textCtrl.Clear()
		self.textCtrl.SetValue(self.content)


	def DeleteMemo(self):
		deleteUrl = self.soup.find('a', href=re.compile('memo_delete.php'))
		href = deleteUrl['href']
		if MsgBox(self, u'삭제 경고', u'이 쪽지를 삭제할까요?', True):
			href = 'http://web.kbuwel.or.kr/plugin/ar.memo' + href[1:]
			self.Get(href)
			self.parent.mlist.GetList(self.parent.mlist.url)
			self.parent.mlist.Display()
			self.parent.mlist.Show()
			self.parent.mlist.listCtrl.SetFocus()
			self.parent.mlist.Play('delete.wav')
			self.Destroy()


	def WriteMemo(self):
		self.Hide()
		href = 'http://web.kbuwel.or.kr/plugin/ar.memo/memo_form.php'
		self.parent.wmemo = MemoWritePanel(self.parent, href, before='mview')


	def ReplyMemo(self):
		links = self.soup('a')

		href = ''
		for link in links:
			if link.getText() == u'답장': 
				href = link['href']
				break

		if not href: return
		href = 'http://web.kbuwel.or.kr/plugin/ar.memo' + href[1:]
		self.Hide()
		self.parent.wmemo = MemoWritePanel(self.parent, href, before='mview')


	def BackToMemoList(self, e):
		self.parent.mlist.Show()
		self.parent.mlist.SetFocus()
		self.parent.mlist.Play('pagePrev.wav')
		self.Destroy()



	def OnNextMemo(self, e):
		links = self.soup('a')
		if links is None: return
		url = ''
		for link in links:
			if link.getText() == u'다음쪽지':
				url = link['href']
				break

		if not url: return self.Play('beep.wav')

		self.GetInfo(url)
		self.Display()
		self.textCtrl.SetFocus()
		self.Play('pageNext.wav')



	def OnPrevMemo(self, e):
		links = self.soup('a')
		if links is None: return
		url = ''
		for link in links:
			if link.getText() == u'이전쪽지':
				url = link['href']
				break

		if not url: return self.Play('beep.wav')

		self.GetInfo(url)
		self.Display()
		self.textCtrl.SetFocus()
		self.Play('pagePrev.wav')


	def OnPopupMenu(self, e):
		self.result = ''
		menuList = [u'뒤로\tESC', 
			u'작성\t&W', 
			u'답장\t&R',
			u'삭제\tDelete', 
			u'다음 쪽지\tAlt+PageDown',
			u'이전 쪽지\tAlt+PageUp',
			u'초기화면\tCtrl+Home', 
			u'코드 바로가기\tCtrl+G',
			u'다운로드 폴더 열기\tCtrl+O',
			u'파일 전송 정보\tCtrl+J'
			]
		self.PopupMenu(MyMenu(self, menuList), e.GetPosition())

		if self.result == u'뒤로\tESC':
			self.BackToMemoList() 
		elif self.result == u'작성\t&W':
			self.WriteMemo()
		elif self.result == u'답장\t&R':
			self.ReplyMemo()
		elif self.result == u'삭제\tDelete':
			self.DeleteMemo()
		elif self.result == u'다음 쪽지\tAlt+PageDown':
			self.OnNextMemo(e)
		elif self.result == u'이전 쪽지\tAlt+PageUp':
			self.OnPrevMemo(e)
		elif self.result == u'초기화면\tCtrl+Home':
			self.parent.OnHome(e)
		elif self.result == u'코드 바로가기\tCtrl+G':
			self.parent.OnGoTo(e)
		elif self.result == u'다운로드 폴더 열기\tCtrl+O':
			self.parent.OnOpenFolder(e)
		elif self.result == u'파일 전송 정보\tCtrl+J':
			self.parent.OnTransInfo(e)
