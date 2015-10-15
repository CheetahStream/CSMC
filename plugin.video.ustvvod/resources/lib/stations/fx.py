#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import common
import connection
import m3u8
import os
import re
import simplejson
import sys
import urllib
import ustvpaths
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

addon = xbmcaddon.Addon()
player = common.XBMCPlayer()
pluginHandle = int(sys.argv[1])

SITE = "fx"
NAME = "FX"
ALIAS = ["FXX", "FOX"]
DESCRIPTION = "FX (originally an initialism of \"Fox extended\", suggesting \"effects\", and stylized as fX from 1994 to 1997) is an American basic cable and satellite television channel that is owned by the Fox Entertainment Group division of 21st Century Fox. FX's programming primarily includes original drama and comedy series (which aspire to the standards of premium cable channels like HBO and Showtime, in regard to adult themes and more unique, higher-quality writing/directing/acting), and reruns of theatrically released feature films and \"broadcast network\" sitcoms."
SHOWS = "http://fapi.fxnetworks.com/fx1_1/shows?filter%5B%5D=broadcast:1&nojoins=1&per_page=all"
FULLEPISODES = "http://fapi.fxnetworks.com/fx/videos?fields=airDate%2Cios_video_url%2Cduration%2Cdescription%2Cname%2Cseason%2Cepisode%2Cimg_url&filter%5B%5D=fullEpisode%3A1&nojoins=1&per_page=all&filter%5B%5D=requiresAuth%3A&filter%5B%5D=fapi_show_id%3A"
CLIPS = "http://fapi.fxnetworks.com/fx/videos?fields=airDate%2Cios_video_url%2Cduration%2Cdescription%2Cname%2Cseason%2Cepisode%2Cimg_url&filter%5B%5D=fullEpisode%3A0&nojoins=1&per_page=all&filter%5B%5D=requiresAuth%3A&filter%5B%5D=fapi_show_id%3A"
AUTH = {'Authentication' : '5a90127750a5907e5d0964785474b33a43d65fa0'}

def masterlist():
	master_db = []
	master_data = connection.getURL(SHOWS, header = AUTH)
	master_menu = simplejson.loads(master_data)['shows']
	for master_item in master_menu:
		if (int(master_item['playable_episodes']) > 0) or (addon.getSetting('hide_clip_only') == 'false'):
			master_name = master_item['name']
			master_id = master_item['id']
			master_db.append((master_name, SITE, 'seasons', master_id))
	return master_db

def seasons(season_url = common.args.url):
	seasons = []
	season_data = connection.getURL(FULLEPISODES, header = AUTH)
	try:
		season_menu = len(simplejson.loads(season_data)['videos'])
	except:
		season_menu = 0
	if season_menu > 0:
		season_url2 = FULLEPISODES + season_url
		seasons.append(('Full Episodes',  SITE, 'episodes', season_url2, -1, -1))
	season_data2 = connection.getURL(CLIPS + season_url, header = AUTH)
	try:
		season_menu2 = len(simplejson.loads(season_data2)['videos'])
	except:
		season_menu2 = 0
	if season_menu2 > 0:
		season_url3 = CLIPS + season_url
		seasons.append(('Clips',  SITE, 'episodes', season_url3, -1, -1))
	return seasons

def episodes(episode_url = common.args.url):
	episodes = []
	episode_data = connection.getURL(episode_url, header = AUTH)
	episode_menu = simplejson.loads(episode_data)['videos']
	for episode_item in episode_menu:
		episode_airdate = common.format_date(episode_item['airDate'],'%Y-%m-%d', '%d.%m.%Y')
		url = episode_item['ios_video_url']
		episode_duration = int(episode_item['duration'])
		episode_plot = episode_item['description']
		episode_name = episode_item['name']
		try:
			season_number = episode_item['season']
		except:
			season_number = -1
		try:
			episode_number = episode_item['episode']
		except:
			episode_number = -1
		try:
			episode_thumb = episode_item['img_url'].replace(' ', '%20')
		except:
			episode_thumb = None
		u = sys.argv[0]
		u += '?url="' + urllib.quote_plus(url) + '"'
		u += '&mode="' + SITE + '"'
		u += '&sitemode="play_video"'
		infoLabels={	'title' 			: episode_name,
						'durationinseconds' : episode_duration,
						'season' 			: season_number,
						'episode' 			: episode_number,
						'plot' 				: episode_plot,
						'premiered' 		: episode_airdate
					}
		episodes.append((u, episode_name, episode_thumb, infoLabels,  'list_qualities', False, 'Clip'))
	return episodes

