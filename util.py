# coding: utf-8
# 함수모음 util.py

import sys
import winsound
import os
import _winreg
import wx
from collections import OrderedDict
import time
import re

class Utility(object):
	def __init__(self):
		self.key = "%x" % os.path.getctime(os.environ["APPDATA"])

	def Play(self, wavfile, async=True):
		try:
			if async:
				winsound.PlaySound(os.path.dirname(sys.argv[0]) + "\\sound\\" + wavfile, winsound.SND_ASYNC)
			else:
				winsound.PlaySound(os.path.dirname(sys.argv[0]) + "\\sound\\" + wavfile, winsound.SND_NOSTOP)
		except:
			pass

	def WriteReg(self, key, value):
		try:
			root_key = _winreg.HKEY_CLASSES_ROOT
			sub_key = _winreg.CreateKey(root_key, r'SOFTWARE\JangSoft')
			_winreg.SetValueEx(sub_key, key, 0, _winreg.REG_SZ, value)
			return True
		except:
			return False


	def ReadReg(self, key):
		try:
			root_key = _winreg.HKEY_CLASSES_ROOT
			sub_key = _winreg.CreateKey(root_key, r'SOFTWARE\JangSoft')
			r = _winreg.QueryValueEx(sub_key, key)
			return r[0]
		except:
			return ""


	def Encrypt(self, s):
		if len(s) < 3: return ''
		try:
			r = ''
			i = 0
			for c in s:
				i = i % len(self.key)
				n = ord(c) + ord(self.key[i])
				r += chr(n) if n <= 126 else chr(n - 95)
				i += 1
			return r
		except:
			return ''


	def Decrypt(self, s):
		try:
			r = ''
			i = 0
			for c in s:
				i = i % len(self.key)
				n= ord(c) - ord(self.key[i])
				r += chr(n) if n >= 32 else chr(n + 95)
				i += 1
			return r
		except:
			return ''

	def Date(self, s):
		# 년-월-일 시:분 --> x월 x일 x시 x분으로 변경
		s = re.sub(r'(\d\d)-(\d\d)-(\d\d) (\d\d):(\d\d)', u' \\2월 \\3일 \\4시 \\5분', s)
		# 01 02 03 등을 1, 2, 3으로 변경
		s = re.sub(r'\b(0)(\d)', r'\2', s)
		return s


def InputBox(parent, title, text, pwd=False):
	try:
		style = wx.OK | wx.CANCEL | wx.TE_PASSWORD if pwd else wx.OK | wx.CANCEL
		entry = wx.TextEntryDialog(parent, text, title, '', style)
		if entry.ShowModal() == wx.ID_OK: 
			return entry.GetValue()
		entry.Destroy()
	except:
		return False


def MsgBox(parent, title, text, question=False):
	try:
		if question:
			d = wx.MessageDialog(parent, text, title, wx.OK | wx.CANCEL)
			if d.ShowModal() == wx.ID_OK:
				return True
			else:
				return False
			d.Destroy()
		else:
			d = wx.MessageDialog(parent, text, title, wx.OK)
			d.ShowModal()
			d.Destroy()
	except:
		pass

class TreeInput(wx.Dialog):
	def __init__(self, parent, code='', name='', mother='', sub=''):
		wx.Dialog.__init__(self, parent, -1, u'메뉴/게시판 정보 입력', wx.DefaultPosition, wx.Size(340, 160))

		wx.StaticText(self, -1, u'바로가기 코드', (10, 10), (100, 20))
		self.code = wx.TextCtrl(self, -1, code, (120, 10), (210, 20))
		wx.StaticText(self, -1, u'이름', (10, 40), (100, 20))
		self.name = wx.TextCtrl(self, -1, name, (120, 40), (210, 20))
		wx.StaticText(self, -1, u'상위메뉴', (10, 70), (100, 20))
		self.mother = wx.TextCtrl(self, -1, mother, (120, 70), (210, 20))
		wx.StaticText(self, -1, u'하위메뉴/주소', (10, 100), (100, 20))
		self.sub = wx.TextCtrl(self, -1, sub, (120, 100), (210, 20))

		self.btnOK = wx.Button(self, wx.ID_OK, u'확인', (120, 130), (100, 20))
		self.btnCancel = wx.Button(self, wx.ID_CANCEL, u'취소', (230, 130), (100, 20))





