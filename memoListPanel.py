# coding: utf-8

import wx
import re
from http import *
from util import *
from memoViewPanel import MemoViewPanel
from memoWritePanel import MemoWritePanel
import urllib



class MemoListPanel(wx.Panel, Utility, Http):

	lArticles = []
	currentList = ''

	def __init__(self, parent, url):
		wx.Panel.__init__(self, parent, -1, (0, 0), (500, 500))
		Http.__init__(self, parent)
		Utility.__init__(self)
		self.parent = parent
		self.currentList = url

		self.listCtrl = wx.ListCtrl(self, -1, (10, 10), (480, 480), wx.LC_REPORT | wx.LC_SINGLE_SEL)
		self.listCtrl.InsertColumn(0, u'상태', width=80)
		self.listCtrl.InsertColumn(1, u'이름', width=100)
		self.listCtrl.InsertColumn(2, u'제목', width=300)
		self.listCtrl.Bind(wx.EVT_RIGHT_DOWN, self.OnPopupMenu)
		self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

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
		if key == wx.WXK_RETURN:
			self.OpenMemo()
		elif key == ord('W'):
			self.WriteMemo()
		elif key == wx.WXK_UP:
			self.KeyUpArrow()
			e.Skip()
		elif key == wx.WXK_DOWN:
			self.KeyDownArrow()
			e.Skip()
		if key == wx.WXK_F5:
			self.Refresh()

		else:
			e.Skip()



	def WriteMemo(self):
		self.Hide()
		href = 'http://web.kbuwel.or.kr/plugin/ar.memo/memo_form.php'
		self.parent.wmemo = MemoWritePanel(self.parent, href, before='mlist')


	def GetList(self, selector):
		self.currentList = selector
		self.lArticles = []
		self.Get(selector)
		self.currentPage = selector

		trs = self.soup.find('tbody')('tr')
		if len(trs) == 1 and trs[0].td['class'][0] == 'empty_table': return

		for tr in trs:
			title = name = href = state = ''
			tds = tr('td')
			name = tds[0].getText()
			title = tds[1].a.getText()
			href = tds[1].a['href']
			state = tds[3].getText()
			state = self.Date(state)
			self.lArticles.append((state, name, title, href))


	def Display(self):
		self.parent.sb.SetStatusText(self.soup.head.title.string, 0)
		self.listCtrl.DeleteAllItems()
		for state, author, text, href in self.lArticles:
			index = self.listCtrl.InsertStringItem(sys.maxint, state)
			self.listCtrl.SetStringItem(index, 1, author)
			self.listCtrl.SetStringItem(index, 2, text)
		self.listCtrl.Focus(0)
		self.listCtrl.Select(0)



	def OpenMemo(self):
		index = self.listCtrl.GetFocusedItem()
		if index == -1: return self.parent.Play('beep.wav')
		self.Hide()
		url = self.lArticles[index][3]
		self.parent.mview = MemoViewPanel(self.parent, url)


	def BackToMenu(self, e):
		self.parent.menu.Show()
		self.parent.menu.SetFocus()
		self.parent.menu.Play('pagePrev.wav')
		self.Destroy()

	def OnPopupMenu(self, e):
		self.result = ''
		menuList = [u'열기\tEnter',
			u'뒤로\tESC', 
			u'작성\t&W',
			u'초기화면\tCtrl+Home', 
			u'코드 바로가기\tCtrl+G',
			u'다운로드 폴더 열기\tCtrl+O',
			u'파일 전송 정보\tCtrl+J'
			]
		self.PopupMenu(MyMenu(self, menuList), e.GetPosition())

		if self.result == u'열기\tEnter':
			self.OpenMemo()
		elif self.result == u'뒤로\tESC':
			self.BackToMenu()
		elif self.result == u'작성\t&W':
			self.WriteMemo()
		elif self.result == u'초기화면\tCtrl+Home':
			self.parent.OnHome(e)
		elif self.result == u'코드 바로가기\tCtrl+G':
			self.parent.OnGoTo(e)
		elif self.result == u'다운로드 폴더 열기\tCtrl+O':
			self.parent.OnOpenFolder(e)
		elif self.result == u'파일 전송 정보\tCtrl+J':
			self.parent.OnTransInfo(e)


	def Refresh(self):
		index = self.listCtrl.GetFocusedItem()
		if index == -1: index = 0
		self.GetList(self.currentList)
		self.Display()
		self.listCtrl.Select(index)
		self.listCtrl.Select(index)
		self.parent.Play('refresh.wav')
