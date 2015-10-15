#!/usr/bin/python
# -*- coding: utf-8 -*-
import cookielib
import httplib
import os
import ustvpaths
import socks
import socket
import ssl
try:
	import stem.process
except:
	pass
import time
import urllib
import urllib2
import xbmc
import xbmcaddon
from dns.resolver import Resolver

addon = xbmcaddon.Addon()

IPURL = 'http://icanhazip.com'
IPFILE = os.path.join(ustvpaths.DATAPATH,'ip.txt')
DNS_REFESH_DELAY = 10
TIMEOUT = 80

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

class SocksiPyConnection(httplib.HTTPConnection):
	def __init__(self, proxytype, proxyaddr, proxyport = None, rdns = True, username = None, password = None, *args, **kwargs):
		self.proxyargs = (proxytype, proxyaddr, proxyport, rdns, username, password)
		httplib.HTTPConnection.__init__(self, *args, **kwargs)

	def connect(self):
		self.sock = socks.socksocket()
		self.sock.setproxy(*self.proxyargs)
		if isinstance(self.timeout, float):
			self.sock.settimeout(self.timeout)
		self.sock.connect((self.host, self.port))

class SocksiPyConnectionS(httplib.HTTPSConnection):
	"""
	Missing part for getting https working https://github.com/Anorov/PySocks/blob/master/sockshandler.py
	"""
	def __init__(self, proxytype, proxyaddr, proxyport = None, rdns = True, username = None, password = None, *args, **kwargs):
		self.proxyargs = (proxytype, proxyaddr, proxyport, rdns, username, password)
		httplib.HTTPSConnection.__init__(self, *args, **kwargs)

	def connect(self):
		sock = socks.socksocket()
		sock.setproxy(*self.proxyargs)
		if type(self.timeout) in (int, float):
			sock.settimeout(self.timeout)
		sock.connect((self.host, self.port))
		self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file)

class SocksiPyHandler(urllib2.HTTPHandler, urllib2.HTTPSHandler):
	def __init__(self, *args, **kwargs):
		self.args = args
		self.kw = kwargs
		urllib2.HTTPHandler.__init__(self)

	def http_open(self, req):
		def build(host, port = None, strict = None, timeout = 0):
			conn = SocksiPyConnection(*self.args, host = host, port = port, strict = strict, timeout = timeout, **self.kw)
			return conn
		return self.do_open(build, req)

	def https_open(self, req):
		def build(host, port = None, strict = None, timeout = 0):    
			conn = SocksiPyConnectionS(*self.args, host = host, port = port, strict = strict, timeout = timeout, **self.kw)
			return conn
		return self.do_open(build, req)

class TorHandler():
	"""
	With some inspiration from https://github.com/benjkelley/torscraper
	"""
	def __init__(self):
		self.SocksPort = str(addon.getSetting('tor_socks_port'))
		self.ExitNodes = str(addon.getSetting('tor_exit_node'))
		self.tor_process = None

	def start_tor(self):
		try:
			tor_cmd = None
			config = {
						'AvoidDiskWrites' : '1',
						'ClientOnly' : '1',
						'DirReqStatistics' : '0',
						'ExcludeExitNodes' : '{be},{pl},{ca},{za},{vn},{uz},{ua},{tw},{tr},{th},{sk},{sg},{se},{sd},{sa},{ru},{ro},{pt},{ph},{pa},{nz},{np},{no},{my},{mx},{md},{lv},{lu},{kr},{jp},{it},{ir},{il},{ie},{id},{hr},{hk},{gr},{gi},{gb},{fi},{es},{ee},{dk},{cz},{cy},{cr},{co},{cn},{cl},{ci},{ch},{by},{br},{bg},{au},{at},{ar},{aq},{ao},{ae},{nl},{de},{fr}',
						'ExitNodes' : self.ExitNodes,
						'GeoIPExcludeUnknown' : '1',
						'NumEntryGuards' : '6',
						'SocksListenAddress' : '127.0.0.1',
						'SocksPort' : self.SocksPort,
						'StrictNodes' : '1'
				}
			if 'Tor' not in os.environ['PATH'] and os.name== 'nt':
				tor_cmd = os.environ['ProgramFiles'] + '\Tor\Tor.exe'
			if tor_cmd is None:
				self.tor_process = stem.process.launch_tor_with_config(
					config = config,
					init_msg_handler = self.print_bootstrap_lines,
					take_ownership = True,)
			else:
				self.tor_process = stem.process.launch_tor_with_config(
					config = config,
					init_msg_handler = self.print_bootstrap_lines,
					take_ownership = True,
					tor_cmd = tor_cmd)
			return True
		except OSError:
			return False

	def kill_tor(self):
		try:	
			self.tor_process.kill()
			return True
		except NameError as e:
			return False

	def print_bootstrap_lines(self, line):
		if 'Bootstrapped ' in line:
			print line + '\n'

