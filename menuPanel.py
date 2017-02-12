# coding: utf-8

import wx
from util import *
from http import *
from bbsPanel import BBSPanel
from viewPanel import ViewPanel
from mailWritePanel import MailWritePanel
from memoListPanel import MemoListPanel
from memoWritePanel import MemoWritePanel


class MenuPanel(wx.Panel, Utility, Http):

	currentMenu = 'top'

	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1, (0, 0), (500, 500))
		Utility.__init__(self)
		Http.__init__(self, parent)
		self.parent = parent

		self.listCtrl = wx.ListCtrl(self, -1, (10, 10), (500, 500), wx.LC_REPORT | wx.LC_SINGLE_SEL)
		self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.listCtrl.Bind(wx.EVT_RIGHT_DOWN, self.OnPopupMenu)
		self.listCtrl.InsertColumn(0, u'게시판 메뉴', width=400)
		self.listCtrl.InsertColumn(1, u'Code', width=80)

		self.Display('top')


	def Display(self, menucode='top'):
		if not menucode in self.dTree: return

		(title, mommy, submenu) = self.dTree[menucode]
		if 'write.php?bo_table=rmail' in submenu:
			self.Hide()
			self.parent.wmail = MailWritePanel(self.parent, submenu, before='menu')
			return False

		elif '/memo.php' in submenu:
			self.Hide()
			self.parent.mlist = MemoListPanel(self.parent, submenu)
			return False

		elif 'memo_form.php' in submenu:
			self.parent.wmemo = MemoWritePanel(self.parent, submenu, before='menu')
			return False

		elif submenu.startswith('/'):
			self.Hide()
			self.parent.bbs = BBSPanel(self.parent, submenu)
			return False

		self.parent.sb.SetStatusText(title, 0)
		self.currentMenu = menucode
		self.listCtrl.DeleteAllItems()
		for c in submenu.split('|'):
			if not c in self.dTree: continue
			(name, mother, sub) = self.dTree[c]
			index = self.listCtrl.InsertStringItem(sys.maxint, name)
			self.listCtrl.SetStringItem(index, 1, c)
		self.listCtrl.Focus(0)
		self.listCtrl.Select(0)
		self.Show()
		self.listCtrl.SetFocus()
		return True


	def OnKeyDown(self, e):
		key = e.GetKeyCode()
		if key == wx.WXK_RETURN:
			self.KeyReturn()
		elif key == wx.WXK_ESCAPE or key == wx.WXK_BACK: 
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


	def OnPopupMenu(self, e):
		self.result = ''
		menuList = [u'열기\tEnter',
			u'뒤로\tESC', 
			u'초기화면\tCtrl+Home', 
			u'코드 바로가기\tCtrl+G',
			u'다운로드 폴더 열기\tCtrl+O',
		u'파일 전송 정보\tCtrl+J'
			]
		self.PopupMenu(MyMenu(self, menuList), e.GetPosition())
		if self.result == u'열기\tEnter':
			self.KeyReturn()
		elif self.result == u'뒤로\tESC':
			self.KeyEscape()
		elif self.result == u'초기화면\tCtrl+Home':
			self.parent.OnHome(e)
		elif self.result == u'코드 바로가기\tCtrl+G':
			self.parent.OnGoTo(e)
		elif self.result == u'다운로드 폴더 열기\tCtrl+O':
			self.parent.OnOpenFolder(e)
		elif self.result == u'파일 전송 정보\tCtrl+J':
			self.parent.OnTransInfo(e)


