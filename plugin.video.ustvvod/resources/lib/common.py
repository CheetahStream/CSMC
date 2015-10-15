#!/usr/bin/python
# -*- coding: utf-8 -*-
import connection
import database
import base64
import os
import ustvpaths
import re
import simplejson
import sys
import time
import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

try:
	import StorageServer
except:
	import storageserverdummy as StorageServer

addon = xbmcaddon.Addon()
pluginHandle = int(sys.argv[1])

TVDBAPIKEY = '03B8C17597ECBD64'
TVDBURL = 'http://thetvdb.com'
TVDBBANNERS = 'http://thetvdb.com/banners/'
TVDBSERIESLOOKUP = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='

cache = StorageServer.StorageServer("ustvvodxxyyyy", 0) 

class XBMCPlayer( xbmc.Player ):
	_counter = 0
	_segments = 1
	_segments_array = []
	_subtitles_Enabled = False
	_subtitles_Type = "SRT"
	_localHTTPServer = True

	def __init__( self, *args, **kwargs  ):
		xbmc.Player.__init__( self )
		self.is_active = True
	
	def onPlayBackSpeedChanged( self, speed ):
		print "**************************** Speed Event *****************************" + str(speed)
	
	def onPlayBackStarted( self ):
		# Will be called when xbmc starts playing a segment
		print "**************************** Play Event *****************************"
		play_time = self.getTime()
		if len(self._segments_array) > 1:
			self._segments = len(self._segments_array)
		if len(self._segments_array) > 1:
			total = 0
			index = -1
			for i, duration in enumerate(self._segments_array):
				total = total + int(duration)
				if play_time < total and index == -1:
					index = i
			self._counter = index + 1
		else:
			self._counter = 1
		
		if self._subtitles_Enabled:
			if self._segments > 1:
				if self._subtitles_Type == "SRT":
					self.setSubtitles(os.path.join(ustvpaths.DATAPATH, 'subtitle-%s.srt' % str(self._counter)))
				else:
					self.setSubtitles(os.path.join(ustvpaths.DATAPATH, 'subtitle-%s.smi' % str(self._counter)))
			else:
				if self._subtitles_Type == "SRT":
					self.setSubtitles(ustvpaths.SUBTITLE)
				else:
					self.setSubtitles(ustvpaths.SUBTITLESMI)

	def onPlayBackEnded( self ):
		# Will be called when xbmc stops playing a segment
		print "**************************** End Event *****************************"
		if self._counter == self._segments:
			print "**************************** End Event -- Stopping Server *****************************"
			self.is_active = False
			if self._localHTTPServer:
				connection.getURL('http://localhost:12345/stop', connectiontype = 0)

	def onPlayBackStopped( self ):
		# Will be called when user stops xbmc playing a file
		print "**************************** Stop Event -- Stopping Server *****************************"
		self.is_active = False
		if self._localHTTPServer:
			connection.getURL('http://localhost:12345/stop', connectiontype = 0)

	def sleep(self, s):
		xbmc.sleep(s) 

class _Info:
	def __init__(self, s):
		args = urllib.unquote_plus(s).split(' , ')
		for x in args:
			try:
				(k, v) = x.split('=', 1)
				setattr(self, k, v.strip('"\''))
			except:
				pass
		if not hasattr(self, 'url'):
			setattr(self, 'url', '')

args = _Info(sys.argv[2][1:].replace('&', ' , '))
network_module_cache = {}

def use_proxy():
	xbmc_version = xbmc.getInfoLabel( "System.BuildVersion" )
	setting = int(addon.getSetting('use_builtin_ssl'))
	proxy = True
	if setting == 1:
		proxy = False
	elif setting == 0 and int(xbmc_version[:2]) >= 13:
		proxy = False
	return proxy
	
def season_list():
	try:
		seasons = get_seasons(args.mode, args.sitemode, args.url)
		for season in seasons:
			section_title,  site, sitemode, url, locked, unlocked = season
			add_directory(smart_utf8(section_title),  site, sitemode, url, locked = locked, unlocked = unlocked)
		set_view('seasons')
	except Exception, e:
		print "Error getting seasons", e

def get_seasons(network_name, site_mode, url = args.url):
	network = get_network(network_name)
	seasons = cache.cacheFunction(getattr(network, site_mode) , url)
	return seasons
	
def enrich_infolabels(infolabels, expires_date = None, date_format = None, epoch = False):
	try:
		if (expires_date is not None and expires_date != '') or epoch:
			if date_format:
				expires_date = format_date(expires_date, date_format, '%d/%m/%Y')
			elif epoch:
				expires_date = format_date(epoch = epoch)
			plot =  'Expires: ' + smart_utf8(expires_date) + '\n' + smart_utf8(infolabels['plot'])
			infolabels['plot'] = plot
			
			
	except:
		pass
	try:
		infolabels['mpaa'] = infolabels['mpaa'].upper()
	except:
		pass
	try:
		infolabels['genre'] = infolabels['genre'].title()
	except:
		pass
	return infolabels
	
def episode_list():
	try:
		tvdb_id = args.tvdb_id 
	except:
		tvdb_id = None
	episodes = get_episodes(args.mode, args.sitemode, args.url, tvdb_id)
	for episode in episodes:
		u, episode_name, episode_thumb, infoLabels, qmode, HD, media_type = episode
		try:
			add_video(u, episode_name, episode_thumb, infoLabels = infoLabels, quality_mode  = qmode, HD = HD)
		except Exception, e:
			print "Error adding video", e, episode
	set_view('episodes')


