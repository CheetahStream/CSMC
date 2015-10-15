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
import time
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

SITE = "fox"
NAME = "FOX"
DESCRIPTION = "Fox Broadcasting Company is a unit of News Corporation and the leading broadcast television network among Adults 18-49. FOX finished the 2010-2011 season at No. 1 in the key adult demographic for the seventh consecutive year ' a feat that has never been achieved in broadcast history ' while continuing to dominate all network competition in the more targeted Adults 18-34 and Teen demographics. FOX airs 15 hours of primetime programming a week as well as late-night entertainment programming, major sports and Sunday morning news."
SHOWS = "http://assets.fox.com/apps/FEA/v1.8/allshows.json"
CLIPS = "http://feed.theplatform.com/f/fox.com/metadata?count=true&byCustomValue={fullEpisode}{false}&byCategories=Series/%s"
FULLEPISODES = "http://feed.theplatform.com/f/fox.com/metadata?count=true&byCustomValue={fullEpisode}{true}&byCategories=Series/%s"

# for some shows, the name that needs to be passed to FULLEPISODES is different than the one in SHOWS
# this dict can be used to manually fix it
different_show_name = {
	'Cosmos - A Spacetime Odyssey': 'cosmos',
}

def masterlist():
	master_db = []
	master_data = connection.getURL(SHOWS)
	master_menu = simplejson.loads(master_data)['shows']
	for master_item in master_menu:
		if master_item['external_link'] == '' and (master_item['fullepisodes'] == 'true' or addon.getSetting('hide_clip_only') == 'false'):
			master_name = master_item['title']
			master_db.append((master_name, SITE, 'seasons', master_name))
	return master_db

def seasons(season_url = common.args.url):
	seasons = []
	if season_url in different_show_name:
		season_url = different_show_name[season_url]
	season_data = connection.getURL(FULLEPISODES % urllib.quote_plus(season_url) + '&range=0-1')
	try:
		season_menu = int(simplejson.loads(season_data)['total_count'])
	except:
		season_menu = 0
	if season_menu > 0:
		season_url2 = FULLEPISODES % urllib.quote_plus(season_url) + '&range=0-' + str(season_menu)
		seasons.append(('Full Episodes',  SITE, 'episodes', season_url2, -1, -1))
	season_data2 = connection.getURL(CLIPS % urllib.quote_plus(season_url) + '&range=0-1')
	try:
		season_menu2 = int(simplejson.loads(season_data2)['total_count'])
	except:
		season_menu2 = 0
	if season_menu2 > 0:
		season_url3 = CLIPS % urllib.quote_plus(season_url) + '&range=0-' + str(season_menu2)
		seasons.append(('Clips',  SITE, 'episodes', season_url3, -1, -1))
	return seasons

def episodes(episode_url = common.args.url):
	episodes = []
	episode_data = connection.getURL(episode_url)
	episode_menu = simplejson.loads(episode_data.replace('}{', '},{'))['results']
	for episode_item in episode_menu:
		episode_airdate = common.format_date(episode_item['airdate'],'%Y-%m-%d', '%d.%m.%Y')
		if (episode_item['authEndDate'] is None or time.time() >= long(episode_item['authEndDate'])/1000) or (episode_item['fullepisode'] == 'false'):
			show_name = episode_item['series'].split('/')[-1]
			url = episode_item['videoURL']
			episode_duration = int(episode_item['length'])
			episode_plot = episode_item['shortDescription']
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
				episode_thumb = episode_item['videoStillURL']
			except:
				episode_thumb = None
			try:
				episode_expires = int(episode_item['endDate']) / 1000
			except:
				episode_expires = False
			episode_mpaa = episode_item['rating']
			try:
				if episode_item['fullepisode'] == 'true':
					episode_type = 'Full Episode'
				else:
					episode_type = 'Clip'
			except:
				episode_type = 'Clip'
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
							'TVShowTitle'		: show_name,
							'mpaa' 				: episode_mpaa
						}
			infoLabels = common.enrich_infolabels(infoLabels, epoch = episode_expires)
			episodes.append((u, episode_name, episode_thumb, infoLabels, 'list_qualities', False, episode_type))
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
	video_data = connection.getURL(video_url + '&manifest=m3u')
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
	if addon.getSetting('sel_quality') == 'true' or qbitrate is not None or  int(xbmc.getInfoLabel( "System.BuildVersion" )[:2]) < 14 or common.use_proxy() :
		print "********************************selecion"
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
		key_url = re.compile('URI="(.*?)"').findall(video_data4)[0]
		key_data = connection.getURL(key_url, loadcookie = True)
		key_file = open(ustvpaths.KEYFILE % '0', 'wb')
		key_file.write(key_data)
		key_file.close()
		video_url5 = re.compile('(http:.*?)\n').findall(video_data4)
		for i, video_item in enumerate(video_url5):
			newurl = base64.b64encode(video_item)
			newurl = urllib.quote_plus(newurl)
			video_data4 = video_data4.replace(video_item, 'http://127.0.0.1:12345/0/foxstation/' + newurl)
		video_data4 = video_data4.replace(key_url, 'http://127.0.0.1:12345/play0.key')
		localhttpserver = True
		filestring = 'XBMC.RunScript(' + os.path.join(ustvpaths.LIBPATH,'proxy.py') + ', 12345)'
		xbmc.executebuiltin(filestring)
		time.sleep(20)
		playfile = open(ustvpaths.PLAYFILE, 'w')
		playfile.write(video_data4)
		playfile.close()
		finalurl = ustvpaths.PLAYFILE
	else:
		print "******************************** bypass selection"
		player._localHTTPServer = False
		finalurl = video_url2
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