class MyMenu(wx.Menu):
	def __init__(self, parent, menuList):
		wx.Menu.__init__(self)
		self.parent = parent

		self.ids = {}
		for m in menuList:
			id = wx.NewId()
			self.ids[id] = m
			mi = wx.MenuItem(self, id, m)
			self.AppendItem(mi)
			self.Bind(wx.EVT_MENU, self.OnResult, mi)

	def OnResult(self, e):
		self.parent.result = self.ids[e.GetId()]



class MenuManager(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, u'메뉴관리', wx.DefaultPosition, wx.Size(500, 500))
		self.parent = parent
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.listCtrl = wx.ListCtrl(self, -1, wx.Point(10, 10), wx.Size(480, 480), wx.LC_REPORT | wx.LC_SINGLE_SEL)
		self.listCtrl.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.listCtrl.InsertColumn(0, u'코드', width=120)
		self.listCtrl.InsertColumn(1, u'', width=120)
		self.listCtrl.InsertColumn(2, u'상위메뉴', width=120)
		self.listCtrl.InsertColumn(3, u'하위메뉴', width=120)

		self.Display()


	def OnClose(self, e):
		count = self.listCtrl.GetItemCount()
		if MsgBox(self, u'알림', u'메뉴 설정을 저장할까요?', True) and count:
			self.parent.dTree.clear()
			for index in range(count):
				code = self.listCtrl.GetItemText(index, 0)
				name = self.listCtrl.GetItemText(index, 1)
				mother = self.listCtrl.GetItemText(index, 2)
				sub = self.listCtrl.GetItemText(index, 3)
				self.parent.dTree[code] = (name, mother, sub)
			self.parent.SaveTreeMenu()
		self.Destroy()


	def OnRightDown(self, e):
		self.result = ''
		self.PopupMenu(MyMenu(self, [u'추가\t&A', u'수정\t&E', u'삭제\t&D', u'위로\t&I', u'아래로\t&K']), e.GetPosition())

		if self.result.startswith(u'추가'):
			self.Add()
		elif self.result.startswith(u'수정'):
			self.Edit()
		elif self.result.startswith(u'삭제'):
			self.Delete()
		elif self.result.startswith(u'위로'):
			self.Up()
		elif self.result.startswith(u'아래'):
			self.Down()

	def Up(self):
		index = self.listCtrl.GetFocusedItem()
		if index <= 0: return
		if self.listCtrl.GetItemCount() <= 1: return
		f = self.listCtrl.GetItemText
		code, name, mother, sub = f(index, 0), f(index, 1), f(index, 2), f(index, 3)
		g = self.listCtrl.SetStringItem
		target = index - 1
		self.listCtrl.SetItemText(index, f(target, 0))
		g(index, 1, f(target, 1))
		g(index, 2, f(target, 2))
		g(index, 3, f(target, 3))

		self.listCtrl.SetItemText(target, code)
		g(target, 1, name)
		g(target, 2, mother)
		g(target, 3, sub)


	def Down(self):
		index = self.listCtrl.GetFocusedItem()
		if index == -1: return
		if self.listCtrl.GetItemCount() <= 1: return
		if index + 1 == self.listCtrl.GetItemCount(): return

		f = self.listCtrl.GetItemText
		code, name, mother, sub = f(index, 0), f(index, 1), f(index, 2), f(index, 3)
		g = self.listCtrl.SetStringItem
		target = index + 1
		self.listCtrl.SetItemText(index, f(target, 0))
		g(index, 1, f(target, 1))
		g(index, 2, f(target, 2))
		g(index, 3, f(target, 3))

		self.listCtrl.SetItemText(target, code)
		g(target, 1, name)
		g(target, 2, mother)
		g(target, 3, sub)


	def Add(self):
		index = self.listCtrl.GetFocusedItem()
		if index == -1: 
			index = sys.maxint

		code = name = mother = sub = ''
		tinput = TreeInput(self) 
		if tinput.ShowModal() == wx.ID_OK:
			code, name, mother, sub = tinput.code.GetValue(), tinput.name.GetValue(), tinput.mother.GetValue(), tinput.sub.GetValue()
			tinput.Destroy()
		else:
			tinput.Destroy()
			return

		index = self.listCtrl.InsertStringItem(index, code)
		self.listCtrl.SetStringItem(index, 1, name)
		self.listCtrl.SetStringItem(index, 2, mother)
		self.listCtrl.SetStringItem(index, 3, sub)

	def Edit(self):
		index = self.listCtrl.GetFocusedItem()
		if index == -1: return
		code = self.listCtrl.GetItemText(index)
		name = self.listCtrl.GetItemText(index, 1)
		mother = self.listCtrl.GetItemText(index, 2)
		sub = self.listCtrl.GetItemText(index, 3)

		tinput = TreeInput(self, code, name, mother, sub) 
		if tinput.ShowModal() == wx.ID_OK:
			code, name, mother, sub = tinput.code.GetValue(), tinput.name.GetValue(), tinput.mother.GetValue(), tinput.sub.GetValue()
			tinput.Destroy()
		else:
			tinput.Destroy()
			return

		self.listCtrl.SetItemText(index, code)
		self.listCtrl.SetStringItem(index, 1, name)
		self.listCtrl.SetStringItem(index, 2, mother)
		self.listCtrl.SetStringItem(index, 3, sub)

	def Delete(self):
		index = self.listCtrl.GetFocusedItem()
		if index == -1: return
		self.listCtrl.DeleteItem(index)

	def Display(self):
		self.listCtrl.DeleteAllItems()
		for code, (name, mother, sub) in self.parent.dTree.items():
			index = self.listCtrl.InsertStringItem(sys.maxint, code)
			self.listCtrl.SetStringItem(index, 1, name)
			self.listCtrl.SetStringItem(index, 2, mother)
			self.listCtrl.SetStringItem(index, 3, sub)