def get_episodes(network_name, site_mode, url = args.url, tvdb_id = None):
	network = get_network(network_name)
	episodes = cache.cacheFunction(getattr(network, site_mode) , url)
	newepisodes = []
	series_tree = None 
	try:
		tvdb_setting = int(addon.getSetting('strict_names'))
	except:
		tvdb_setting = 0
	if tvdb_id is not None and tvdb_setting !=1:
		for episode in episodes:
			try:
				u, episode_name, episode_thumb, infoLabels, qmode, HD, media_type = episode
				if ('episode' not in infoLabels.keys()  or infoLabels['episode'] == -1 or  'season' not in infoLabels.keys() or infoLabels['season'] == -1) and media_type == 'Full Episode':
					if series_tree is None:
						series_url = TVDBURL + ('/api/%s/series/%s/all/en.xml' % (TVDBAPIKEY, tvdb_id))
						series_xml = connection.getURL(series_url, connectiontype = 0)
						series_tree = BeautifulSoup(series_xml, 'html.parser', parse_only = SoupStrainer('episode'))
					try:
						episode_item = series_tree.find('episodename', text = episode_name).parent
					except:
						episode_item = series_tree.find('episodename', text = re.compile(episode_name.replace(' ', ' ?').replace('.', '\.').replace('The ', '(The )?').replace('.', '.,?').replace('-', '-?').replace(',', ',?|( and)?'), re.I)).parent
					infoLabels['episode'] =  int(episode_item.episodenumber.string)
					infoLabels['season'] =  int(episode_item.seasonnumber.string)
			except:
				pass
			newepisodes.append((u, episode_name, episode_thumb, infoLabels, qmode, HD, media_type))
	else:
		newepisodes = episodes
	return newepisodes

def root_list(network_name):
	"""
	Loads data from master list
	"""
	network = get_network(network_name)
	dialog = xbmcgui.DialogProgress()
	dialog.create(smart_utf8(addon.getLocalizedString(39016)))
	current = 0
	rootlist = []
	network_name = network.NAME
	dialog.update(0, smart_utf8(addon.getLocalizedString(39017)) + network.NAME, smart_utf8(addon.getLocalizedString(39018)))
	showdata = network.masterlist()
	total_shows = len(showdata)
	current_show = 0
	for show in showdata:
		percent = int( (float(current_show) / total_shows))
		dialog.update(percent, smart_utf8(addon.getLocalizedString(39017)) + network.NAME, smart_utf8(addon.getLocalizedString(39005)) + show[0])
		current_show += 1
		if (dialog.iscanceled()):
			return False
	for show in showdata:
		try:
			add_show(show[0], show[1], show[2], show[3], sitedata = show[4])
		except:
			add_show(show[0], show[1], show[2], show[3])
	set_view('root')

def get_network(module_name):
	""" 
	Loads network using a quick and dirty plugin method
	"""
	if module_name in network_module_cache:
		return network_module_cache[module_name]
	print "!!! plugin loading of site : " + module_name 
	try:
		module = __import__(module_name)
		if hasattr(module, 'SITE') and hasattr(module, 'masterlist'):
			if not hasattr(module, 'NAME'):
				setattr(module, 'NAME', module_name)
			if not hasattr(module, 'DESCRIPTION'):
				setattr(module, 'DESCRIPTION', module_name)
			network_module_cache[module_name] = module
			return module
		else:
			print "error loading site, SITE and masterlist must be defined!"
	except Exception, e:
		print str(e)

def get_networks():
	""" 
	Loads all networks using a quick and dirty plugin method
	"""
	networks = []
	for filename in os.listdir(ustvpaths.STATIONPATH):
		if filename.endswith('.py'):
			module_name = os.path.splitext(filename)[0]
			network = get_network(module_name)
			if network:
				networks.append(network)
	return networks

def get_quality_method():
	val = addon.getSetting('qualityMethod')
	if val == "Lowest":
		return "LOW"
	return "HIGH"

def set_view(type = 'root'):
	confluence_views = [500,501,50,503,504,508,51]
	if type == 'root':
		xbmcplugin.setContent(pluginHandle, 'movies')
	elif type == 'seasons':
		xbmcplugin.setContent(pluginHandle, 'movies')
	else:
		if type == 'tvshows':
			xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		xbmcplugin.setContent(pluginHandle, type)
	if addon.getSetting('viewenable') == 'true':
		view = int(addon.getSetting(type + 'view'))
		xbmc.executebuiltin('Container.SetViewMode(' + str(confluence_views[view]) + ')')

def format_date(inputDate = '', inputFormat = '', outputFormat = '%Y-%m-%d', epoch = False):
	if epoch:
		return time.strftime(outputFormat, time.localtime(epoch))
	else:
		return time.strftime(outputFormat, time.strptime(inputDate, inputFormat))

def convert_to_timezone(inputDate = '', inputFormat = '', timezone = 0, epoch = False):
	if epoch:
		return epoch + (timezone*3600 + time.timezone)
	else:
		return time.strftime(inputFormat, time.localtime(time.mktime(time.strptime(inputDate, inputFormat)) + (timezone*3600 + time.timezone)))

def format_seconds(timestring):
	if timestring[0] == ':':
		timestring = '0' + timestring
	timestring2 = 0
	if len(timestring.split(':')) == 1:
		ftr = [1]
	elif len(timestring.split(':')) == 2:
		ftr = [60,1]
	else:
		ftr = [3600,60,1]
	timestring2 = sum([a*b for a,b in zip(ftr, map(int,timestring.split(':')))])
	return int(timestring2)

