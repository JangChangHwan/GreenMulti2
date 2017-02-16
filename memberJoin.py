# coding: utf-8


from util import *
from http import *
from collections import OrderedDict
import wx
import re


class MemberJoin(wx.Dialog, Http, Utility):

	joined = False
	action = ''
	title = ''
	dTags = OrderedDict()
	lInputs = []

	def __init__(self, parent, url):
		self.parent = parent
		self.url = url
		wx.Dialog.__init__(self, parent, -1, u'', wx.DefaultPosition, (400, 400))
		Utility.__init__(self)
		Http.__init__(self, self.parent)

		try:
			self.GetInfo(self.url)
		finally:
			self.SetControls()
			self.ShowModal()


	def OnCancel(self, e):
			self.Destroy()



	def GetInfo(self, url):
		self.Get(url)

		# 회원 가입이 된 상태라면 
		if u'회원등급 :' in self.html: 
			self.joined = True
			div = self.soup.find('div', attrs={'class': 'box_info_msg'})
			if div is not None: 
				self.memberInfo = div.getText()
				self.memberInfo = re.sub(u'(?ims)회원정보 수정.*회원정보 탈퇴|\n{2,}', '', self.memberInfo)



		# 회원 미가입 상태라면
		else:
			self.dTags.clear()
			self.action = 		'http://web.kbuwel.or.kr/plugin/ar.club/'  + self.response.getheader('Location')
			self.Get(self.action)
			# 대화상자 제목
			divTitle = self.soup.find('div', style='text-align:center;font-size:1.5em;')
			if divTitle is not None:
				self.title = divTitle.getText()

			# 태그 수집
			self.dTags = {'qmd': 'join'}
			# input 수집
			# key : name, value = (value, descript)
			tds = self.soup('td', attrs={'class': 'td_itm1'})
			if tds is None: return
			for td in tds:
				try:
					name = td.input['name']
					value = td.input['value']
					desc = td.getText()
					self.dTags[name] = (value, desc)
					if name == 'cl_nick': self.dTags[name] = value
				except:
					pass


	def SetControls(self):
		if self.joined:
			self.SetTitle(u'동호회 회원 정보')
			self.textCtrl = wx.TextCtrl(self, -1, self.memberInfo, (10, 10), (380, 350)			, wx.TE_MULTILINE | wx.TE_READONLY)
			# 닫기 버튼
			self.buttonCancel = wx.Button(self, wx.ID_CANCEL, u'닫기', (290, 370), (100, 20))
			self.buttonCancel.Bind(wx.EVT_BUTTON, self.OnCancel)
		
# 미가입 상황
		else:
			# 대화상자 제목 변경
			self.SetTitle(self.title)
			# 대화상자 크기 변경
			if len(self.dTags) < 2: return
			inputCount = len(self.dTags) - 2 # hidden과  닉네임 제외
			width = 450
			height = inputCount * 50 + 40
			self.SetSize((width, height))
			# input 태그에 해당하는 textCtrl 생성
			n = 0
			for k, v in self.dTags.items():
				if type(v) != tuple: continue
				wx.StaticText(self, -1, v[1], (10, n*50+10), (210, 40))
				tc = wx.TextCtrl(self, -1, v[0], (230, n*50+10), (210, 40), name=k)
				self.lInputs.append(tc)
				n += 1
			# 버튼 두개
			self.buttonJoin = wx.Button(self, wx.ID_OK, u'가입신청', (120, n*50+10), (100, 20))
			self.buttonJoin.Bind(wx.EVT_BUTTON, self.OnJoin)
			self.buttonCancel = wx.Button(self, wx.ID_CANCEL, u'취소', (230, n*50+10), (100, 20))
			self.buttonCancel.Bind(wx.EVT_BUTTON, self.OnCancel)


	def OnJoin(self, e):
		for tc in self.lInputs:
			if not tc.GetValue(): 
				MsgBox(self, u'오류', u'모든 항목은 필수 입력 사항입니다. 질문에 빠짐없이 답해 주세요.')
				return 

		# dTags 정리
		for tc in self.lInputs:
			key = tc.Name
			value = tc.GetValue()
			self.dTags[key] = value

		# posting
		self.Post(self.action, self.dTags)
		loca = self.response.getheader('Location')
		# 가입 성공
		if loca and 'member.php' in loca:
			MsgBox(self, u'가입 신청 완료', u'동호회 가입 신청을 완료했습니다. 자세한 것은 해당 동호회 운영자에게 문의하세요.')
			self.OnCancel(e)

		# 가입 실패
		else:
			MsgBox(self, u'가입 실패', u'동호회 가입에 실패했습니다. 닉네임과 질문에 대한 답을 정확하게 입력했는지 확인해 주세요.')
			return