class MultilineInput(wx.Dialog):
	def __init__(self, parent, title, content=''):
		wx.Dialog.__init__(self, parent, -1, title, wx.DefaultPosition, (400, 300))
		self.parent = parent

		self.textCtrl = wx.TextCtrl(self, -1, content, (10, 10), (380, 250),  wx.TE_MULTILINE)
		self.buttonOK = wx.Button(self, wx.ID_OK, u'확인(&Y)', (180, 170), (100, 20))
		self.buttonCancel = wx.Button(self, wx.ID_CANCEL, u'취소(&N)', (290, 170), (100, 20))




def TransferManager(dFileInfo, q):
	"""q = pNum, filename, totalSize, downSize, elapsedTime."""
	while True:
		try:
			pNum, fileName, totalSize, downSize, elapsedTime = q.get()
			if fileName == 'exit': return
			dFileInfo[(pNum, fileName)] = (totalSize, downSize, elapsedTime)
			if totalSize == downSize: 
				dFileInfo.pop((pNum, fileName))
		except:
			pass



class TransferInfo(wx.Dialog, Utility):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, u'파일 전송 정보', wx.DefaultPosition, (400, 400))
		Utility.__init__(self)
		self.parent = parent

		self.listCtrl = wx.ListCtrl(self, -1, (10, 10), (380, 380), wx.LC_REPORT | wx.LC_SINGLE_SEL)
		self.listCtrl.InsertColumn(0, u'', width=50)
		self.listCtrl.InsertColumn(1, u'', width=150)
		self.listCtrl.InsertColumn(2, u'전송율', width=50)
		self.listCtrl.InsertColumn(3, u'전송속도', width=50)
		self.listCtrl.InsertColumn(4, u'크기', width=80)
		self.listCtrl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.LoadFileInfo()

	def OnClose(self, e):
		self.Destroy()

	def OnKeyDown(self, e):
		key = e.GetKeyCode()
		if key == wx.WXK_SPACE:
			self.LoadFileInfo()
		elif key == wx.WXK_ESCAPE:
			self.OnClose(e)
		elif key == wx.WXK_DELETE:
			self.Stop()

		else:
			e.Skip()

	def Stop(self):
		index = self.listCtrl.GetFocusedItem()
		if index == -1: return
		pNum = self.listCtrl.GetItemText(index, 0)
		fileName = self.listCtrl.GetItemText(index, 1)
		if not MsgBox(self, u'경고', u'다음 파일 전송을 취소할까요?\n파일이름 : %s\n프로세스번호 : %s' % (fileName, pNum), True): return
		try:
			p = self.parent.dProcess[(pNum, fileName)]
			self.parent.dFileInfo.pop((pNum, fileName))
			p.terminate()

			self.Play('delete.wav')
			self.LoadFileInfo()
		except:
			pass


	def LoadFileInfo(self):
		index = self.listCtrl.GetFocusedItem()
		if index == -1: index = 0

		self.listCtrl.DeleteAllItems()
		for (pNum, fileName), (totalSize, downSize, elapsedTime) in self.parent.dFileInfo.items():
			if downSize == totalSize: 
				try:
					self.parent.dFileInfo.pop((pNum, fileName))
				except:
					pass
				continue
			row = self.listCtrl.InsertStringItem(sys.maxint, pNum)
			self.listCtrl.SetStringItem(row, 1, fileName)
			ratio = 100.0 * downSize / totalSize
			self.listCtrl.SetStringItem(row, 2, u'%0.2f %%' % ratio)
			if elapsedTime:
				speed = downSize / 1024.0 / 1024.0 / elapsedTime 
			else:
				speed = 0
			self.listCtrl.SetStringItem(row, 3, u'%0.2f MB/sec' % speed)
			size = totalSize / 1024.0 / 1024.0
			self.listCtrl.SetStringItem(row, 4, u'%0.2f MB' % size)

		self.listCtrl.Focus(index)
		self.listCtrl.Select(index)