def smart_unicode(s):
	"""credit : sfaxman"""
	if not s:
		return ''
	try:
		if not isinstance(s, basestring):
			if hasattr(s, '__unicode__'):
				s = unicode(s)
			else:
				s = unicode(str(s), 'UTF-8')
		elif not isinstance(s, unicode):
			s = unicode(s, 'UTF-8')
	except:
		if not isinstance(s, basestring):
			if hasattr(s, '__unicode__'):
				s = unicode(s)
			else:
				s = unicode(str(s), 'ISO-8859-1')
		elif not isinstance(s, unicode):
			s = unicode(s, 'ISO-8859-1')
	return s

def smart_utf8(s):
	return smart_unicode(s).encode('utf-8')

def replace_signs(text):
	dic = {	'â€™'	: '\'',
			'�'		: '\'',
			'â„¢' 	: '',
			'â€œ'	: '',
			'â€"'	: '-',
			'â€“'	: '-',
			'â€”'	: '-',
			'Â²'	: '²',
			'â€�'	: '"',
			'â€˜N'	: '\'N',
			'Ã¡'	: 'á',
			'Ã©'	: 'é',
			'â€˜'	: '\'',
			'á'		: ' ',
			'é'		: 'e'}
	for i, j in dic.iteritems():
		text = smart_utf8(text).replace(i, j).strip()
	return text

def refresh_db():
	if not os.path.isfile(ustvpaths.DBFILE):
		database.create_db()
	networks = get_networks()
	dialog = xbmcgui.DialogProgress()
	dialog.create(smart_utf8(addon.getLocalizedString(39016)))
	total_stations = len(networks)
	current = 0
	increment = 100.0 / total_stations
	all_shows = []
	for network in networks:
		network_name = network.NAME
		if addon.getSetting(network.SITE) == 'true':
			percent = int(increment * current)
			dialog.update(percent, smart_utf8(addon.getLocalizedString(39017)) + network.NAME, smart_utf8(addon.getLocalizedString(39018)))
			showdata = network.masterlist()
			for show in showdata:
				try:
					series_title, mode, submode, url = show
				except:
					series_title, mode, submode, url, siteplot = show
				all_shows.append((smart_unicode(series_title.lower().strip()), smart_unicode(mode), smart_unicode(submode)))
			total_shows = len(showdata)
			current_show = 0
			for show in showdata:
				percent = int((increment * current) + (float(current_show) / total_shows) * increment)
				dialog.update(percent, smart_utf8(addon.getLocalizedString(39017)) + network.NAME, smart_utf8(addon.getLocalizedString(39005)) + show[0])
				get_serie(show[0], show[1], show[2], show[3], forceRefresh = False)
				current_show += 1
				if (dialog.iscanceled()):
					return False
		current += 1
	command = 'select tvdb_series_title , series_title, mode, submode, url from shows order by series_title'
	shows = database.execute_command(command, fetchall = True) 
	for show in shows:
		tvdb_series_title, series_title, mode, submode, url = show
		if ((smart_unicode(series_title.lower().strip()),smart_unicode(mode), smart_unicode(submode)) not in all_shows and (smart_unicode(tvdb_series_title.lower().strip()),smart_unicode(mode), smart_unicode(submode)) not in all_shows):
			command = 'delete from shows where series_title = ? and mode = ? and submode = ? and url = ?;'
			values = (series_title, mode, submode, url)
			print "Deleting - " + series_title + " " + mode + " " + submode + " " + url
			database.execute_command(command, values, fetchone = True, commit = True)

def get_skelton_series(series_title, mode, submode, url):
	return [series_title, mode,submode, url, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, True, False, False, series_title]

def get_serie(series_title, mode, submode, url, forceRefresh = False, sitedata = None):
	command = 'select * from shows where lower(series_title) = ? and mode = ? and submode = ?;'
	values = (series_title.lower(), mode, submode)
	checkdata = database.execute_command(command, values, fetchone = True)
	empty_values = get_skelton_series(series_title, mode, submode, url)
	try:
		siteplot = sitedata['plot']
	except:
		siteplot = None
	try:
		tvdb_setting = int(addon.getSetting('strict_names'))
	except:
		tvdb_setting = 0
	if checkdata and not forceRefresh and checkdata[24]  is not None and checkdata[20] != 'None':
		if smart_unicode(checkdata[3]) != smart_unicode(url): 
			command = 'update shows set url = ? where tvdb_series_title = ? and mode = ? and submode = ?;'
			values = (url, series_title, mode, submode)
			database.execute_command(command, values, commit = True)
			command = 'select * from shows where lower(series_title) = ? and mode = ? and submode = ?;'
			values = (series_title.lower(), mode, submode)
			return database.execute_command(command, values, fetchone = True)
		elif checkdata[15] is None and siteplot  is not None:
			command = 'update shows set plot = ? where series_title = ? and mode = ? and submode = ?;'
			values = (siteplot, series_title, mode, submode)
			database.execute_command(command, values, commit = True)
			command = 'select * from shows where lower(series_title) = ? and mode = ? and submode = ?;'
			values = (series_title.lower(), mode, submode)
			return database.execute_command(command, values, fetchone = True)
		else:
			return checkdata
	elif tvdb_setting != 1 or forceRefresh:
		network = get_network(mode)
		try:
			tvdb_data = get_tvdb_series(series_title, manualSearch = forceRefresh, site = network.NAME, network_alias = network.ALIAS)
		except:
			tvdb_data = get_tvdb_series(series_title, manualSearch = forceRefresh, site = network.NAME)
		if tvdb_data:
			tvdb_id, imdb_id, tvdbbanner, tvdbposter, tvdbfanart, first_aired, date, year, actors, genres, network, plot, runtime, rating, airs_dayofweek, airs_time, status, tvdb_series_title = tvdb_data
			values = [series_title, mode, submode, url, tvdb_id, imdb_id, tvdbbanner, tvdbposter, tvdbfanart, first_aired, date, year, actors, genres, network, plot, runtime, rating, airs_dayofweek, airs_time, status, True, False, False, tvdb_series_title]
		else:
			values = empty_values
		command = 'insert or replace into shows values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
		database.execute_command(command, values, commit = True)
		command = 'select * from shows where series_title = ? and mode = ? and submode = ?;'
		values = (series_title, mode, submode)
		return database.execute_command(command, values, fetchone = True)
	else:
		command = 'insert or replace into shows values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
		empty_values[20] = 'None'
		database.execute_command(command, empty_values, commit = True)
		return empty_values

