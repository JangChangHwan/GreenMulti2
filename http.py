# coding: utf-8

import urllib, httplib, mimetypes
from bs4 import BeautifulSoup as bs

class Http(object):

	host = ''
	cookie = ''
	html = ''
	soup = None
	response = None

	def __init__(self, host, cookie):
		self.host = host
		self.cookie = cookie

	def Get(self, selector, headers={}):
		contentType, xxx = mimetypes.guess_type(selector)
		if contentType is None: contentType = 'text/html'
		headers['Content-Type'] = contentType
		headers['Cookie'] = self.cookie
		conn = httplib.HTTPConnection(self.host)
		conn.request('GET', selector, headers=headers)
		self.response = conn.getresponse()
		self.Soup(self.response)


	def Post(self, selector, body, headers={}):
		headers['Content-Type'] = 'application/x-www-form-urlencoded'
		headers['Content-Length'] = str(len(body))
		headers['Cookie'] = self.cookie
		conn = httplib.HTTPConnection(self.host)
		conn.request('POST', selector, body, headers)
		self.response = conn.getresponse()
		self.Soup(self.response)


	def Soup(self, res, encoding='utf-8'):
		html = res.read()
		self.html = unicode(html, encoding)
		self.soup = bs(html, 'html.parser')

