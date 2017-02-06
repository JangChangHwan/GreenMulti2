# coding: utf-8
# 함수모음 util.py

import pickle
import sys
import winsound
import os
import _winreg
import wx
from collections import OrderedDict




class Utility(object):

	dTree = OrderedDict()

	def __init__(self):
		self.key = "%x" % os.path.getctime(os.environ["APPDATA"])
		self.LoadTreeMenu()

	def LoadTreeMenu(self):
		try:
			with open('treemenu.dat', 'rb') as f:
				self.dTree = pickle.load(f)
		except:
			self.dTree['top'] = (u'초기메뉴', '', 'green|guide|mail|bbs|computer|potion|blindnews||magazin|pds')


	def SaveTreeMenu(self):
		try:
			with open('treemenu.dat', 'wb') as f:
				pickle.dump(self.dTree, f)
		except:
			pass


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

	def ParamSplit(self, url):
# url 주소 문자열을 유니코드로 바꾸고 base_url 문자열과 매개변수가 담긴 사전으로 반환한다.
		d = {}
		base_url, params = url.split("?")
		for kvp in params.split("&"):
			if not kvp or not ("=" in kvp): continue
			k, v = kvp.split("=")
			if not k: continue
			d[k] = v
		return (base_url, d)

	def ParamJoin(self, d, enc = True):
# 다시 url로 조립 물론 urlencode를  사용할지를 선택
		if enc: 
			params = urllib.urlencode(d)
		else:
			params = "&".join(["%s=%s" % (k, v) for k, v in d.items()])
		return params




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


class MultilineEditor(wx.Dialog):
	def __init__(self, parent, title, content=''):
		wx.Dialog.__init__(self, parent, -1, title, wx.DefaultPosition, (400, 200))

		self.textCtrl = wx.TextCtrl(self, -1, content, (10, 10), (380, 150),  wx.TE_MULTILINE)
		self.buttonOK = wx.Button(self, wx.ID_OK, u'확인(&Y)', (180, 170), (100, 20))
		self.buttonCancel = wx.Button(self, wx.ID_CANCEL, u'취소(&N)', (290, 170), (100, 20))


def TransferManager(dFileInfo, q):
	"""q = filename, mode, totalSize, downSize, elapsedTime."""
	while True:
		fileName, mode, totalSize, downSize, elapsedTime = q.get()
		if mode == 'exit': return
		dFileInfo[fileName] = (mode, totalSize, downSize, elapsedTime)



class TransferInfo(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, u'파일 전송 정보', wx.DefaultPosition, (400, 400))
		self.parent = parent

		self.listCtrl = wx.ListCtrl(self, -1, (10, 10), (380, 380), wx.LC_REPORT | wx.LC_SINGLE_SEL)
		self.listCtrl.InsertColumn(0, u'파일이름', width=150)
		self.listCtrl.InsertColumn(1, u'mode', width=50)
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

		else:
			e.Skip()

	def LoadFileInfo(self):
		index = self.listCtrl.GetFocusedItem()
		if index == -1: index = 0

		self.listCtrl.DeleteAllItems()
		for fileName, (mode, totalSize, downSize, elapsedTime) in self.parent.dFileInfo.items():
			row = self.listCtrl.InsertStringItem(sys.maxint, fileName)
			self.listCtrl.SetStringItem(row, 1, mode)
			ratio = 100.0 * downSize / totalSize
			if ratio == 100: 
				self.parent.dFileInfo.pop(fileName)
				continue
			self.listCtrl.SetStringItem(row, 2, u'%0.2f %%' % ratio)
			speed = downSize / 1024.0 / 1024.0 / elapsedTime 
			self.listCtrl.SetStringItem(row, 3, u'%0.2f MB/sec' % speed)
			size = totalSize / 1024.0 / 1024.0
			self.listCtrl.SetStringItem(row, 4, u'%0.2f MB' % size)

		self.listCtrl.Focus(index)
		self.listCtrl.Select(index)




class Search(wx.Dialog):

	sfl = {u'전체': 'wr_subject||wr_content||mb_id||wr_name', u'제목': 'wr_subject', u'내용': 'wr_content', u'제목+내용': 'wr_subject||wr_content', u'아이디': 'mb_id', u'글쓴이': 'wr_name'}

	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, u'게시판 검색', wx.DefaultPosition, wx.Size(340, 100))

		wx.StaticText(self, -1, u'검색대상', (10, 10), (100, 20))
		self.choice = wx.Choice(self, -1, (120, 10), (210, 20), [u'전체', u'제목', u'내용', u'제목+내용', u'아이디', u'글쓴이'])
		wx.StaticText(self, -1, u'검색어', (10, 40), (100, 20))
		self.textCtrl = wx.TextCtrl(self, -1, '', (120, 40), (210, 20))

		self.buttonOK = wx.Button(self, wx.ID_OK, u'확인', (120, 70), (100, 20))
		self.buttonCancel = wx.Button(self, wx.ID_CANCEL, u'취소', (230, 70), (100, 20))

		self.choice.SetSelection(0)
		self.textCtrl.SetFocus()