def get_series_id(seriesdata, seriesname, site = '', allowManual = False, network_alias = []):
	shows = BeautifulSoup(seriesdata, 'html.parser').find_all('series')
	for show_item in shows:
		if  '**' in show_item.seriesname.string:
			show_item.clear()
	show_list = []
	punctuation = ":'!,. -\"?s"
	exclude = set(punctuation)
	tvdb_show_name = shows[0].seriesname.string.lower()
	tvdb_show_name = tvdb_show_name.replace('usa', '')
	tvdb_show_name = tvdb_show_name.replace(shows[0].network.string.lower(), '').replace(site.lower(),'').replace('on','').strip()
	tvdb_show_name = tvdb_show_name.replace('the', '').replace('show','').strip()
	lookup = seriesname.lower().replace('usa', '').replace(u"\u00AE", '')
	lookup = lookup.replace('the', '').replace('show','').strip()
	lookup = lookup.replace(site.lower(), '').replace('on','').strip()
	tvdb_show_name = ''.join(ch for ch in tvdb_show_name if ch not in exclude)
	if 'with' in tvdb_show_name and ':' not in lookup:
		tvdb_show_name = tvdb_show_name.split('with')[0].strip()
	else:
		tvdb_show_name = tvdb_show_name.replace('with', '')
	tvdb_show_name = tvdb_show_name.replace('tarring', '')
	lookup = ''.join(ch for ch in lookup if ch not in exclude)
	if 'with' in lookup:
		lookup = lookup.split('with')[0].strip()
	if 'hoted' in lookup:
		lookup = lookup.split('hoted')[0].strip()
	if 'hosted' in tvdb_show_name:
		tvdb_show_name = tvdb_show_name.split('hosted')[0].strip()
	lookup = lookup.replace('&', 'and')
	tvdb_show_name = tvdb_show_name.replace('&', 'and')
	numbers = {'one':1,
			'two':2,
			'three':3,
			'four':4,
			'five':5,
			'six':6,
			'seven':7,
			'eight':8,
			'nine':9}
	for key in numbers:
		lookup = lookup.replace(key, str(numbers[key]))
		tvdb_show_name = tvdb_show_name.replace(key, str(numbers[key]))
	if len(shows) > 1 or tvdb_show_name != lookup:
		ret = -1
		lookup_name = seriesname.replace('%E2%84%A2', '').lower().replace("'", "").replace('?', '').replace('!', '').replace('&', ' and ').strip()
		lookup_name = lookup_name.replace(u"\u0174", '').replace(u"\u2122", '')
		lookup_network = site.replace('The', '').replace(',', '').strip()
		for i, show_item in enumerate(shows):
			count = 0
			item_name = show_item.seriesname.string.lower().replace("'", "")
			item_name = item_name.replace(u"\u0174", '').replace('&', ' and ').replace(', the', '')
			try:
				item_network = show_item.network.string.replace('The', '').replace(',', '').strip()
			except:
				item_network = ''
			if re.compile('(The )?' + lookup_name.replace(', the', '').replace(' ', '.? ') +'( ' + site + ')?[!?]?( \(?US\)?)?(\s?\([0-9]{4}\))?$', re.IGNORECASE).match(item_name) and (item_network == lookup_network or item_network in network_alias or '(us)' in item_name):
				ret = i
				count = count + 1
		if allowManual == True and (count > 1 or ret == -1):
			select = xbmcgui.Dialog()
			for show_item in shows:
				try:
					show_list.append(show_item.seriesname.string + ' [' + show_item.network.string + ']')
				except:
					show_list.append(show_item.seriesname.string)
			if site.endswith(', The'):
				station = 'The ' + site.replace(', The', '')
			else:
				station = site
			ret = select.select(smart_utf8(addon.getLocalizedString(39020)) + seriesname + ' [' + station.strip() + ']', show_list)
		if ret is not -1:
			seriesid = shows[ret].seriesid.string
	else:
		seriesid = shows[0].seriesid.string
	return seriesid

