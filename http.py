# coding: utf-8

import httplib, mimetypes, mimetools
import os
from multiprocessing import Process, Queue
from bs4 import BeautifulSoup as bs
from util import *
import re
import time
from winsound import Beep
from win32com.client import Dispatch
import zipfile
from cStringIO import StringIO
import stat



class Http(object):

	cookies = ''
	html = ''
	soup = None
	response = None


	def __init__(self, parent=None):
		self.parent = parent
		if self.parent is not None:
			self.cookies = self.parent.cookies


	def Get(self, selector, soup=True, headers={}):
		(host, selector) = self.Url(selector)
		headers['Cookie'] = self.cookies
		conn = httplib.HTTPConnection(host)
		conn.request('GET', selector, headers=headers)
		self.response = conn.getresponse()
		if soup: self.Soup(self.response)


	def Post(self, selector, fields, soup=True):
		(host, selector) = self.Url(selector)
		fieldList = []
		for k, v in fields.items():
			if type(v) == unicode: v = v.encode('utf-8')
			fieldList.append((k, v))

		boundary, body = self.SimpleEncoder(fieldList)
		content_type = 'multipart/form-data; boundary=%s' % boundary

		h = httplib.HTTPConnection(host)
		h.putrequest('POST', selector)
		h.putheader('content-type', content_type)
		h.putheader('content-length', str(len(body)))
		h.putheader('Cookie', self.cookies)
		h.endheaders()
		h.send(body)
		self.response = h.getresponse()
		if soup: self.Soup(self.response)


	def Soup(self, res, encoding='utf-8'):
		self.html = self.soup = ''
		try:
			html = res.read()
			self.html = unicode(html, encoding)
			self.soup = bs(html, 'html.parser')
		except:
			self.soup = ''


	def Url(self, url):
		"return (host, selector)"

		if url.startswith('./'):
			return ('web.kbuwel.or.kr', '/bbs' + url[1:])
		elif url.startswith('board.php') or url.startswith('download.php'):
			return ('web.kbuwel.or.kr', '/bbs/' + url)
		elif url.startswith('http://web.kbuwel.or.kr'):
			return ('web.kbuwel.or.kr', url.replace('http://web.kbuwel.or.kr', ''))
		elif url.startswith('http://bigfile.kbuwel.or.kr'):
			return ('bigfile.kbuwel.or.kr', url.replace('http://bigfile.kbuwel.or.kr', ''))

		else:
			return ('web.kbuwel.or.kr', url)


	def GetTextFromTag(self, soup_tag):
		s = unicode(soup_tag)
		texts = re.findall('>([^<>]*)<', s)
		texts = [s.strip() for s in texts if re.search(u'[\\w가-힣]', s) is not None]
		text = '\r\n'.join(texts)
		text = text.replace('&nbsp;', '')
		return text


	def SimpleEncoder(self, vars):
		boundary = mimetools.choose_boundary()
		buffer = StringIO()

		for(key, value) in vars:
			buffer.write('--%s\r\n' % boundary)
			buffer.write('Content-Disposition: form-data; name="%s"' % key)
			if value is None:
				value = ""
			buffer.write('\r\n\r\n' + value + '\r\n')
		buffer.write('--' + boundary + '--\r\n')
		buffer = buffer.getvalue()
		return (boundary, buffer)



	def MultipartEncoder(self, vars, files):
		boundary = mimetools.choose_boundary()
		buffer = StringIO()

		for(key, value) in vars:
			buffer.write('--%s\r\n' % boundary)
			buffer.write('Content-Disposition: form-data; name="%s"' % key)
			if value is None:
				value = ""
			buffer.write('\r\n\r\n' + value + '\r\n')

		(key, path) = files
		fd = open(path, 'rb')
		file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
		filename = fd.name.split('/')[-1]
		fd.close()

		contenttype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
		buffer.write('--%s\r\n' % boundary)
		if type(filename) == unicode: filename = filename.encode('utf-8', 'ignore')
		buffer.write('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename))
		buffer.write('Content-Type: %s\r\n' % contenttype)
		buffer.write('Content-Length: %s\r\n' % file_size)
		buffer.write('\r\n' )

		buffer = buffer.getvalue()
		return (boundary, buffer)







class Download(Process, Http, Utility):
	def __init__(self, filePath, url, q, pNum):
		Process.__init__(self)
		Utility.__init__(self)
		Http.__init__(self, None)
		self.filePath = filePath
		self.url = url
		self.q = q
		self.pNum = pNum

		r = self.LoginCheck()
		if r: 
			self.Play('down_start.wav', async=False)
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
			if self.response.getheader('Location'):
				self.cookies = self.response.getheader('set-cookie')
				return True
			return False
		except:
			return False


	def run(self):

		self.Get(self.url, soup=False)
		totalSize = self.response.length
		if os.path.exists(self.filePath) and os.path.getsize(self.filePath) == totalSize:
			self.Play('pass.wav', async=False)
			return

		downSize = 0
		chunck = 1024 * 1024
		startTime = time.time()
		fileName = os.path.basename(self.filePath)
		f = open(self.filePath, 'wb')
		self.q.put((self.pNum, fileName, totalSize, 0, 0))

		while True:
			part = self.response.read(chunck)
			f.write(part)
			downSize += len(part)
			elapsedTime = time.time() - startTime
			self.q.put((self.pNum, fileName, totalSize, downSize, elapsedTime))
			if self.response.length == 0: break

		f.close()
		self.q.put((self.pNum, fileName, totalSize, totalSize, elapsedTime))

		if self.ReadReg('autodaisy'):
			self.ConvertDaisy(self.filePath)

		time.sleep(1)
		self.Play('down.wav', async=False)

	def ConvertDaisy(self, filePath):
		if not filePath.lower().endswith('.zip'): return
		try:
			zfile = zipfile.ZipFile(filePath, 'r')
			for fileName in zfile.namelist():
				# .xml이 아니면 패스
				if not fileName.lower().endswith('.xml'): continue
				# .xml이면 파싱하여 데이지 파일인지 검사
				xml = zfile.read(fileName)
				soup = bs(xml, 'html.parser')
				m = soup.find('dtbook', xmlns=re.compile(r'^http://www.daisy.org/'))
				if m is None: continue
				# 문자 추출
				paras = soup('p')
				if paras is None: continue
				txt = u'\r\n'.join([p.getText() for p in paras])
				txt = re.sub(r'[ ]{2,}', ' ', txt)
				destPath = filePath[:-4] + '.txt'
				with open(destPath, 'wb') as f:
					f.write(txt.encode('utf-16', 'ignore'))
					zfile.close()
					os.remove(filePath)
				break
		except:
			self.Play('error.wav', async=False)



class Upload(Process, Utility, Http):
	def __init__(self, selector, fields, files, q, pNum):
		"fields : dict, files : list [file, path]"
		Process.__init__(self)
		Utility.__init__(self)
		Http.__init__(self, None)
		self.selector = selector
		self.fields = fields
		self.files = files
		self.q = q
		self.pNum = pNum
		if self.LoginCheck(): self.run()

	def run(self):
		(host, self.selector) = self.Url(self.selector)
		fieldList = []
		for k, v in self.fields.items():
			if type(v) == unicode: v = v.encode('utf-8')
			fieldList.append((k, v))
		fileList = self.files

		(boundary, head) = self.MultipartEncoder(fieldList, fileList)

		fileName = os.path.basename(fileList[1])
		fileSize = os.path.getsize(fileList[1])
		content_type = 'multipart/form-data; boundary=%s' % boundary
		tail = '\r\n--' + boundary + '--\r\n'

		blockSize = 1024 * 1024
		upSize = 0
		totalSize = len(head) + fileSize + len(tail)
		startTime = time.time()

		h = httplib.HTTPConnection(host)
		h.putrequest('POST', self.selector)
		h.putheader('content-type', content_type)
		h.putheader('content-length', str(totalSize))
		h.putheader('Cookie', self.cookies)
		h.endheaders()

		self.Play('down_start.wav')
		self.q.put((self.pNum, fileName, fileSize, 0, 0))
		h.send(head)

		fp = open(fileList[1], 'rb')
		fp.seek(0)
		while True:
			part = fp.read(blockSize)
			if not part: break

			h.send(part)
			elapsedTime = time.time() - startTime
			upSize += len(part)
			self.q.put((self.pNum, fileName, fileSize, upSize, elapsedTime))

		# tail을 보낸다.
		h.send(tail)
		elapsedTime = time.time() - startTime
		self.q.put((self.pNum, fileName, fileSize, fileSize, elapsedTime))
		fp.close()
		self.response = h.getresponse()

		time.sleep(1)
		self.Play('up.wav', async=False)



	def LoginCheck(self):
		try:
			kbuid = self.Decrypt(self.ReadReg('kbuid'))
			kbupw = self.Decrypt(self.ReadReg('kbupw'))
			if not kbuid or not kbupw: return False

			params = {'url': 'http%3A%2F%2Fweb.kbuwel.or.kr', 'mb_id': kbuid, 'mb_password': kbupw}
			self.Post('/bbs/login_check.php', params, soup=False)
			if self.response.getheader('Location'):
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

		fileLinks = self.soup('a', href=re.compile(r'download.php|http://bigfile\.kbuwel\.or\.kr'))
		if fileLinks is not None:
			for link in fileLinks:
				descript = ' '.join(link.getText().split())
				m = re.search(r'^(.+) \(\d+(,\d{3})*(\.\d+)?(M|K|byte)\)$', descript)
				if m is not None:
					self.files[m.group(1)] = (descript, link['href'])

		if not self.files: return

		for fileName, (descript, fileUrl) in self.files.items():
			stop = False
			for (pNum, transferFile) in self.parent.dFileInfo.keys():
				if pNum > 0 and fileName == transferFile: stop = True
			if stop == True:
				self.Play('pass.wav', async=False)
				continue

			filePath = os.path.join(downloadFolder, fileName)
			self.parent.processNumber += 1
			pNum = str(self.parent.processNumber)
			p = Process(target=Download, args=(filePath, fileUrl, self.parent.transQueue, pNum))
			p.start()
			self.parent.dProcess[(pNum, fileName)] = p

