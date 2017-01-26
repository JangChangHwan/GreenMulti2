# coding: utf-8

import httplib, mimetypes
import os
from bs4 import BeautifulSoup as bs
from MultipartPostHandler import MultipartPostHandler
import re


class Http(object):

	host = 'han.kbuwel.or.kr'
	cookie = ''
	html = ''
	soup = None
	response = None

	def __init__(self, parent):
		self.parent = parent
		self.cookies = self.parent.cookies


	def Get(self, selector, headers={}):
		headers['Content-Type'] = 'text/html'
		headers['Cookie'] = self.cookies
		conn = httplib.HTTPConnection(self.host)
		conn.request('GET', selector, headers=headers)
		self.response = conn.getresponse()
		self.Soup(self.response)


	def Post(self, selector, fields):
		fieldList = fields.items() if isinstance(fields, dict) else fields
		fieldList = [(k, v.encode('utf-8', 'ignore')) for k, v in fieldList]
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
		self.Soup(self.response)


	def Soup(self, res, encoding='utf-8'):
		html = res.read()
		self.html = unicode(html, encoding)
		self.soup = bs(html, 'html.parser')


	def Url(self, url):

		if url.startswith('./'):
			return '/bbs' + url[1:]
		elif url.startswith('board.php'):
			return '/bbs/' + url
		else:
			return url



	def UrlString(self, s):
		data = repr(s.encode('utf-8'))[1:-1].replace(r'\x', '%')
		data = data.replace('&', '%26')
		data = data.replace('=', '%3D')
		data = data.replace(':', '%3A')
		data = data.replace('/', '%2F')
		return data


	def Upload(self, selector, d):
		wr_subject = d.pop('wr_subject')
		wr_content = d.pop('wr_content')
		bf_file = d.pop('bf_file[]')
		if bf_file:
			files = [('bf_file[]', bf_file)]
		else:
			params = urllib.urlencode(d)
			params += '&wr_subject=' + self.UrlString(wr_subject) + '&wr_content=' + self.UrlString(wr_content)
			self.Post(selector, params)
			return 'Post'

		fields = d.items()
		fields.append(('wr_subject', wr_subject.encode('utf-8')))
		fields.append(('wr_content', wr_content.encode('utf-8')))
		files = [('bf_file[]', open(bf_file, 'rb'))]

		self.MultipartPost(selector, fields, files)


	def MultipartPost(self, selector, fields, files):
		fieldList = fields.items() if isinstance(fields, dict) else fields
		fieldList = [(k, v.encode('utf-8', 'ignore')) for k, v in fieldList]
		fileList = files.items() if isinstance(files, dict) else files
		boundary, body = MultipartPostHandler.multipart_encode(fieldList, fileList)
		content_type = 'multipart/form-data; boundary=%s' % boundary

		h = httplib.HTTPConnection(self.host)
		h.putrequest('POST', selector)
		h.putheader('content-type', content_type)
		h.putheader('content-length', str(len(body)))
		h.putheader('Cookie', self.cookies)
		h.endheaders()
		h.send(body)
		self.response = h.getresponse()
		self.Soup(self.response)


	def GetTextFromTag(self, soup_tag):
		s = unicode(soup_tag)
		texts = re.findall('>([^<>]*)<', s)
		text = '\r\n'.join(texts)
		text = text.replace('&nbsp;', ' ')
		return text