def get_tvdb_series(seriesname, manualSearch = False, site = '', network_alias = []):
	seriesdata = connection.getURL(TVDBSERIESLOOKUP + urllib.quote_plus(smart_utf8(seriesname)), connectiontype = 0)
	try:
		if int(addon.getSetting('strict_names')) != 2 or manualSearch:
			interactive = True
		else:
			interactive = False
		tvdb_id = get_series_id(seriesdata, seriesname, site, interactive, network_alias)
	except:
		if manualSearch:
			keyb = xbmc.Keyboard(seriesname, smart_utf8(addon.getLocalizedString(39004)))
			keyb.doModal()
			if (keyb.isConfirmed()):
					seriesname_custom = keyb.getText()
					searchurl = TVDBSERIESLOOKUP + urllib.quote_plus(seriesname_custom)
					tvdbid_url = connection.getURL(searchurl, connectiontype = 0)
					try:
						tvdb_id = get_series_id(tvdbid_url, seriesname_custom, site, True)
					except:
						print 'common :: get_tvdb_series :: Manual Search failed'
						return False
			else:
				return False
		else:
			return False
	series_xml = TVDBURL + ('/api/%s/series/%s/en.xml' % (TVDBAPIKEY, tvdb_id))
	series_xml = connection.getURL(series_xml, connectiontype = 0)
	series_tree = BeautifulSoup(series_xml, 'html.parser').find('series')
	try:
		if smart_unicode(series_tree.firstaired.text) is not '':
			first_aired = smart_unicode(series_tree.firstaired.text)
			date = first_aired
			year = first_aired.split('-')[0]
		else:
			first_aired = None
			date = None
			year = None
	except:
		print 'common :: get_tvdb_series :: %s - Air Date Failed' % seriesname
		first_aired = None
		date = None
		year = None
	try:
		if smart_unicode(series_tree.genre.text) is not '':
			genres = smart_unicode(series_tree.genre.text)
		else:
			genres = None
	except:
		print 'common :: get_tvdb_series :: %s - Genre Failed' % seriesname
		genres = None
	try:
		if smart_unicode(series_tree.overview.text) is not '':
			plot = smart_unicode(series_tree.overview.text)
		else:
			plot = None
	except:
		print 'common :: get_tvdb_series :: %s - Plot Failed' % seriesname
		plot = None
	try:
		if smart_unicode(series_tree.actors.text) is not '':
			actors = smart_unicode(series_tree.actors.text)
		else:
			actors = None
	except:
		print 'common :: get_tvdb_series :: %s - Actors Failed' % seriesname
		actors = None
	try:
		if smart_unicode(series_tree.rating.text) is not '':
			rating = smart_unicode(series_tree.rating.text)
		else:
			rating = None
	except:
		print 'common :: get_tvdb_series :: %s - Rating Failed' % seriesname
		rating = None
	try:
		if smart_unicode(series_tree.banner.text) is not '':
			tvdbbanner = smart_unicode(TVDBBANNERS + series_tree.banner.text)
		else:
			tvdbbanner = None
	except:
		print 'common :: get_tvdb_series :: %s - Banner Failed' % seriesname
		tvdbbanner = None
	try:
		if smart_unicode(series_tree.fanart.text) is not '':
			tvdbfanart = smart_unicode(TVDBBANNERS + series_tree.fanart.text)
		else:
			tvdbfanart = None
	except:
		print 'common :: get_tvdb_series :: %s - Fanart Failed' % seriesname
		tvdbfanart = None
	try:
		if smart_unicode(series_tree.poster.text) is not '':
			tvdbposter = smart_unicode(TVDBBANNERS + series_tree.poster.text)
		else:
			tvdbposter = None
	except:
		print 'common :: get_tvdb_series :: %s - Poster Failed' % seriesname
		tvdbposter = None
	try:
		if smart_unicode(series_tree.imdb_id.text) is not '':
			imdb_id = smart_unicode(series_tree.imdb_id.text)
		else:
			imdb_id = None
	except:
		print 'common :: get_tvdb_series :: %s - IMDB_ID Failed' % seriesname
		imdb_id = None
	try:
		if smart_unicode(series_tree.runtime.text) is not '':
			runtime = smart_unicode(series_tree.runtime.text)
		else:
			runtime = None
	except:
		print 'common :: get_tvdb_series :: %s - Runtime Failed' % seriesname
		runtime = None
	try:
		if smart_unicode(series_tree.airs_dayofweek.text) is not '':
			airs_dayofweek = smart_unicode(series_tree.airs_dayofweek.text)
		else:
			airs_dayofweek = None
	except:
		print 'common :: get_tvdb_series :: %s - Airs_DayOfWeek Failed' % seriesname
		airs_dayofweek = None
	try:
		if smart_unicode(series_tree.airs_time.text) is not '':
			airs_time = smart_unicode(series_tree.airs_time.text)
		else:
			airs_time = None
	except:
		print 'common :: get_tvdb_series :: %s - Airs_Time Failed' % seriesname
		airs_time = None
	try:
		if smart_unicode(series_tree.status.text) is not '':
			status = smart_unicode(series_tree.status.text)
		else:
			status = None
	except:
		print 'common :: get_tvdb_series :: %s - Status Failed' % seriesname
		status = None
	try:
		if smart_unicode(series_tree.network.text) is not '':
			network = smart_unicode(series_tree.network.text)
		else:
			network = None
	except:
		print 'common :: get_tvdb_series :: %s - Network Failed' % seriesname
		network = None
	try:
		if smart_unicode(series_tree.seriesname.text) is not '':
			seriesname = smart_unicode(series_tree.seriesname.text)
	except:
		print 'common :: get_tvdb_series :: %s - TVDB SeriesName Failed' % seriesname
	return [tvdb_id, imdb_id, tvdbbanner, tvdbposter, tvdbfanart, first_aired, date, year, actors, genres, network, plot, runtime, rating, airs_dayofweek, airs_time, status, seriesname]

