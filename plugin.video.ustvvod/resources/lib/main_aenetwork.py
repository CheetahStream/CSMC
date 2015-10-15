#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import connection
import m3u8
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

addon = xbmcaddon.Addon()
pluginHandle = int(sys.argv[1])

def masterlist(SITE, SHOWS):
	master_db = []
	master_data = connection.getURL(SHOWS)
	master_tree = simplejson.loads(master_data)
	for master_item in master_tree:
		if (master_item['hasNoVideo'] == 'false'):
			master_name = common.smart_utf8(master_item['detailTitle'])
			master_db.append((master_name, SITE, 'seasons', urllib.quote_plus(master_item['showID'])))
	return master_db

def seasons(SITE, SEASONSEPISODE, SEASONSCLIPS, EPISODES, CLIPS, season_url = common.args.url):
	seasons = []
	season_data = connection.getURL(SEASONSEPISODE % season_url)
	season_tree = simplejson.loads(season_data)['season']
	for season_item in season_tree:
		season_name = 'Season ' + str(season_item)
		seasons.append((season_name,  SITE, 'episodes', EPISODES % (season_url, season_item), -1, -1))
	season_url = common.args.url
	season_data = connection.getURL(SEASONSCLIPS % season_url)
	season_tree = simplejson.loads(season_data)['season']
	for season_item in season_tree:
		season_name = 'Season Clips ' + str(season_item)
		seasons.append((season_name,  SITE, 'episodes', CLIPS % (season_url, season_item), -1, -1))
	return seasons

def episodes(SITE, episode_url = common.args.url):
	episodes = []
	episode_data = connection.getURL(episode_url)
	episode_tree = simplejson.loads(episode_data)['Items']
	for episode_item in episode_tree:
		if episode_item['isBehindWall'] == 'false':
			url = episode_item['playURL_HLS']
			episode_duration = int(episode_item['totalVideoDuration']) / 1000
			try:
				episode_airdate = common.format_date(episode_item['airDate'].split('T')[0],'%Y-%m-%d')
			except:
				episode_airdate = -1
			episode_name = episode_item['title']
			try:
				season_number = int(episode_item['season'])
			except:
				season_number = -1
			try:
				episode_number = int(episode_item['episode'])
			except:
				episode_number = -1
			try:
				episode_thumb = episode_item['thumbnailImageURL']
			except:
				try:
					episode_thumb = episode_item['stillImageURL']
				except:
					try:
						episode_thumb = episode_item['modalImageURL']
					except:
						episode_thumb = None
			episode_plot = episode_item['description']
			episode_showtitle = episode_item['seriesName']
			try:
				episode_mpaa = episode_item['rating'].upper()
			except:
				episode_mpaa = None
			try:
				episode_expires = episode_item['expirationDate'].split('T')[0]
			except:
				episode_expires = None
			if episode_item['mrssLengthType'] == 'Episode':
				episode_type = 'Full Episode'
			else:
				episode_type = 'Clips'
			try:
				if  episode_item['isHD'] == 'true':
					episode_HD = True
				else:
					episode_HD = False
			except:
				episode_HD = False
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels={	'title' 			: episode_name,
							'durationinseconds' : episode_duration,
							'season' 			: season_number,
							'episode' 			: episode_number,
							'plot' 				: episode_plot,
							'premiered' 		: episode_airdate,
							'TVShowTitle' 		: episode_showtitle,
							'mpaa' 				: episode_mpaa }
			episodes.append((u, episode_name, episode_thumb, infoLabels, 'list_qualities', episode_HD, episode_type))
	return episodes

def list_qualities():
	video_url = common.args.url
	bitrates = []
	sig = sign_url(video_url)
	smil_url = re.compile('(.+)\?').findall(video_url)[0] + '?switch=hls&assetTypes=medium_video_s3&mbr=true&metafile=true&sig=' + sig
	video_data = connection.getURL(smil_url)
	smil_tree = BeautifulSoup(video_data, 'html.parser')
	video_url2 = smil_tree.video['src']
	m3u_master_data = connection.getURL(video_url2)
	m3u_master = m3u8.parse(m3u_master_data)
	for video_index in m3u_master.get('playlists'):
		bitrate = int(video_index.get('stream_info')['bandwidth'])
		display = int(bitrate) / 1024
		bitrates.append((display, bitrate))
	return bitrates

