# coding: utf-8

import wx
import re
from http import *
from util import *
from collections import OrderedDict


class WritePanel(wx.Panel, Http):

	dInfo = OrderedDict()
	before = ''

	def __init__(self, parent, url, before='view'):
		Http.__init__(self, parent)
		wx.Panel.__init__(self, parent, -1, (0, 0), (500, 500))
		self.parent = parent
		self.before = before

		wx.StaticText(self, -1, u'제목', (10, 10), (100, 20))
		self.textCtrl1 = wx.TextCtrl(self, -1, '', (120, 10), (370, 20))

		wx.StaticText(self, -1, u'본문', (10, 40), (100, 20))
		self.textCtrl2 = wx.TextCtrl(self, -1, '', (120, 40), (370, 420), wx.TE_MULTILINE)

		self.btnFile = wx.Button(self, -1, u'첨부파일', (10, 470), (100, 20))
		self.btnFile.Bind(wx.EVT_BUTTON, self.OnButtonFile)
		self.path = wx.TextCtrl(self, -1, '', (120, 470), (150, 20), wx.TE_READONLY)

		self.buttonOK = wx.Button(self, wx.ID_OK, u'저장(&S)', (280, 470), (100, 20))
		self.buttonOK.Bind(wx.EVT_BUTTON, self.OnButtonOK)
		self.buttonCancel = wx.Button(self, wx.ID_CANCEL, u'취소(&N)', (390, 470), (100, 20))
		self.buttonCancel.Bind(wx.EVT_BUTTON, self.OnCancel)

		self.GetInfo(url)
		self.textCtrl1.SetFocus()
		# 단축키 지정
		accel = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CANCEL), (wx.ACCEL_ALT, wx.WXK_LEFT, wx.ID_CANCEL)])
		self.SetAcceleratorTable(accel)
		

	def OnCancel(self, e):
		if self.before == 'view':
			self.parent.view.Show()
			self.parent.view.SetFocus()
			self.parent.view.Play('pagePrev.wav')
		elif self.before == 'bbs':
			self.parent.bbs.Show()
			self.parent.bbs.SetFocus()
			self.parent.bbs.Play('pagePrev.wav')
		self.Destroy()


	def GetInfo(self, url):
		self.Get(url)
		self.parent.sb.SetStatusText(self.soup.head.title.string, 0)
		self.dInfo.clear()
		# hidden 속성을 dInfo 사전에 저장한다.
		form = self.soup.find('form', id='fwrite')
		hiddens = form('input', type='hidden')
		for h in hiddens:
			self.dInfo[h['name']] = h['value']
		# 제목 추가
		title = self.soup.find('input', type='text')
		self.dInfo[title['name']] = title['value']
		self.textCtrl1.SetValue(title['value'])
		# 본문 추가
		body = self.soup.find('textarea')
		self.dInfo[body['name']] = body.getText()
		self.textCtrl2.SetValue(body.getText())


	def OnButtonFile(self, e):
		if self.path.GetValue():
			self.path.SetValue('')
			MsgBox(self, u'알림', u'첨부파일 추가를 취소합니다.')
			return

		fileDialog = wx.FileDialog(self, u'파일 선택', '', '*.*', 'All Files (*.*)|*.*', wx.FD_OPEN | wx.FD_CHANGE_DIR)
		if fileDialog.ShowModal() == wx.ID_OK:
			path = fileDialog.GetPath()
			self.path.SetValue(path)
		fileDialog.Destroy()


	def OnButtonOK(self, e): 
		title = self.textCtrl1.GetValue()
		self.dInfo['wr_subject'] = title
		body = self.textCtrl2.GetValue()
		self.dInfo['wr_content'] = body
		path = self.path.GetValue()

		if not title or not body: 
			return MsgBox(self, u'오류', u'제목과 본문은 필수입력사항입니다.')

		# 첨부파일이 없다면 post로 보내고 있으면 multipartPost로 보낸다.
		if path and os.path.exists(path):
			p = Process(target=Upload, args=('/bbs/write_update.php', self.dInfo, {'bf_file[]': path}, self.parent.transQueue))
			p.start()
			self.parent.dProcess[(os.path.basename(path), 'upload')] = p

		else:
			self.Post('/bbs/write_update.php', self.dInfo)
			url = self.response.getheader('Location')
			self.parent.bbs.GetList(self.Url(url))
			self.parent.bbs.Display()
			self.parent.bbs.Play('up.wav')

		self.parent.bbs.Show()
		self.parent.bbs.listCtrl.SetFocus()
		if self.before == 'view': self.parent.ClosePanels(['view'])
		self.Destroy()