def prepare_dns_proxy(cookie_handler):
	update_url = addon.getSetting('dns_update_url')
	if update_url:
		try:
			t = os.path.getmtime(IPFILE)
			now = time.time()
			elapsed = now - t
		except:
			elapsed = -1
		try:
			file = open(IPFILE, 'r')
			oldip = file.read()
			file.close()
		except:
			oldip = ''
		if elapsed > DNS_REFESH_DELAY or elapsed == -1:
			myip = getURL(IPURL, connectiontype = 0)
			if myip != oldip:
				oldip = myip
				getURL(update_url, connectiontype = 0)
		newfile = file = open(IPFILE, 'w')
		file.write(oldip)
		file.close()
	dnsproxy = []
	dnsproxy.append(addon.getSetting('dns_proxy'))
	dnsproxy.append(addon.getSetting('dns_proxy_2'))
	dnsproxy.append(addon.getSetting('dns_proxy_3'))
	MyHTTPHandler._dnsproxy = dnsproxy
	opener = urllib2.build_opener(MyHTTPHandler, cookie_handler)
	return opener

def prepare_us_proxy(cookie_handler):
	if (addon.getSetting('us_proxy_socks5') == 'true'):
		if ((addon.getSetting('us_proxy_pass') is not '') and (addon.getSetting('us_proxy_user') is not '')):
			print 'Using socks5 authenticated proxy: ' + addon.getSetting('us_proxy') + ':' + addon.getSetting('us_proxy_port')
			socks_handler = SocksiPyHandler(socks.PROXY_TYPE_SOCKS5, addon.getSetting('us_proxy'), int(addon.getSetting('us_proxy_port')), True, addon.getSetting('us_proxy_user'), addon.getSetting('us_proxy_pass'))
			opener = urllib2.build_opener(socks_handler, cookie_handler)
		else:
			print 'Using socks5 proxy: ' + addon.getSetting('us_proxy') + ':' + addon.getSetting('us_proxy_port')
			socks_handler = SocksiPyHandler(socks.PROXY_TYPE_SOCKS5, addon.getSetting('us_proxy'), int(addon.getSetting('us_proxy_port')), True)
			opener = urllib2.build_opener(socks_handler, cookie_handler)
	elif (addon.getSetting('us_proxy_socks5') == 'false'):
		us_proxy = 'http://' + addon.getSetting('us_proxy') + ':' + addon.getSetting('us_proxy_port')
		proxy_handler = urllib2.ProxyHandler({'http' : us_proxy})
		if ((addon.getSetting('us_proxy_pass') is not '') and (addon.getSetting('us_proxy_user') is not '')):
			print 'Using authenticated proxy: ' + us_proxy
			password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
			password_mgr.add_password(None, us_proxy, addon.getSetting('us_proxy_user'), addon.getSetting('us_proxy_pass'))
			proxy_auth_handler = urllib2.ProxyBasicAuthHandler(password_mgr)
			opener = urllib2.build_opener(proxy_handler, proxy_auth_handler, cookie_handler)
		else:
			print 'Using proxy: ' + us_proxy
			opener = urllib2.build_opener(proxy_handler, cookie_handler)
	return opener

def prepare_tor_proxy(cookie_handler):
	if addon.getSetting('tor_use_local') == 'true':
		tor_proxy = '127.0.0.1'
	else:
		tor_proxy = addon.getSetting('tor_proxy')
	print 'Using tor proxy at ' + tor_proxy + ':' + addon.getSetting('tor_socks_port') + ' with exit node: ' + addon.getSetting('tor_exit_node')
	socks_handler = SocksiPyHandler(socks.PROXY_TYPE_SOCKS5, tor_proxy, int(addon.getSetting('tor_socks_port')), True)
	opener = urllib2.build_opener(socks_handler, cookie_handler)
	return opener	

