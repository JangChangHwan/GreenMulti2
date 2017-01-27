# coding: utf-8

import wx
from menuPanel import *
from util import *
from multiprocessing import Process, Queue
from threading import Thread
from collections import OrderedDict


class GreenMulti2(wx.Frame, Utility):

	cookies = ''
	transQueue = Queue()
	dFileInfo = OrderedDict()

	def __init__(self, title):
		wx.Frame.__init__(self, None, -1, title, wx.DefaultPosition, (500, 500))
		Utility.__init__(self)

		# 메뉴바
		menuBar = wx.MenuBar()
		fileMenu = wx.Menu()

		self.loginMI = wx.MenuItem(fileMenu, -1, u"로그인\tCtrl+L")
		fileMenu.AppendItem(self.loginMI)
		self.Bind(wx.EVT_MENU, self.OnLogin, self.loginMI)

		downloadFolderMI = wx.MenuItem(fileMenu, -1, u"다운로드 폴더 변경")
		fileMenu.AppendItem(downloadFolderMI)
		self.Bind(wx.EVT_MENU, self.OnDownloadFolder, downloadFolderMI)

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

		self.OnLogin('')


	def OnClose(self, e):
		self.transQueue.put(('', 'exit', 0, 0, 0))
		self.Destroy()


	def OnMenuManage(self, e):
		mgr = MenuManager(self)
		mgr.ShowModal()
		mgr.Destroy()


	def OnLogin(self, e):
#		try:
			kbuid = self.Decrypt(self.ReadReg('kbuid'))
			if not kbuid: kbuid = InputBox(self, u'넓은마을 로그인', u'아이디')

			kbupw = self.Decrypt(self.ReadReg('kbupw'))
			if not kbupw: kbupw = InputBox(self, u'넓은마을 로그인', u'비밀번호', pwd=1) 
			if not kbuid or not kbupw: return MsgBox(self, u'알림', u'사용자 아이디와 비밀번호는 필수 입력사항입니다.')

			params = {'url': 'http%3A%2F%2Fweb.kbuwel.or.kr', 'mb_id': kbuid, 'mb_password': kbupw}
			self.menu.Post('/bbs/login_check.php', params)

			if self.menu.response.getheader('Location') and 'bo_table=notice' in self.menu.response.getheader('Location'):
				self.cookies = self.menu.cookies = self.menu.response.getheader('set-cookie')
			else:
				self.Logout(u'넓은마을 로그인에 실패했습니다. 아이디와 비밀번호를 정확하게 입력해 주세요.')
				return

			# 초록등대 정회원 확인
			self.menu.Get('/bbs/board.php?bo_table=green61&cl=green')
			title = self.menu.soup.head.title.getText()
			if not title.startswith(u'오류')			:
				self.WriteReg('kbuid', self.Encrypt(kbuid))
				self.WriteReg('kbupw', self.Encrypt(kbupw))
				self.loginMI.SetText(u'로그아웃\tCtrl+L')
				self.Play("start.wav")
			else:
				self.Logout(u'초록등대 정회원이 아닙니다. 회원 가입 및 등급 관련 문의는 초록등대 운영자에게 해 주세요.')
				return

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
		dirDialog = wx.DirDialog(self, u'다운로드 폴더 선택', folder)
		if dirDialog.ShowModal() == wx.ID_OK:
			self.WriteReg('downloadfolder', dirDialog.GetPath())
			MsgBox(self, u'다운로드폴더 변경 완료', dirDialog.GetPath() + u' 폴더로 변경했습니다.')
		dirDialog.Destroy()


if __name__ == '__main__':
	app = wx.App()
	GreenMulti2(u'초록멀티 2.0')
	app.MainLoop()
