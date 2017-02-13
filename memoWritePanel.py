# coding: utf-8

import wx
import re
from http import *
from util import *
from collections import OrderedDict


class MemoWritePanel(wx.Panel, Http):

	dInfo = OrderedDict()
	before = ''

	def __init__(self, parent, url, before='mview'):
		Http.__init__(self, parent)
		wx.Panel.__init__(self, parent, -1, (0 ,0), (500, 500))
		self.parent = parent
		self.before = before
		self.url = url

		wx.StaticText(self, -1, u'받는사람', (10, 10), (100, 20))
		self.receiver = wx.TextCtrl(self, -1, '', (120, 10), (370, 20))

		wx.StaticText(self, -1, u'본문', (10, 40), (100, 20))
		self.textCtrl = wx.TextCtrl(self, -1, '', (120, 40), (370, 420), wx.TE_MULTILINE)

		self.buttonOK = wx.Button(self, wx.ID_OK, u'저장(&S)', (280, 470), (100, 20))
		self.buttonOK.Bind(wx.EVT_BUTTON, self.OnButtonOK)
		self.buttonCancel = wx.Button(self, wx.ID_CANCEL, u'취소(&N)', (390, 470), (100, 20))
		self.buttonCancel.Bind(wx.EVT_BUTTON, self.OnCancel)

		self.receiver.SetFocus()

		# 단축키 지정
		accel = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CANCEL), (wx.ACCEL_ALT, wx.WXK_LEFT, wx.ID_CANCEL)])
		self.SetAcceleratorTable(accel)

		self.GetInfo(self.url)


	def GetInfo(self, url):
		self.Get(self.Url(url))		
		self.parent.sb.SetStatusText(self.soup.head.title.string, 0)
		recv = self.soup.find('input', id='me_recv_mb_id')
		self.receiver.SetValue(recv['value'])
		text = self.soup.find('textarea', id='me_memo')
		self.textCtrl.SetValue(text.getText())


	def OnCancel(self, e):
		if self.before == 'mview':
			self.parent.mview.Show()
			self.parent.mview.SetFocus()
			self.parent.mview.Play('pagePrev.wav')

		elif self.before == 'mlist':
			self.parent.mlist.Show()
			self.parent.mlist.SetFocus()
			self.parent.mlist.Play('pagePrev.wav')

		elif self.before == 'menu':
			self.parent.menu.Show()
			self.parent.menu.SetFocus()
			self.parent.menu.Play('pagePrev.wav')

		self.Destroy()


	def OnButtonOK(self, e): 
		receiver = 		self.receiver.GetValue()
		self.dInfo['me_recv_mb_id'] = receiver
		body = self.textCtrl.GetValue()
		self.dInfo['me_memo'] = body

		if not receiver or not body: 
			return MsgBox(self, u'오류', u'받는사람, 본문은 필수입력사항입니다.')

		self.Post('/plugin/ar.memo/memo_form_update.php', self.dInfo)
		self.parent.menu.Play('up.wav')

		if self.before == 'mview':
			self.parent.mview.Show()
			self.parent.mview.SetFocus()

		elif self.before == 'mlist': 
			self.parent.mlist.GetList(self.parent.mlist.url)
			self.parent.mlist.Display()
			self.parent.mlist.Show()
			self.parent.mlist.listCtrl.SetFocus()

		elif self.before == 'menu':
			self.parent.menu.Show()
			self.parent.menu.listCtrl.SetFocus()

		self.Destroy()

