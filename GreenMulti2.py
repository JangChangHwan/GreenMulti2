# coding: utf-8

import wx
import re
from menuPanel import *
from util import *
from multiprocessing import Process, Queue, freeze_support
from threading import Thread
from collections import OrderedDict
from win32com.client import Dispatch
import sys, os
import time
import datetime
from subprocess import Popen




class GreenMulti2(wx.Frame, Utility):

	cookies = ''
	limit = 3
	transQueue = Queue()
	dFileInfo = OrderedDict()
	mainTitle = ''
	dProcess = {}
	mailCount = 0
	memoCount = 0

	def __init__(self, title):
		wx.Frame.__init__(self, None, -1, title, wx.DefaultPosition, (500, 500))
		Utility.__init__(self)
		self.mainTitle = title

		# 메뉴바
		menuBar = wx.MenuBar()
		fileMenu = wx.Menu()

		self.loginMI = wx.MenuItem(fileMenu, -1, u"로그인\tCtrl+L")
		fileMenu.AppendItem(self.loginMI)
		self.Bind(wx.EVT_MENU, self.OnLogin, self.loginMI)

		homeMI = wx.MenuItem(fileMenu, -1, u"초기화면으로\tAlt+Home")
		fileMenu.AppendItem(homeMI)
		self.Bind(wx.EVT_MENU, self.OnHome, homeMI)

		gotoMI = wx.MenuItem(fileMenu, -1, u"코드 바로가기\tCtrl+G")
		fileMenu.AppendItem(gotoMI)
		self.Bind(wx.EVT_MENU, self.OnGoTo, gotoMI)

		downloadFolderMI = wx.MenuItem(fileMenu, -1, u"다운로드 폴더 변경")
		fileMenu.AppendItem(downloadFolderMI)
		self.Bind(wx.EVT_MENU, self.OnDownloadFolder, downloadFolderMI)

		openFolderMI = wx.MenuItem(fileMenu, -1, u"다운로드 폴더 열기\tCtrl+O")
		fileMenu.AppendItem(openFolderMI)
		self.Bind(wx.EVT_MENU, self.OnOpenFolder, openFolderMI)

		shortcutMI = wx.MenuItem(fileMenu, -1, u'바탕화면 바로가기 추가/제거')
		fileMenu.AppendItem(shortcutMI)
		self.Bind(wx.EVT_MENU, self.OnShortcut, shortcutMI)


		transInfoMI = wx.MenuItem(fileMenu, -1, u"파일 전송 정보\tCtrl+J")
		fileMenu.AppendItem(transInfoMI)
		self.Bind(wx.EVT_MENU, self.OnTransInfo, transInfoMI)

		self.xxxMI = wx.MenuItem(fileMenu, -1, u"메뉴관리")
		fileMenu.AppendItem(self.xxxMI)
		self.Bind(wx.EVT_MENU, self.OnMenuManage, self.xxxMI)

		quitMI = wx.MenuItem(fileMenu, -1, u"종료")
		fileMenu.AppendItem(quitMI)
		self.Bind(wx.EVT_MENU, self.OnClose, quitMI)
		menuBar.Append(fileMenu, u'파일(&F)')
		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.menu = MenuPanel(self)

		self.Show()

		th = Thread(target=TransferManager, args=(self.dFileInfo, self.transQueue))
		th.start()

		self.Login()


	def OnClose(self, e):
		# 전송 중인 프로 세스 종료 여부
		for p in self.dProcess.values():
			if p is not None and p.is_alive():
				if MsgBox(self, u'경고', u'파일 전송이 끝나지 않았습니다. 그래도 초록멀티를 종료할까요?', True):
					break
				else:
					return
		# 프로세스 강제종료
		for p in self.dProcess.values():
			if p is not None: p.terminate()

		# 파일 전송 관리자 쓰레드를 종료
		self.transQueue.put(('', 'exit', 0, 0, 0))
		self.Destroy()


	def OnMenuManage(self, e):
		mgr = MenuManager(self)
		mgr.ShowModal()
		mgr.Destroy()


	def OnLogin(self, e):
		if self.loginMI.GetText().startswith(u'로그인'): 
			self.Login()
		else:
			self.Logout()


	def Login(self):
#		try:
			kbuid = self.Decrypt(self.ReadReg('kbuid'))
			if not kbuid: kbuid = InputBox(self, u'넓은마을 로그인', u'아이디')

			kbupw = self.Decrypt(self.ReadReg('kbupw'))
			if not kbupw: kbupw = InputBox(self, u'넓은마을 로그인', u'비밀번호', pwd=1) 
			if not kbuid or not kbupw: return MsgBox(self, u'알림', u'사용자 아이디와 비밀번호는 필수 입력사항입니다.')

			params = {'url': 'http%3A%2F%2Fweb.kbuwel.or.kr', 'mb_id': kbuid, 'mb_password': kbupw}
			self.menu.Post('/bbs/login_check.php', params)
			if self.menu.response.getheader('Location'):
				self.cookies = self.menu.cookies = self.menu.response.getheader('set-cookie')
				self.WriteReg('kbuid', self.Encrypt(kbuid))
				self.WriteReg('kbupw', self.Encrypt(kbupw))
				self.loginMI.SetText(u'로그아웃\tCtrl+L')
			else:
				self.Logout(u'넓은마을 로그인에 실패했습니다. 아이디와 비밀번호를 정확하게 입력해 주세요.')
				return

			# 초록등대 정회원 확인
			self.menu.Get('/bbs/board.php?bo_table=green61&cl=green')
			title = self.menu.soup.head.title.getText()
			if not title.startswith(u'오류')			:
				self.limit = 100

			self.menu.Get('/bbs/board.php?bo_table=free')
			self.Play("start.wav", async=False)
			self.CheckMailMemo(self, self.menu.soup)