def play_video(video_url = common.args.url):
	try:
		qbitrate = common.args.quality
	except:
		qbitrate = None
	hbitrate = -1
	lbitrate = -1
	sbitrate = int(addon.getSetting('quality')) * 1000
	finalurl = ''
	key_included = False
	video_data = connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	if (addon.getSetting('enablesubtitles') == 'true'):
		try:
			closedcaption = video_tree.find('textstream', src = True)['src']
			convert_subtitles(closedcaption)
			video_closedcaption = 'true'
			player._subtitles_Enabled = True
		except:
			video_closedcaption = 'false'
	video_url2 = video_tree.find('video', src = True)['src']
	video_data2 = connection.getURL(video_url2, savecookie = True)
	video_url3 = m3u8.parse(video_data2)
	video_url4 = None
	for video_index in video_url3.get('playlists'):
		bitrate = int(video_index.get('stream_info')['bandwidth'])
		if qbitrate is None:
			if (bitrate < lbitrate or lbitrate == -1) and bitrate > 100000:
				lbitrate = bitrate
				lvideo_url4 = video_index.get('uri')
			if bitrate > hbitrate and bitrate <= sbitrate and bitrate > 100000:
				hbitrate = bitrate
				video_url4 = video_index.get('uri')
			if video_url4 is None:
				video_url4 = lvideo_url4
		else:
			if qbitrate == bitrate:
				video_url4 = video_index.get('uri')
	video_data4 = connection.getURL(video_url4, loadcookie = True)
	try:
		key_url = re.compile('URI="(.*?)"').findall(video_data4)[0]
		key_data = connection.getURL(key_url, loadcookie = True)
		key_file = open(ustvpaths.KEYFILE % '0', 'wb')
		key_file.write(key_data)
		key_file.close()
		key_included = True
	except:
		pass
	video_url5 = re.compile('(http:.*?)\n').findall(video_data4)
	for i, video_item in enumerate(video_url5):
		newurl = base64.b64encode(video_item)
		newurl = urllib.quote_plus(newurl)
		video_data4 = video_data4.replace(video_item, 'http://127.0.0.1:12345/0/foxstation/' + newurl)
	if key_included == True:
		video_data4 = video_data4.replace(key_url, 'http://127.0.0.1:12345/play0.key')
	localhttpserver = True
	filestring = 'XBMC.RunScript(' + os.path.join(ustvpaths.LIBPATH,'proxy.py') + ', 12345)'
	xbmc.executebuiltin(filestring)
	playfile = open(ustvpaths.PLAYFILE, 'w')
	playfile.write(video_data4)
	playfile.close()
	finalurl = ustvpaths.PLAYFILE
	item = xbmcgui.ListItem(path = finalurl)
	if qbitrate is not None:
		item.setThumbnailImage(common.args.thumb)
		item.setInfo('Video', {	'title' 	  : common.args.name,
								'season' 	  : common.args.season_number,
								'episode'     : common.args.episode_number,
								'TVShowTitle' : common.args.show_title})
	xbmcplugin.setResolvedUrl(pluginHandle, True, item)
	while player.is_active:
		player.sleep(250)

def list_qualities(video_url = common.args.url):
	bitrates = []
	video_data = connection.getURL(video_url + '&manifest=m3u')
	video_tree = BeautifulSoup(video_data, 'html.parser')
	video_url2 = video_tree.find('video', src = True)['src']
	video_data2 = connection.getURL(video_url2, savecookie = True)
	video_url3 = m3u8.parse(video_data2)
	for video_index in video_url3.get('playlists'):
		bitrate = int(video_index.get('stream_info')['bandwidth'])
		if bitrate  > 100000:
			bitrates.append((bitrate / 1000, bitrate))
	return bitrates

def clean_subs(data):
	br = re.compile(r'<br.*?>')
	tag = re.compile(r'<.*?>')
	space = re.compile(r'\s\s\s+')
	apos = re.compile(r'&amp;apos;')
	sub = br.sub('\n', data)
	sub = tag.sub(' ', sub)
	sub = space.sub(' ', sub)
	sub = apos.sub('\'', sub)
	return sub

def convert_subtitles(closedcaption):
	str_output = ''
	last_start_time = ''
	subtitle_data = connection.getURL(closedcaption, connectiontype = 0)
	subtitle_data = BeautifulSoup(subtitle_data, 'html.parser', parse_only = SoupStrainer('div'))
	lines = subtitle_data.find_all('p')
	for i, line in enumerate(lines):
		if line is not None:
			sub = clean_subs(common.smart_utf8(line))
			start_time = common.smart_utf8(line['begin'].replace('.', ','))
			try:
				end_time = common.smart_utf8(line['end'].replace('.', ','))
			except:
				continue
			if last_start_time != start_time:
				if i != 0:
					str_output += '\n\n'
				str_output += str(i + 1) + '\n' + start_time + ' --> ' + end_time + '\n' + sub
			else:
				str_output += '\n' + sub 
			last_start_time = start_time
	file = open(ustvpaths.SUBTITLE, 'w')
	file.write(str_output)
	file.close()