def get_plot_by_tvdbid(tvdb_id):
	command = 'select * from shows where tvdb_id = ?;'
	values = (tvdb_id,)
	showdata = database.execute_command(command, values, fetchone = True)
	prefixplot = ''
	if showdata:
		series_title, mode, sitemode, url, tvdb_id, imdb_id, tvdbbanner, tvdbposter, tvdbfanart, first_aired, date, year, actors, genres, network, plot, runtime, rating, airs_dayofweek, airs_time, status, has_full_episodes, favor, hide, tvdb_series_title = showdata
		if network is not None:
			prefixplot += smart_utf8(addon.getLocalizedString(39013)) + network + '\n'
		if (airs_dayofweek is not None) and (airs_time is not None):
			prefixplot += smart_utf8(addon.getLocalizedString(39014)) + airs_dayofweek + '@' + airs_time + '\n'
		if status is not None:
			prefixplot += smart_utf8(addon.getLocalizedString(39015)) + status + '\n'
		if prefixplot is not '':
			prefixplot += '\n'
		if plot is not None:
			prefixplot = smart_unicode(prefixplot) + smart_unicode(replace_signs(plot))
	return prefixplot

def get_show_data(series_title, mode = '', sitemode = '', url = '', sitedata = None):
	series_title = replace_signs(smart_unicode(series_title))
	if not os.path.exists(ustvpaths.DBFILE):
		database.create_db()
	database.check_db_version()
	showdata = get_serie(series_title, mode, sitemode, url, forceRefresh = False, sitedata = sitedata)
	return showdata

def load_showlist(favored = 0):
	shows = fetch_showlist(favored)
	for show in shows:
		add_show( masterList = True, showdata = show)

def fetch_showlist(favored = 0):
	if not os.path.exists(ustvpaths.DBFILE):
		database.create_db()
		refresh_db()
	elif not favored:
		refresh = False
		command = 'select distinct mode from shows order by mode'
		modes = database.execute_command(command, fetchall = True)
		mode_list = [element[0] for element in modes]
		for network in get_networks():
			if addon.getSetting(network.SITE) == 'true' and network.SITE not in mode_list:
				refresh = True
		if refresh:
			refresh_db()
	database.check_db_version()
	command = "select * from shows  where url <> '' and hide <> 1 and favor = ? order by series_title"
	return database.execute_command(command, fetchall = True, values = [favored]) 