#		except:
#			pass


	def Logout(self, msg=u'로그아웃하였습니다. 로그인 정보를 삭제했습니다.'):
		try:
			self.cookies = self.menu.cookies = ''
			self.WriteReg('kbuid', '')
			self.WriteReg('kbupw', '')
			self.loginMI.SetText(u'로그인')
			MsgBox(self, u'알림', msg)
		except:
			pass


	def OnDownloadFolder(self, e):
		folder = self.ReadReg('downloadfolder')
		if not folder: 
			shell = Dispatch('WScript.Shell')
			folder = shell.SpecialFolders('MyDocuments')
		dirDialog = wx.DirDialog(self, u'다운로드 폴더 선택', folder)
		if dirDialog.ShowModal() == wx.ID_OK:
			self.WriteReg('downloadfolder', dirDialog.GetPath())
			MsgBox(self, u'다운로드폴더 변경 완료', dirDialog.GetPath() + u' 폴더로 변경했습니다.')
		dirDialog.Destroy()


	def OnTransInfo(self, e):
		infoDialog = TransferInfo(self)
		infoDialog.ShowModal()


	def OnOpenFolder(self, e):
		downFolder = self.ReadReg('downloadfolder')
		if not downFolder: 
			shell = Dispatch('WScript.Shell')
			downFolder = shell.SpecialFolders('MyDocuments')
		if type(downFolder) == unicode: downFolder = downFolder.encode('euc-kr', 'ignore')
		Popen(['explorer.exe', downFolder])


	def OnShortcut(self, e):
		shell = Dispatch('WScript.Shell')
		desktop = shell.SpecialFolders('Desktop')
		path = os.path.join(desktop, 'GreenMulti2.lnk')
		target = sys.argv[0]

		if os.path.exists(path):
			os.remove(path)
			MsgBox(self, u'알림', u'바탕화면에서 바로가기를 제거했습니다.')
		else:
			shortcut = shell.CreateShortcut(path)
			shortcut.Targetpath = target
			shortcut.WindowStyle = 1
			shortcut.HotKey = 'CTRL+ALT+G'
			shortcut.IconLocation = 'notepad.exe, 0'
			shortcut.Description = 'GreenMulti2'
			shortcut.WorkingDirectory = os.path.dirname(sys.argv[0])
			shortcut.Save()
			MsgBox(self, u'알림', u'바탕화면에 바로가기를 만들었습니다.')


	def OnHome(self, e):
		self.ClosePanels()
		self.menu.Display('top')
		self.menu.Play('home.wav')


	def OnGoTo(self, e):
		code = InputBox(self, u'코드 바로가기', u'코드 : ')
		if not code: return
		if not code in self.dTree: return MsgBox(self, u'오류', u'존재하지 않는 바로가기 코드입니다.')
		self.ClosePanels()
		if code != 'top': self.menu.Display(self.dTree[code][1])
		self.menu.Display(code)
		self.menu.Play('codeMove.wav')


	def ClosePanels(self, panels=['bbs', 'view', 'write', 'rmail', 'wmail', 'mlist', 'mview', 'wmemo']):
		for panel in panels:
			try:
				if hasattr(self, panel): 
					p = getattr(self, panel)
					p.Hide()
					p.Destroy()
			except:
				continue


	def CheckMailMemo(self, ancestor, soup):
		iMail = iMemo = 0
		mail = soup.find('a', title=re.compile(u'^메일'))
		m1 = re.search(u'새메일(\\d+)통', mail.getText())
		if m1 is not None:
			iMail = int(m1.group(1))

		memo = self.menu.soup.find('a', title=re.compile(u'^메모'))
		m2 = re.search(u'새메모 \\((\\d+)\\)', memo.getText())
		if m2 is not None:
			iMemo = int(m2.group(1))

		if ancestor.mailCount < iMail and ancestor.memoCount < iMemo:
			ancestor.Play('mailMemo.wav', async=False)
		elif ancestor.mailCount < iMail:
			ancestor.Play('mail.wav', async=False)
		elif ancestor.memoCount < iMemo:
			ancestor.Play('memo.wav', async=False)

		ancestor.mailCount = iMail
		ancestor.memoCount = iMemo



def BetaTest():
	limitDate = datetime.date(2017, 5, 31)
	currentDate = datetime.date.fromtimestamp(time.time())
	if limitDate < currentDate:
		sys.exit()

if __name__ == '__main__':
	BetaTest()
	freeze_support()
	app = wx.App()
	GreenMulti2(u'초록멀티2 Beta4')
	app.MainLoop()
