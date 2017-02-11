# coding: utf-8

import httplib, mimetypes
import os
from multiprocessing import Process, Queue
from bs4 import BeautifulSoup as bs
from MultipartPostHandler import MultipartPostHandler
from util import *
import re
import time
from winsound import Beep
from win32com.client import Dispatch


class Http(object):

	host = 'web.kbuwel.or.kr'
	cookies = ''
	html = ''
	soup = None
	response = None



	def __init__(self, parent=None):
		self.parent = parent
		if self.parent is not None:
			self.cookies = self.parent.cookies


	def Get(self, selector, soup=True, headers={}):
		selector = self.Url(selector)
		headers['Cookie'] = self.cookies
		conn = httplib.HTTPConnection(self.host)
		conn.request('GET', selector, headers=headers)
		self.response = conn.getresponse()
		if soup: self.Soup(self.response)


	def Post(self, selector, fields, soup=True):
		selector = self.Url(selector)
		fieldList = []
		for k, v in fields.items():
			if type(v) == unicode: v = v.encode('utf-8')
			fieldList.append((k, v))

		boundary, body = MultipartPostHandler.multipart_encode(fieldList, [])
		content_type = 'multipart/form-data; boundary=%s' % boundary

		h = httplib.HTTPConnection(self.host)
		h.putrequest('POST', selector)
		h.putheader('content-type', content_type)
		h.putheader('content-length', str(len(body)))
		h.putheader('Cookie', self.cookies)
		h.endheaders()
		h.send(body)
		self.response = h.getresponse()
		if soup: self.Soup(self.response)


	def Soup(self, res, encoding='utf-8'):
		html = res.read()
		self.html = unicode(html, encoding)
		self.soup = bs(html, 'html.parser')


	def Url(self, url):

		if url.startswith('./'):
			return '/bbs' + url[1:]
		elif url.startswith('board.php') or url.startswith('download.php'):
			return '/bbs/' + url
		elif url.startswith('http://web.kbuwel.or.kr'):
			return url.replace('http://web.kbuwel.or.kr', '')
		else:
			return url


	def GetTextFromTag(self, soup_tag):
		s = unicode(soup_tag)
		texts = re.findall('>([^<>]*)<', s)
		texts = [s.strip() for s in texts if re.search(u'[\\w가-힣]', s) is not None]
		text = '\r\n'.join(texts)
		text = text.replace('&nbsp;', '')
		return text




class Download(Process, Http, Utility):
	def __init__(self, filePath, url, q):
		Process.__init__(self)
		Utility.__init__(self)
		Http.__init__(self, None)
		self.filePath = filePath
		self.url = url
		self.q = q
		r = self.LoginCheck()
		if r: 
			self.run()
		else:
			self.Play('error.wav', async=False)


	def LoginCheck(self):
		try:
			kbuid = self.Decrypt(self.ReadReg('kbuid'))
			kbupw = self.Decrypt(self.ReadReg('kbupw'))
			if not kbuid or not kbupw: return False

			params = {'url': 'http%3A%2F%2Fweb.kbuwel.or.kr', 'mb_id': kbuid, 'mb_password': kbupw}
			self.Post('/bbs/login_check.php', params, soup=False)
			if self.response.getheader('Location') and 'bo_table=notice' in self.response.getheader('Location'):
				self.cookies = self.response.getheader('set-cookie')
				return True
			return False
		except:
			return False


	def run(self):

		mode = 'download'
		self.Get(self.url, soup=False)
		totalSize = self.response.length
		if os.path.exists(self.filePath) and os.path.getsize(self.filePath) == totalSize:
			self.Play('pass.wav', async=False)
			return

		self.Play('down_start.wav', async=False)
		downSize = 0
		chunck = 1024 * 256
		startTime = time.time()
		fileName = os.path.basename(self.filePath)
		f = open(self.filePath, 'wb')
		self.q.put((fileName, mode, totalSize, 0, 0))

		while True:
			part = self.response.read(chunck)
			f.write(part)
			downSize += len(part)
			elapsedTime = time.time() - startTime
			self.q.put((fileName, mode, totalSize, downSize, elapsedTime))
			if self.response.length == 0: break

		f.close()
		self.q.put((fileName, mode, totalSize, totalSize, elapsedTime))
		self.Play('down.wav', async=False)