def play_video():
	try:
		qbitrate = common.args.quality
	except:
		qbitrate = None
	closedcaption = None
	video_url = common.args.url
	sig = sign_url(video_url)
	smil_url = re.compile('(.+)\?').findall(video_url)[0] + '?switch=hls&assetTypes=medium_video_s3&mbr=true&metafile=true&sig=' + sig
	smil_data = connection.getURL(smil_url)
	smil_tree = BeautifulSoup(smil_data, 'html.parser')
	video_url2 = smil_tree.video['src']	
	try:
		closedcaption = smil_tree.textstream['src']
	except:
		pass
	m3u_master_data = connection.getURL(video_url2, savecookie = True)
	m3u_master = m3u8.parse(m3u_master_data)
	hbitrate = -1
	sbitrate = int(addon.getSetting('quality')) * 1024
	for video_index in m3u_master.get('playlists'):
		bitrate = int(video_index.get('stream_info')['bandwidth'])
		if qbitrate is None:
			if bitrate > hbitrate and bitrate <= sbitrate:
				hbitrate = bitrate
				m3u8_url =  video_index.get('uri')
		elif  bitrate == qbitrate:
			m3u8_url =  video_index.get('uri')
	m3u_data = connection.getURL(m3u8_url, loadcookie = True)
	key_url = re.compile('URI="(.*?)"').findall(m3u_data)[0]
	key_data = connection.getURL(key_url, loadcookie = True)		
	key_file = open(ustvpaths.KEYFILE % '0', 'wb')
	key_file.write(key_data)
	key_file.close()
	video_url5 = re.compile('(http:.*?)\n').findall(m3u_data)
	for i, video_item in enumerate(video_url5):
		newurl = base64.b64encode(video_item)
		newurl = urllib.quote_plus(newurl)
		m3u_data = m3u_data.replace(video_item, 'http://127.0.0.1:12345/0/foxstation/' + newurl)
	localhttpserver = True
	filestring = 'XBMC.RunScript(' + os.path.join(ustvpaths.LIBPATH,'proxy.py') + ', 12345)'
	xbmc.executebuiltin(filestring)
	time.sleep(20)
	m3u_data = m3u_data.replace(key_url, 'http://127.0.0.1:12345/play0.key')
	playfile = open(ustvpaths.PLAYFILE, 'w')
	playfile.write(m3u_data)
	playfile.close()
	finalurl = ustvpaths.PLAYFILE
	if (addon.getSetting('enablesubtitles') == 'true') and (closedcaption is not None):
		convert_subtitles(closedcaption)
	item = xbmcgui.ListItem(path = finalurl)
	try:
		item.setThumbnailImage(common.args.thumb)
	except:
		pass
	try:
		item.setInfo('Video', {	'title' 	  : common.args.name,
								'season' 	  : common.args.season_number,
								'episode' 	  : common.args.episode_number,
								'TVShowTitle' : common.args.show_title})
	except:
		pass
	xbmcplugin.setResolvedUrl(pluginHandle, True, item)
	if ((addon.getSetting('enablesubtitles') == 'true') and (closedcaption is not None))  or localhttpserver is True:
		while not xbmc.Player().isPlaying():
			xbmc.sleep(100)
	if (addon.getSetting('enablesubtitles') == 'true') and (closedcaption is not None):
		xbmc.Player().setSubtitles(ustvpaths.SUBTITLE)
	if localhttpserver is True:
		while xbmc.Player().isPlaying():
			xbmc.sleep(1000)
		connection.getURL('http://localhost:12345/stop', connectiontype = 0)

def clean_subs(data):
	br = re.compile(r'<br.*?>')
	tag = re.compile(r'<.*?>')
	space = re.compile(r'\s\s\s+')
	apos = re.compile(r'&amp;apos;')
	gt = re.compile(r'&gt;')
	sub = br.sub('\n', data)
	sub = tag.sub(' ', sub)
	sub = space.sub(' ', sub)
	sub = apos.sub('\'', sub)
	sub = gt.sub('>', sub)
	return sub

def convert_subtitles(closedcaption):
	str_output = ''
	subtitle_data = connection.getURL(closedcaption, connectiontype = 0)
	subtitle_data = BeautifulSoup(subtitle_data, 'html.parser', parse_only = SoupStrainer('div'))
	srt_output = ''
	lines = subtitle_data.find_all('p')
	i = 0
	last_start_time = ''
	last_end_time = ''
	for line in lines:
		try:
			if line is not None:
				sub = clean_subs(common.smart_utf8(line))
				start_time = common.smart_utf8(line['begin'].replace('.', ','))
				end_time = common.smart_utf8(line['end'].replace('.', ','))
				if start_time != last_start_time and end_time != last_end_time:
					str_output += '\n' + str(i + 1) + '\n' + start_time + ' --> ' + end_time + '\n' + sub + '\n'
					i = i + 1
					last_end_time = end_time
					last_start_time = start_time
				else:
					str_output +=  sub + '\n\n'
		except:
			pass
	file = open(ustvpaths.SUBTITLE, 'w')
	file.write(str_output)
	file.close()
	return True

def sign_url(url):
	sig = connection.getURL('http://www.history.com/components/get-signed-signature?url=' + re.compile('/[sz]/(.+)\?').findall(url)[0])
	return sig