def add_show(series_title = '', mode = '', sitemode = '', url = '', favor = 0, hide = 0, masterList = False, showdata = None, sitedata = None):
	infoLabels = {}
	tvdbfanart = None
	tvdbbanner = None
	tvdbposter = None
	tvdb_id = None
	thumb = ''
	fanart = ''
	prefixplot = ''
	actors2 = []
	try:
		siteplot = sitedata['plot']
	except:
		siteplot = None
	try:
		sitethumb = sitedata['thumb']
	except:
		sitethumb = None
	try:
		sitegenre = sitedata['genre']
	except:
		sitegenre = None
	if showdata is None:
		showdata = get_show_data(series_title, mode, sitemode, url, siteplot)
	series_title, mode, sitemode, url, tvdb_id, imdb_id, tvdbbanner, tvdbposter, tvdbfanart, first_aired, date, year, actors, genres, network, plot, runtime, rating, airs_dayofweek, airs_time, status, has_full_episodes, favor, hide, tvdb_series_title = showdata
	network_module = get_network(mode)
	if not network_module:
		return
	network_name = network_module.NAME
	network_description = network_module.DESCRIPTION
	if tvdbfanart is not None:
		fanart = tvdbfanart
	else:
		if args.__dict__.has_key('fanart'):
			fanart = args.fanart
		else:
			fanart = None
	if tvdbbanner is not None:
		thumb = tvdbbanner
	elif tvdbposter is not None:
		thumb = tvdbposter
	elif sitethumb is not None:
		thumb = sitethumb
	else:
		thumb = os.path.join(ustvpaths.IMAGEPATH, mode + '.png')
	orig_series_title = urllib.quote_plus(smart_utf8(series_title))
	if tvdb_series_title is not None:
		series_title = smart_utf8(tvdb_series_title)
	infoLabels['title'] = series_title
	infoLabels['tvShowtitle'] = series_title
	if network_name.endswith(', The'):
		station = 'The ' + network_name.replace(', The', '')
	else:
		station = network_name
	if network is not None:
		if station == network:
			prefixplot += smart_utf8(addon.getLocalizedString(39013)) + station + '\n'
		else:
			prefixplot += smart_utf8(addon.getLocalizedString(39012)) + network + '\n'
			prefixplot += smart_utf8(addon.getLocalizedString(39013)) + station + '\n'
	else:
		prefixplot += smart_utf8(addon.getLocalizedString(39013)) + station + '\n'
	if (airs_dayofweek is not None) and (airs_time is not None):
		prefixplot += smart_utf8(addon.getLocalizedString(39014)) + airs_dayofweek + '@' + airs_time + '\n'
	elif (airs_dayofweek is not None) and (airs_time is None):
		prefixplot += smart_utf8(addon.getLocalizedString(39014)) + airs_dayofweek + '\n'
	elif  (airs_dayofweek is None) and (airs_time is not None):
		prefixplot += smart_utf8(addon.getLocalizedString(39014)) + airs_time + '\n'
	else:
		pass
	if status is not None:
		prefixplot += smart_utf8(addon.getLocalizedString(39015)) + status + '\n'
	if plot is None and siteplot is not None:
		plot = siteplot
	if prefixplot is not None:
		prefixplot += '\n'
	if plot is not None:
		infoLabels['plot'] = smart_utf8(prefixplot) + smart_utf8(replace_signs(plot))
	else:
		infoLabels['plot'] = smart_utf8(prefixplot)
	if date is not None:
		infoLabels['date'] = smart_utf8(date)
	if first_aired is not None: 
		infoLabels['aired'] = smart_utf8(first_aired)
	if year is not None:
		infoLabels['year'] = smart_utf8(year)
	if actors is not None:
		actors = actors.strip('|').split('|')
		if actors[0] is not '':
			for actor in actors:
				actors2.append(smart_utf8(actor))
			infoLabels['cast'] = actors2
	if genres is not None:
		infoLabels['genre'] = smart_utf8(genres.replace('|',',').strip(','))
	elif sitegenre is not None:
		infoLabels['genre'] = smart_utf8(sitegenre)
	if network is not None:
		infoLabels['studio'] = smart_utf8(network)
	if runtime is not None:
		infoLabels['duration'] = smart_utf8(runtime)
	if rating is not None:
		infoLabels['rating'] = smart_utf8(rating)
	name = smart_utf8(replace_signs(series_title))
	series_title = smart_utf8(replace_signs(series_title))
	u = sys.argv[0]
	u += '?url="' + urllib.quote_plus(url) + '"'
	u += '&mode="' + mode + '"'
	u += '&sitemode="' + sitemode + '"'
	u += '&thumb="' + urllib.quote_plus(thumb) + '"'
	if tvdb_id is not None:
		u += '&tvdb_id="' + urllib.quote_plus(tvdb_id) + '"'
	if ustvpaths.PLUGINFANART is not fanart and fanart is not None:
		u += '&fanart="' + urllib.quote_plus(fanart) + '"'
	if tvdbposter is not None:
		u += '&poster="' + urllib.quote_plus(tvdbposter) + '"'
	u += '&name="' + urllib.quote_plus(series_title) + '"'
	contextmenu = []
	refresh_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([orig_series_title, mode, sitemode,url])) + '&mode=contextmenu' + '&sitemode=refresh_show'
	contextmenu.append((smart_utf8(addon.getLocalizedString(39008)), 'XBMC.RunPlugin(%s)' % refresh_u))
	if favor is 1:
		fav_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([orig_series_title, mode, sitemode,url])) + '&mode=contextmenu' + '&sitemode=unfavor_show'
		contextmenu.append((smart_utf8(addon.getLocalizedString(39006)), 'XBMC.RunPlugin(%s)' % fav_u))
	else:
		fav_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([orig_series_title, mode, sitemode,url])) + '&mode=contextmenu' + '&sitemode=favor_show'
		contextmenu.append((smart_utf8(addon.getLocalizedString(39007)), 'XBMC.RunPlugin(%s)' % fav_u))
	if hide is 1:
		hide_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([orig_series_title, mode, sitemode,url])) + '&mode=contextmenu' + '&sitemode=unhide_show'
		contextmenu.append((smart_utf8(addon.getLocalizedString(39009)), 'XBMC.RunPlugin(%s)' % hide_u))
	else: 
		hide_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([orig_series_title, mode, sitemode,url])) + '&mode=contextmenu' + '&sitemode=hide_show'
		contextmenu.append((smart_utf8(addon.getLocalizedString(39010)), 'XBMC.RunPlugin(%s)' % hide_u))
	delete_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([orig_series_title, mode, sitemode,url])) + '&mode=contextmenu' + '&sitemode=delete_show'
	contextmenu.append((smart_utf8(addon.getLocalizedString(39011)), 'XBMC.RunPlugin(%s)' % delete_u))
	if  addon.getSetting('show_export') == 'true':
		export_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([orig_series_title, mode, sitemode,url])) + '&mode=ExportShowLibrary' + '&submode=exportshow'
		contextmenu.append((smart_utf8(addon.getLocalizedString(39034)) % series_title, 'XBMC.RunPlugin(%s)' % export_u))
	settings_u = sys.argv[0] + '?url="' + urllib.quote_plus('<join>'.join([orig_series_title, mode, sitemode,url])) + '&mode=contextmenu' + '&sitemode=settings'
	contextmenu.append(("Settings", 'XBMC.RunPlugin(%s)' % settings_u))
	if masterList and addon.getSetting('network_in_master') == 'true': 
		displayname = name + ' on ' + network_name
	else:
		displayname = name
	item = xbmcgui.ListItem(displayname, iconImage = thumb, thumbnailImage = thumb)
	item.addContextMenuItems(contextmenu, True)
	item.setProperty('fanart_image', fanart)
	item.setInfo(type = 'Video', infoLabels = infoLabels)
	xbmcplugin.addDirectoryItem(pluginHandle, url = u, listitem = item, isFolder = True)

