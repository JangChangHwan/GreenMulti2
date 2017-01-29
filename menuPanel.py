# coding: utf-8

import wx
from util import *
from http import *
from bbsPanel import BBSPanel
from viewPanel import ViewPanel


class MenuPanel(wx.Panel, Utility, Http):

	currentMenu = 'top'

	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1, (0, 0), (500, 500))
		Utility.__init__(self)
		Http.__init__(self, parent)
		self.parent = parent

		self.listCtrl = wx.ListCtrl(self, -1, (10, 10), (500, 500), wx.LC_REPORT | wx.LC_SINGLE_SEL)
		self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.listCtrl.InsertColumn(0, u'게시판 메뉴', width=400)
		self.listCtrl.InsertColumn(1, u'Code', width=80)
		self.Display('top')


	def Display(self, menucode='top'):
		if not menucode in self.dTree: return
		self.parent.SetTitle(self.dTree[menucode][0] + ' - ' + self.parent.mainTitle)
		(title, mommy, submenu) = self.dTree[menucode]
		if submenu.startswith('/'):
			self.Hide()
			self.parent.bbs = BBSPanel(self.parent, submenu)
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

