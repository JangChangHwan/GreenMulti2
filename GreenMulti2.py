# coding: utf-8

import basicMenu
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
import ctypes
import urllib


class GreenMulti2(wx.Frame, Utility):

	dTree = OrderedDict()
	cookies = ''
	limit = 3
	transQueue = Queue()
	dFileInfo = OrderedDict()
	mainTitle = ''
	dProcess = {}
	mailCount = 0
	memoCount = 0
	tts = False
	ttsName = ''
	processNumber = 0

	def __init__(self, title):
		wx.Frame.__init__(self, None, -1, title, wx.DefaultPosition, (500, 500))
		Utility.__init__(self)
		self.mainTitle = title
		self.LoadTreeMenu()
		self.PrepareSpeaking()

		# 메뉴바
		menuBar = wx.MenuBar()
		self.fileMenu = wx.Menu()

		self.loginMI = wx.MenuItem(self.fileMenu, -1, u"로그인\tCtrl+L")
		self.fileMenu.Append(self.loginMI)
		self.Bind(wx.EVT_MENU, self.OnLogin, self.loginMI)

		homeMI = wx.MenuItem(self.fileMenu, -1, u"초기화면으로\tAlt+Home")
		self.fileMenu.Append(homeMI)
		self.Bind(wx.EVT_MENU, self.OnHome, homeMI)

		gotoMI = wx.MenuItem(self.fileMenu, -1, u"코드 바로가기\tCtrl+G")
		self.fileMenu.Append(gotoMI)
		self.Bind(wx.EVT_MENU, self.OnGoTo, gotoMI)

		downloadFolderMI = wx.MenuItem(self.fileMenu, -1, u"다운로드 폴더 변경")
		self.fileMenu.Append(downloadFolderMI)
		self.Bind(wx.EVT_MENU, self.OnDownloadFolder, downloadFolderMI)

		openFolderMI = wx.MenuItem(self.fileMenu, -1, u"다운로드 폴더 열기\tCtrl+O")
		self.fileMenu.Append(openFolderMI)
		self.Bind(wx.EVT_MENU, self.OnOpenFolder, openFolderMI)

		shortcutMI = wx.MenuItem(self.fileMenu, -1, u'바탕화면 바로가기 추가/제거')
		self.fileMenu.Append(shortcutMI)
		self.Bind(wx.EVT_MENU, self.OnShortcut, shortcutMI)

		transInfoMI = wx.MenuItem(self.fileMenu, -1, u"파일 전송 정보\tCtrl+J")
		self.fileMenu.Append(transInfoMI)
		self.Bind(wx.EVT_MENU, self.OnTransInfo, transInfoMI)

		contactMI = wx.MenuItem(self.fileMenu, -1, u"제작자에게...")
		self.fileMenu.Append(contactMI)
		self.Bind(wx.EVT_MENU, self.OnContact, contactMI)

		self.daisyMI = wx.MenuItem(self.fileMenu, -1, u"데이지 자동 변환", kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.OnAutoDaisy, self.daisyMI)

		menuDataMI = wx.MenuItem(self.fileMenu, -1, u"메뉴 데이터 파일 다운로드")
		self.fileMenu.Append(menuDataMI)
		self.Bind(wx.EVT_MENU, self.OnMenuData, menuDataMI)
		helpMI = wx.MenuItem(self.fileMenu, -1, u"도움말\tF1")
		self.fileMenu.Append(helpMI)
		self.Bind(wx.EVT_MENU, self.OnHelp, helpMI)

		quitMI = wx.MenuItem(self.fileMenu, -1, u"종료")
		self.fileMenu.Append(quitMI)
		self.Bind(wx.EVT_MENU, self.OnClose, quitMI)
		menuBar.Append(self.fileMenu, u'파일(&F)')
		self.SetMenuBar(menuBar)

		# 상태표시줄
		self.sb = wx.StatusBar(self, -1)
		self.sb.SetFieldsCount(2)
		self.SetStatusBar(self.sb)


		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.menu = MenuPanel(self)


		self.Show()

		th1 = Thread(target=TransferManager, args=(self.dFileInfo, self.transQueue))
		th1.start()


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
		self.Hide()
		self.Play('exit.wav', async=False)
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


			# 넓마 로그인
			params = {'url': 'http%3A%2F%2Fweb.kbuwel.or.kr', 'mb_id': kbuid, 'mb_password': kbupw}
			self.menu.Post('/bbs/login_check.php', params)
			if not self.menu.response:
				wx.MessageBox(u"넓은마을 서버에 접속할 수 없습니다.", u"연결 오류", parent=self)
				return 
			elif self.menu.response.getheader('Location'):
				self.cookies = self.menu.cookies = self.menu.response.getheader('set-cookie')
				self.WriteReg('kbuid', self.Encrypt(kbuid))
				self.WriteReg('kbupw', self.Encrypt(kbupw))
				self.loginMI.SetText(u'로그아웃\tCtrl+L')
			else:
				self.Logout(u'넓은마을 로그인에 실패했습니다. 아이디와 비밀번호를 정확하게 입력해 주세요.')
				return

			# 초록등대 정회원 확인
			self.menu.Get('http://web.kbuwel.or.kr/plugin/ar.club/member.php?&cl=green')
			m = re.search(u'회원등급 :[^\\(\\)]*\\((\\d+)\\)', self.menu.html)
			if m is not None and int(m.group(1)) >= 5:
				self.limit = 100
				self.fileMenu.Insert(9, self.daisyMI)
				if self.ReadReg('autodaisy'): 			self.fileMenu.Check(self.daisyMI.GetId(), True)
			else:
				self.limit = 3
				self.WriteReg('autodaisy', '')

			self.Play('start.wav', async=False)

			# 메일 메모 확인
			self.menu.Get('/bbs/board.php?bo_table=free')
			self.CheckMailMemo(self, self.menu.soup)