def getURL(url, values = None, header = {}, amf = False, savecookie = False, loadcookie = False, connectiontype = addon.getSetting('connectiontype'), cookiefile = 0):
	success = True
	while success:
		success = False;
		old_opener = urllib2._opener
		try:
			cj = cookielib.LWPCookieJar(ustvpaths.COOKIE % str(cookiefile))
			cookie_handler = urllib2.HTTPCookieProcessor(cj)
			if int(connectiontype) == 0:
				urllib2.install_opener(urllib2.build_opener(cookie_handler))
			if int(connectiontype) == 1:
				urllib2.install_opener(prepare_dns_proxy(cookie_handler))
			elif int(connectiontype) == 2:
				urllib2.install_opener(prepare_us_proxy(cookie_handler))
			elif int(connectiontype) == 3:
				handler = TorHandler()
				if ((addon.getSetting('tor_use_local') == 'true') and addon.getSetting('tor_as_service') == 'false'):
					if not handler.start_tor():
						print 'Error launching Tor. It may already be running.\n'
				urllib2.install_opener(prepare_tor_proxy(cookie_handler))
			print 'connection :: getURL :: url = ' + url
			if values is None:
				req = urllib2.Request(bytes(url))
			else:
				if amf == False:
					data = urllib.urlencode(values)
				elif amf == True:
					data = values
				req = urllib2.Request(bytes(url), data)
			header.update({'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0'})
			if connectiontype == 2:
				header.update({'X-Forwarded-For' : addon.getSetting('us_proxy')})
			elif int(connectiontype) == 1:
				header.update({'X-Forwarded-For' : addon.getSetting('dns_proxy')})
			for key, value in header.iteritems():
				req.add_header(key, value)
			if loadcookie is True:
				try:
					cj.load(ignore_discard = True)
					cj.add_cookie_header(req)
				except:
					print 'Cookie Loading Error'
					pass
			response = urllib2.urlopen(req, timeout = TIMEOUT)
			link = response.read()
			if (savecookie is True) and (len(cj) > 0):
				try:
					cj.save(ignore_discard = True)
				except:
					print 'Cookie Saving Error'
					success = True
					pass
			elif (savecookie is True) and (len(cj) == 0):
				success = True
			response.close()
			if ((int(connectiontype) == 3) and (addon.getSetting('tor_use_local') == 'true') and (addon.getSetting('tor_as_service') == 'false')):
				if not handler.kill_tor(): 
					print 'Error killing Tor process! It may still be running.\n' 
				else: 
					print 'Tor instance killed!\n'
		except urllib2.HTTPError, error:
			success = True
			xbmc.log('HTTP Error reason: ' + str(error), xbmc.LOGINFO)
			return error.read()
		except Exception, e:
			print "URL Error:: ", e
		else:
			urllib2.install_opener(old_opener)
	return link

def getRedirect(url, values = None , header = {}, connectiontype = addon.getSetting('connectiontype')):
	old_opener = urllib2._opener
	try:
		cj = cookielib.LWPCookieJar(ustvpaths.COOKIE)
		cookie_handler = urllib2.HTTPCookieProcessor(cj)
		if int(connectiontype) == 1:
			urllib2.install_opener(prepare_dns_proxy(cookie_handler))
		elif int(connectiontype) == 2:
			urllib2.install_opener(prepare_us_proxy(cookie_handler))
		elif int(connectiontype) == 3:
			handler = TorHandler()
			if ((addon.getSetting('tor_use_local') == 'true') and addon.getSetting('tor_as_service') == 'false'):
				if not handler.start_tor():
					print 'Error launching Tor. It may already be running.\n'
			urllib2.install_opener(prepare_tor_proxy(cookie_handler))
		print 'connection :: getRedirect :: url = ' + url
		if values is None:
			req = urllib2.Request(bytes(url))
		else:
			data = urllib.urlencode(values)
			req = urllib2.Request(bytes(url), data)
		header.update({'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0'})
		if int(connectiontype) == 2:
			header.update({'X-Forwarded-For' : addon.getSetting('us_proxy')})
		elif int(connectiontype) == 1:
			header.update({'X-Forwarded-For' : addon.getSetting('dns_proxy')})
		for key, value in header.iteritems():
			req.add_header(key, value)
		response = urllib2.urlopen(req, timeout = TIMEOUT)
		finalurl = response.geturl()
		response.close()
		if ((int(connectiontype) == 3) and (addon.getSetting('tor_use_local') == 'true') and (addon.getSetting('tor_as_service') == 'false')):
			if not handler.kill_tor(): 
				print 'Error killing Tor process! It may still be running.\n' 
			else: 
				print 'Tor instance killed!\n'
	except urllib2.HTTPError, error:
		print 'HTTP Error reason: ', error
		return error.read()
	except Exception, e:
		print "Error: ", e
	else:
		urllib2.install_opener(old_opener)
		return finalurl