def add_directory(name, mode = '', sitemode = '', directory_url = '', thumb = None, fanart = None, description = None, aired = '', genre = '', count = 0, locked = -1, unlocked = -1, contextmenu = None):
	if fanart is None:
		if args.__dict__.has_key('fanart'):
			fanart = args.fanart
		else:
			fanart = ustvpaths.PLUGINFANART
	if thumb is None:
		if args.__dict__.has_key('poster'):
			thumb = args.poster
		elif args.__dict__.has_key('thumb'):
			thumb = args.thumb
		else:
			thumb = ''
	if args.__dict__.has_key('name'):
		showname = args.name
	else:
		showname = ''
	if description is None:
		network = get_network(mode)
		if (locked == -1 and unlocked == -1) or locked == 0:
			if args.__dict__.has_key('tvdb_id'):
				description = get_plot_by_tvdbid(args.tvdb_id)
			else:
				description = network.DESCRIPTION
		else:
			description = smart_utf8(addon.getLocalizedString(39013)) + get_network(mode).NAME + '\n\n'
			description += smart_utf8(addon.getLocalizedString(39031)) + str(unlocked) + "\n"
			description += smart_utf8(addon.getLocalizedString(39032)) + str(locked)
			if locked > 0:
				description += smart_utf8(addon.getLocalizedString(39033)) % network.ACCOUNTNAME + '\n' + network.ACCOUNTINFOURL
	infoLabels = {	'title' : name,
					'tvshowtitle' : showname,
					'genre' : genre,
					'premiered' : aired,
					'plot' : description,
					'count' : count }
	u = sys.argv[0]
	u += '?url="' + urllib.quote_plus(directory_url) + '"'
	u += '&mode="' + mode + '"'
	u += '&sitemode="' + sitemode + '"'
	u += '&thumb="' + urllib.quote_plus(thumb) + '"'
	u += '&fanart="' + urllib.quote_plus(fanart) + '"'
	u += '&name="' + urllib.quote_plus(name) + '"'
	if args.__dict__.has_key('tvdb_id'):
		u += '&tvdb_id="' + urllib.quote_plus(args.tvdb_id) + '"'
	item=xbmcgui.ListItem(name, iconImage = thumb, thumbnailImage = thumb)
	item.setProperty('fanart_image', fanart)
	item.setInfo(type = 'Video', infoLabels = infoLabels)
	refresh_u = sys.argv[0] + '?url="<join>"' + sys.argv[0] + '?url="' + '&mode=contextmenu' + '&sitemode=refresh_db' 
	if contextmenu is None:
		contextmenu = []
	contextmenu.append((smart_utf8(addon.getLocalizedString(39021)), 'XBMC.RunPlugin(%s)' % refresh_u))
	item.addContextMenuItems(contextmenu, False)
	xbmcplugin.addDirectoryItem(pluginHandle, url = u, listitem = item, isFolder = True)

def add_video(video_url, displayname, thumb = None, fanart = None, infoLabels = False, HD = False, quality_mode = False):
	displayname = smart_utf8(replace_signs(smart_unicode(displayname)))
	if fanart is None:
		if args.__dict__.has_key('fanart'):
			fanart = args.fanart
		else:
			fanart = ustvpaths.PLUGINFANART
	if thumb is None:
		if args.__dict__.has_key('thumb'):
			thumb = args.thumb
		else:
			thumb = ''
	if 'episode' in infoLabels.keys() and 'season' in infoLabels.keys() and addon.getSetting('add_episode_identifier') == 'true' and infoLabels['season'] != -1 and infoLabels['episode'] != -1:
			displayname = 'S' + str(infoLabels['season']).zfill(2) + 'E' + str(infoLabels['episode']).zfill(2) + ' - ' + displayname
	item = xbmcgui.ListItem(displayname, iconImage = thumb, thumbnailImage = thumb)
	item.setInfo(type = 'Video', infoLabels = infoLabels)
	try:
		if 'durationinseconds' in infoLabels.keys():	
			duration = infoLabels['durationinseconds']
		else:
			duration = 0
		if HD is True:
			item.addStreamInfo('video', {'codec' : 'h264', 'width' : 1280, 'height' : 720, 'duration' : duration})
		else:
			item.addStreamInfo('video', {'codec' : 'h264', 'width' : 720, 'height' : 400, 'duration' : duration})
		item.addStreamInfo('audio', {'codec': 'aac', 'channels' : 2})
	except:
		pass
	item.setProperty('fanart_image', fanart)
	item.setProperty('IsPlayable', 'true')
	if quality_mode:
		contextmenu = []
		if 'episode' in infoLabels.keys():	
			episode = infoLabels['episode']
		else:
			episode = -1
		if 'season' in infoLabels.keys():	
			season = infoLabels['season']
		else:
			season = -1
		if 'TVShowTitle' in infoLabels.keys():
			show_title = infoLabels['TVShowTitle']
		else:
			show_title = ''
		if show_title is None:
			show_title = ''
		quailty_u = sys.argv[0] + '?url='+ urllib.quote_plus('<join>'.join([show_title, str(season), str(episode), thumb, base64.b64encode(displayname), quality_mode, video_url])) +'&mode=contextmenu' + '&sitemode=select_quality' 
		q_u = sys.argv[0] + '?url='+ urllib.quote_plus('<join>'.join([show_title, str(season), str(episode), thumb, base64.b64encode(displayname), quality_mode, video_url])) +'&mode=contextmenu' + '&sitemode=queue' 
		contextmenu.append((smart_utf8(addon.getLocalizedString(39022)), 'XBMC.PlayMedia(%s)' % quailty_u))
		contextmenu.append((smart_utf8(addon.getLocalizedString(39038)), 'XBMC.RunPlugin(%s)' % q_u))
		item.addContextMenuItems(contextmenu)
	xbmcplugin.addDirectoryItem(pluginHandle, url = video_url, listitem = item, isFolder = False)

def show_exception(error1, error2):
	xbmc.executebuiltin('XBMC.Notification(%s, %s, 5000)' % (error1, smart_utf8(error2)))
	
def proxyConfig():
	proxy_config =  {"connectiontype" : addon.getSetting('connectiontype'), 
				"dns_proxy" : [addon.getSetting('dns_proxy'), addon.getSetting('dns_proxy_2'), addon.getSetting('dns_proxy_3')],
				"proxy" : {
							"us_proxy" : addon.getSetting('us_proxy'),
							"us_proxy_port" : addon.getSetting('us_proxy_port'),
							"us_proxy_user" : addon.getSetting('us_proxy_user'),
							"us_proxy_pass" : addon.getSetting('us_proxy_pass')
							}
				}
	proxy_config = simplejson.dumps(proxy_config)
	proxy_config = urllib.quote_plus(proxy_config)
	return proxy_config