class Search(wx.Dialog):

	sfl = {u'전체': 'wr_subject||wr_content||mb_id||wr_name', u'제목': 'wr_subject', u'내용': 'wr_content', u'제목+내용': 'wr_subject||wr_content', u'아이디': 'mb_id', u'글쓴이': 'wr_name'}

	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, u'게시판 검색', wx.DefaultPosition, wx.Size(340, 130))

		wx.StaticText(self, -1, u'검색어', (10, 10), (100, 30))
		self.textCtrl = wx.TextCtrl(self, -1, '', (120, 10), (210, 30))

		wx.StaticText(self, -1, u'검색대상', (10, 50), (100, 30))
		self.choice = wx.Choice(self, -1, (120, 50), (210, 30), [u'전체', u'제목', u'내용', u'제목+내용', u'아이디', u'글쓴이'])

		self.buttonOK = wx.Button(self, wx.ID_OK, u'확인', (120, 90), (100, 30))
		self.buttonCancel = wx.Button(self, wx.ID_CANCEL, u'취소(ESC)', (230, 90), (100, 30))

		self.choice.SetSelection(0)
		self.textCtrl.SetFocus()

		accel = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CANCEL), (wx.ACCEL_NORMAL, wx.WXK_RETURN, wx.ID_OK)])
		self.SetAcceleratorTable(accel)




class CodeMove(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, u'코드 바로가기', wx.DefaultPosition, wx.Size(340, 90))
		self.parent = parent

		wx.StaticText(self, -1, u'코드', (10, 10), (100, 30))
		self.combo = wx.ComboBox(self, -1, "", (120, 10), (210, 30), self.parent.dTree.keys(), wx.CB_DROPDOWN | wx.CB_SORT | wx.CB_READONLY)

		self.buttonOK = wx.Button(self, wx.ID_OK, u'확인(Enter)', (120, 50), (100, 30))
		self.buttonCancel = wx.Button(self, wx.ID_CANCEL, u'취소(ESC)', (230, 50), (100, 30))
		self.combo.SetFocus()

		accel = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CANCEL), (wx.ACCEL_NORMAL, wx.WXK_RETURN, wx.ID_OK)])
		self.SetAcceleratorTable(accel)



class HelpBox(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, u'초록멀티2 도움말', wx.DefaultPosition, (600, 500))

		self.textCtrl = wx.TextCtrl(self, -1, self.LoadHelp(), (10, 10), (580, 480), wx.TE_MULTILINE | wx.TE_READONLY)

		self.close = wx.Button(self, wx.ID_CANCEL, u'닫기', (600, 500), (1,1))
		self.close.Hide()
		self.close.Bind(wx.EVT_BUTTON, self.OnClose)
		accel = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CANCEL)])
		self.SetAcceleratorTable(accel)



		self.ShowModal()

	def LoadHelp(self):
		txt = ''
		if os.path.exists('readme.txt'):
			with open('readme.txt', 'rb') as f:
				txt = f.read()
				txt = unicode(txt, 'utf-8')
		else:
			txt = u'도움말이 담긴 readme.txt 파일이 없습니다.'
		return txt

	def OnClose(self, e):
			self.Destroy()

