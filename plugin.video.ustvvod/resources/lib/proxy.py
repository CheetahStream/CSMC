#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import BaseHTTPServer
import cookielib
import httplib
import os
import ustvpaths
import re
import simplejson
import socket
import sys
import time
import urllib
import urllib2
from dns.resolver import Resolver

HOST_NAME = 'localhost'
TIMEOUT = 50
PORT_NUMBER = int(sys.argv[1])

class MyHTTPConnection(httplib.HTTPConnection):
	_dnsproxy = []
	def connect(self):
		resolver = Resolver()
		resolver.nameservers = self._dnsproxy
		answer = resolver.query(self.host, 'A')
		self.host = answer.rrset.items[0].address
		self.sock = socket.create_connection((self.host, self.port))

class MyHTTPHandler(urllib2.HTTPHandler):
	_dnsproxy = []
	def http_open(self, req):
		MyHTTPConnection._dnsproxy = self._dnsproxy 
		return self.do_open(MyHTTPConnection, req)
		
class StoppableHTTPServer(BaseHTTPServer.HTTPServer):
	def serve_forever(self):
		self.stop = False
		while not self.stop:
			self.handle_request()
		print 'Server stopped'

class StoppableHttpRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_HEAD(self):
		self.writeHeaders()

	def do_GET(self):
		self.answer_request(1)

	def writeHeaders(self):
		self.send_response(200, "OK")
		self.send_header("Content-type", "text/plain")
		self.end_headers()

	def sendPage( self, type, body ):
		self.send_response(200, "OK")
		self.send_header("Content-type", type)
		self.send_header("Content-length", str(len(body)))
		self.end_headers()
		self.wfile.write(body)

	def answer_request(self, sendData):
		request_path = self.path[1:]
		request_path = re.sub(r'\?.*', '', request_path)
		if 'stop' in self.path:
			self.writeHeaders()
			self.server.stop = True
		elif 'key' in self.path:
			self.serveKey(request_path)
		elif 'm3u8' in self.path:
			self.serveM3U8(request_path)
		elif 'foxstation' in self.path:
			self.serveFoxStation(request_path, sendData)
		elif 'proxy' in self.path:
			self.serveProxy(request_path, sendData)

	def serveKey(self, filename):
		try:
			file = open(ustvpaths.KEYFILE.replace('play%s.key', filename), 'r')
			data = file.read()
			file.close()
			self.sendPage("html/plain", data)
		except IOError:
			self.send_error(404, 'File Not Found')
		return

	def serveM3U8(self, filename):
		try:
			file = open(ustvpaths.PLAYFILE.replace('play.m3u8', filename), 'r')
			data = file.read()
			file.close()
			self.sendPage("application/x-mpegURL", data)
		except IOError:
			self.send_error(404, 'File Not Found')
		return

	def serveFoxStation(self, path, data):
		i, path = path.split('/', 1)
		realpath = urllib.unquote_plus(path[11:])
		fURL = base64.b64decode(realpath)
		self.serveFile(fURL, data, cookienum = i)

	def serveProxy(self, path, data):
		realpath = urllib.unquote_plus(path)[6:]
		proxyconfig = realpath.split('/')[-1]
		proxy_object = simplejson.loads(proxyconfig)
		if int(proxy_object['connectiontype']) == 1:
			proxies = proxy_object['dns_proxy']
			MyHTTPHandler._dnsproxy = proxies
			handler = MyHTTPHandler
		elif int(proxy_object['connectiontype']) == 2:
			proxy = proxy_object['proxy']
			us_proxy = 'http://' + proxy['us_proxy'] + ':' + proxy['us_proxy_port']
			proxy_handler = urllib2.ProxyHandler({'http' : us_proxy})
			handler = proxy_handler
		realpath = realpath.replace('/' + proxyconfig, '')
		fURL = base64.b64decode(realpath)
		self.serveFile(fURL, data, handler)

	def serveFile(self, fURL, sendData, httphandler = None, cookienum = 0):
		cj = cookielib.LWPCookieJar(ustvpaths.COOKIE % str(cookienum))
		if httphandler is None:
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
		else:
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), httphandler)
		request = urllib2.Request(url = fURL)
		sheaders = self.decodeHeaderString(self.headers.headers)
		del sheaders['Host']
		sheaders['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0'
		for key in sheaders:
			opener.addheaders = [(key, sheaders[key])]
		if os.path.isfile(ustvpaths.COOKIE % str(cookienum)):
			cj.load(ignore_discard = True)
			cj.add_cookie_header(request)
		response = opener.open(request, timeout = TIMEOUT)
		self.send_response(200)
		headers = response.info()
		for key in headers:
			try:
				self.send_header(key, headers[key])
			except Exception, e:
				print "Exception: ", e
				pass
		self.end_headers()
		if (sendData):
			fileout = self.wfile
			try:
				try:
					buf = response.read(int(headers['content-length']))
					fileout.write(buf)
					fileout.close()
					response.close()
				except Exception, e:
					fileout.close()
					response.close()
					print "Exception: ", e
			except Exception, e:
				fileout.close()
				print "Exception: ", e
				return
		try:
			fileout.close()
		except:
			pass

	def decodeHeaderString(self, hs):
		di = {}
		hss = [item.rstrip() for item in hs]
		for line in hss:
			u = line.split(': ')
			try:
				di[u[0]] = u[1]
			except:
				pass
		return di

def runserver(server_class = StoppableHTTPServer, handler_class = StoppableHttpRequestHandler):
	server_address = (HOST_NAME, PORT_NUMBER)
	httpd = server_class(server_address, handler_class)
	httpd.serve_forever()

if __name__ == '__main__':
	runserver()