class Upload(Process, Utility, Http):
	def __init__(self, selector, fields, files, q):
		Process.__init__(self)
		Utility.__init__(self)
		Http.__init__(self, None)
		self.selector = selector
		self.fields = fields
		self.files = files
		path = self.files['bf_file[]']
		self.filename = os.path.basename(path)
		self.files['bf_file[]'] = open(path, 'rb')

		self.q = q

		if self.LoginCheck(): self.run()

	def run(self):
		self.selector = self.Url(self.selector)
		fieldList = []
		for k, v in self.fields.items():
			if type(v) == unicode: v = v.encode('utf-8')
			fieldList.append((k, v))
		fileList = self.files.items()
		boundary, body = MultipartPostHandler.multipart_encode(fieldList, fileList)
		content_type = 'multipart/form-data; boundary=%s' % boundary
		chunck = 1024 * 256
		upSize = 0
		fileSize = len(body)
		startTime = time.time()

		h = httplib.HTTPConnection(self.host)
		h.putrequest('POST', self.selector)
		h.putheader('content-type', content_type)
		h.putheader('content-length', str(fileSize))
		h.putheader('Cookie', self.cookies)
		h.endheaders()

		self.Play('down_start.wav', async=False)
		while upSize < fileSize:
			endPart = fileSize if upSize + chunck > fileSize else upSize + chunck
			h.send(body[upSize:endPart])
			elapsedTime = time.time() - startTime
			self.q.put((self.filename, 'upload', fileSize, upSize, elapsedTime))
			upSize = endPart

		self.response = h.getresponse()
		self.q.put((self.filename, 'upload', fileSize, fileSize, elapsedTime))
		self.Play('up.wav', async=False)



	def LoginCheck(self):
		try:
			kbuid = self.Decrypt(self.ReadReg('kbuid'))
			kbupw = self.Decrypt(self.ReadReg('kbupw'))
			if not kbuid or not kbupw: return False

			params = {'url': 'http%3A%2F%2Fweb.kbuwel.or.kr', 'mb_id': kbuid, 'mb_password': kbupw}
			self.Post('/bbs/login_check.php', params, soup=False)
			if self.response.getheader('Location') and 'bo_table=notice' in self.response.getheader('Location'):
				self.cookies = self.response.getheader('set-cookie')
				return True
			return False
		except:
			return False


class DownloadFromList(Utility, Http):

	files = {}

	def __init__(self, parent, url):
		Http.__init__(self, parent)
		Utility.__init__(self)
		self.parent = parent

		self.files.clear()

		self.Get(url)

		downloadFolder = self.ReadReg('downloadfolder')
		if not downloadFolder : 
			shell = Dispatch('Wscript.Shell')
			downloadFolder = shell.SpecialFolders('MyDocuments')

		fileLinks = self.soup('a', href=re.compile('download.php'))
		if fileLinks is not None:
			for link in fileLinks:
				descript = ' '.join(link.getText().split())
				self.files[link.strong.getText()] = (descript, link['href'])

		if not self.files: return

		for fileName, (descript, fileUrl) in self.files.items():
			if fileName in self.parent.dFileInfo and self.parent.dFileInfo[fileName][0] == 'download': 
				self.Play('pass.wav', async=False)
				continue

			filePath = os.path.join(downloadFolder, fileName)
			p = Process(target=Download, args=(filePath, fileUrl, self.parent.transQueue))
			p.start()
			self.parent.dProcess[(fileName, 'download')] = p