#		except:
#			pass


	def Logout(self, msg=u'로그아웃하였습니다. 로그인 정보를 삭제했습니다.'):
		try:
			if self.limit == 100:
				self.limit == 3
				self.fileMenu.Remove(self.daisyMI)
			self.cookies = self.menu.cookies = ''
			self.WriteReg('kbuid', '')
			self.WriteReg('kbupw', '')
			self.loginMI.SetText(u'로그인\tCtrl+L')
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
		self.Play('home.wav')


	def OnGoTo(self, e):
		cm = CodeMove(self)
		if cm.ShowModal() == wx.ID_CANCEL:
			cm.Destroy()
			return

		code = cm.combo.GetValue()
		cm.Destroy()

		if not code or not code in self.dTree: return
		self.ClosePanels()
		if code != 'top': self.menu.Display(self.dTree[code][1])
		self.menu.Display(code)
		self.Play('codeMove.wav')


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
		memo = soup.find('a', title=re.compile(u'^메모'))
		if mail is None or memo is None: return

		m1 = re.search(u'새메일(\\d+)통', mail.getText())
		if m1 is not None:
			iMail = int(m1.group(1))

		m2 = re.search(u'새메모 \\((\\d+)\\)', memo.getText())
		if m2 is not None:
			iMemo = int(m2.group(1))

		if ancestor.mailCount < iMail and ancestor.memoCount < iMemo:
			self.Play('mailMemo.wav')
		elif ancestor.mailCount < iMail:
			self.Play('mail.wav')
		elif ancestor.memoCount < iMemo:
			self.Play('memo.wav')

		ancestor.mailCount = iMail
		ancestor.memoCount = iMemo


	def OnMenuData(self, e):
		try:
			currentVersion = self.ReadReg("KBUMenu.version")
			if not currentVersion: currentVersion = "0"
			r = urllib.urlopen("https://docs.google.com/uc?export=download&id=1pD_qONu0kW1ftWi2JWOvFNFk186JTcU_")
			ver = r.read()
			if int(currentVersion) == int(ver):
				wx.MessageBox(u"최신 메뉴 데이터 파일입니다.\n 현재 버전: %s" % currentVersion, u"알림", parent=self)
				return

			sel = wx.MessageBox(u"새로운 버전을 다운로드 할까요?\n현재 버전: %s\n최신 버전 : %s" % (currentVersion, ver), u"알림", style=wx.YES|wx.NO, parent=self)
			if not sel == wx.YES:
				return
			dataFile = os.path.join(os.path.dirname(sys.executable), "KBUMenu.dat")
			if os.path.exists(dataFile + ".bak"):
				os.remove(dataFile + ".bak")
			if os.path.exists(dataFile):
				os.rename(dataFile, dataFile + ".bak")
			r2 = urllib.urlopen("https://docs.google.com/uc?export=download&id=1HFTO_38JX3VX2HzyYY47I4-oHPQ4__xH")
			menuData = r2.read()
			with open(dataFile, "wb") as f:
				f.write(menuData)
				self.WriteReg("KBUMenu.version", str(ver))
				wx.MessageBox(u"다운로드를 완료했습니다.", u"알림", parent=self)
		except:
			pass



	def OnHelp(self, e):
		HelpBox(self)

	def PrepareSpeaking(self):
		# NVDA 우선 
		try:
			self.tts = ctypes.windll.LoadLibrary('nvdaControllerClient32.dll')
			res = self.tts.nvdaController_testIfRunning()
			if res == 0:
					self.ttsName = 'nvda'
					return
			else:
				try:
					self.tts = Dispatch('SenseReader.Application')
					self.ttsName = 'xvsrd'
				except:
					self.tts = False
					self.tts = False
		except:
			self.tts = False
			self.ttsName = False


	def Speak(self, s):
		try:
			if not self.tts: return
			if self.ttsName == 'xvsrd':
				self.tts.StopSpeaking()
				self.tts.Speak(s)
			elif self.ttsName == 'nvda':
				self.tts.nvdaController_speakText('')
				self.tts.nvdaController_speakText(s)
		except:
			self.tts = None

	def LoadTreeMenu(self):

		# kbuMenu.dat 파일 불러 오기
		try:
			with open('KBUMenu.dat', 'rb') as f:
				data = f.read()
				data = basicMenu.basicMenu + unicode(data, 'utf-8')
				data = data.replace('\r', '')
				menus = data.split('\n')
				for m in menus:
					if m.startswith('#')  or not '\t' in m: continue
					code, name, parent, sub = m.split('\t')
					if not code in self.dTree: self.dTree[code] = (name, parent, sub)
		except:
			sys.exit()


	def OnAutoDaisy(self, e):
		auto = self.ReadReg('autodaisy')
		if auto:
			self.WriteReg('autodaisy', '')
			self.fileMenu.Check(self.daisyMI.GetId(), False)
		else:
			self.WriteReg('autodaisy', 'auto')
			self.fileMenu.Check(self.daisyMI.GetId(), True)


	def OnContact(self, e):
		if not self.cookies: return MsgBox(self, u'알림', u'먼저 로그인하세요.')
		mi = MultilineInput(self, u'개발자에게 쪽지보내기')
		if mi.ShowModal() == wx.ID_CANCEL: return mi.Destroy()
		content = mi.textCtrl.GetValue()
		mi.Destroy()
		if not content: return MsgBox(self, u'오류', u'메시지 내용이 없습니다. 쪽지 보내기를 취소합니다.')

		dInfo = {'me_recv_mb_id': 'philjang', 'me_memo': content}
		self.menu.Post('/plugin/ar.memo/memo_form_update.php', dInfo)
		self.Play('up.wav')


	def SpeakText(self, ctrl):
		text = ctrl.GetValue()
		if text:
			self.Speak(text)



def BetaTest():
	limitDate = datetime.date(2017, 6, 30)
	currentDate = datetime.date.fromtimestamp(time.time())
	if limitDate < currentDate:
		sys.exit()

if __name__ == '__main__':
#	BetaTest()
	freeze_support()
	app = wx.App()
	GreenMulti2(u'초록멀티 2.1.3')
	app.MainLoop()
