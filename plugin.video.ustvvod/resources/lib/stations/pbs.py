#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import common
import connection
import coveapi
import m3u8
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
pluginHandle = int (sys.argv[1])

SITE = "pbs"
NAME = "PBS"
DESCRIPTION = "PBS and our member stations are America's largest classroom, the nation's largest stage for the arts and a trusted window to the world. In addition, PBS's educational media helps prepare children for success in school and opens up the world to them in an age-appropriate way."
SHOWS = "http://video.pbs.org/programs/list"
SWFURL = "http://www-tc.pbs.org/video/media/swf/PBSPlayer.swf?video=%s&player=viral"
CLOSEDCAPTION = "http://video.pbs.org/videoInfo/%s/?format=jsonp&callback=video_info"
KEY = "RnJlZUNhYmxlLTgxMzQyMmE5LTg0YWMtNDdjYy1iYzVhLTliMDZhY2NlM2I2YQ=="
SECRET = "MDEyYzcxMDgtNWJiNS00YmFlLWI1MWYtMDRkMTIzNGZjZWRk"
TYPES = ["Episode", "Segment", "Clip", "Promotion", "Interstitial", "Other"]

cove = coveapi.connect(base64.b64decode(KEY), base64.b64decode(SECRET))

def masterlist():
	master_start = 0
	master_count = 200
	master_db = []
	master_dict = {}
	master_check = []
	master_menu = simplejson.loads(connection.getURL(SHOWS, header = {'X-Requested-With' : 'XMLHttpRequest'}))
	for master_item in master_menu.itervalues():
		for master_item in master_item:
			master_check.append(master_item['title'])
	while master_start < master_count:
		master_data = cove.programs.filter(fields = 'mediafiles', order_by = 'title', limit_start = master_start)
		master_menu = master_data['results']
		master_count = master_data['count']
		master_stop = master_data['stop']
		del master_data
		for master_item2 in master_menu:
			website = master_item2['website']
			if website is None:
				website = ''
			if master_item2['title'] in master_check and ('PBS Kids' !=  master_item2['nola_root']) and ('blog' not in website):
				master_name = common.smart_utf8(master_item2['title'])
				season_url = re.compile('/cove/v1/programs/(.*?)/').findall(master_item2['resource_uri'])[0]
				tvdb_name = common.get_show_data(master_name, SITE, 'seasons', common.smart_unicode(master_name) + '#' +season_url)[-1]
				if season_url:
					if tvdb_name not in master_dict.keys():
						try:
							master_dict[tvdb_name] = common.smart_unicode(master_name) + '#' +season_url
						except Exception, e:
							print "e1", e
							return e
					else:
						try:
							master_dict[tvdb_name] = master_dict[tvdb_name] + '|' + common.smart_unicode(master_name) + '#' + season_url
						except Exception, e:
							print "error",e
							return e
				else:
					print "No season"
		master_start = master_stop
	for master_name in master_dict:
		season_url = master_dict[master_name]
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons(season_urls = common.args.url):
	seasons = []
	for season_url in season_urls.split('|'):
		name = season_url.split('#')[0]
		season_url = season_url.split('#')[1]
		for type in TYPES:
			try:
				season_data = cove.videos.filter(fields = 'mediafiles', filter_program = season_url, order_by = '-airdate', filter_availability_status = 'Available', limit_start = 0, filter_type = type)
				season_menu = int(season_data['count'])
			except:
				season_menu = 0
			if season_menu > 0:
				if ',' in season_urls:
					seasons.append((name + ' ' + type+'s',  SITE, 'episodes', (season_url + '#' + type), -1, -1))
				else:
					seasons.append((type + 's',  SITE, 'episodes', (season_url + '#' + type), -1, -1))
	return seasons

def episodes(episode_url = common.args.url):
	episodes = []
	episode_id, type = episode_url.split('#')
	episode_start = 0
	episode_count = 200
	page = 0
	while episode_start < episode_count and page <= int(addon.getSetting('maxpages')):
		page = page + 1
		try:
			episode_data = cove.videos.filter(fields = 'associated_images,mediafiles', filter_program = episode_id, order_by = '-airdate', filter_availability_status = 'Available', limit_start = episode_start, filter_type = type)

			episode_menu = episode_data['results']
			episode_count = episode_data['count']
			episode_stop = episode_data['stop']
			del episode_data
			for episode_item in episode_menu:
				infoLabels={}
				if episode_item['mediafiles']:
					url = str(episode_item['tp_media_object_id'])
					episode_name = episode_item['title']
					try:
						season_number = re.compile('Season (\d*)').findall(episode_name)[0]
					except:
						season_number = -1
					try:
						episode_number = re.compile('Episode (\d*)').findall(episode_name)[0]
					except:
						episode_number = -1
					episode_type = 'Full ' + episode_item['type']
					episode_plot = episode_item['long_description']
					episode_airdate = common.format_date(episode_item['airdate'], '%Y-%m-%d %H:%M:%S', '%d.%m.%Y')
					episode_duration = int(episode_item['mediafiles'][0]['length_mseconds'] / 1000)
					episode_thumb = episode_item['associated_images'][0]['url']
					for episode_thumbs in episode_item['associated_images']:
						if episode_thumbs['type']['eeid'] == 'iPad-Large':
							episode_thumb = episode_thumbs['url']
					episode_hd = False
					for episode_media in episode_item['mediafiles']:
						try:
							if int(episode_media['video_encoding']['eeid'].split('-')[1].strip('k')) > 2000:
								episode_hd = True
						except:
							pass
					episode_mpaa = episode_item['rating']
					episode_show = episode_thumb.split('/')[5].replace('-', ' ').title()
					u = sys.argv[0]
					u += '?url="' + urllib.quote_plus(url) + '"'
					u += '&mode="' + SITE + '"'
					u += '&sitemode="play_video"'
					infoLabels={	'title' : episode_name,
									'episode' : episode_number,
									'season' : season_number,
									'durationinseconds' : episode_duration,
									'plot' : episode_plot,
									'premiered' : episode_airdate,
									'mpaa' : episode_mpaa,
									'TVShowTitle' : episode_show} 
					episodes.append((u, episode_name, episode_thumb, infoLabels, None, episode_hd, episode_type))
			episode_start = episode_stop
			if episode_stop == 0:
				break
		except:
			pass
	return episodes

def play_video(video_url = common.args.url):
	hbitrate = -1
	sbitrate = int(addon.getSetting('quality')) * 1024
	closedcaption = None
	video_url2 = None
	finalurl = ''
	try:
		closedcaption = simplejson.loads(connection.getURL(CLOSEDCAPTION % video_url).replace('video_info(', '').replace(')', ''))['closed_captions_url']
	except:
		pass
	if (addon.getSetting('enablesubtitles') == 'true') and (closedcaption is not None) and (closedcaption != ''):
		convert_subtitles(closedcaption.replace(' ', '+'))
	video_data = cove.videos.filter(fields = 'mediafiles', filter_tp_media_object_id = video_url)
	video_menu = video_data['results'][0]['mediafiles']
	for video_item in video_menu:
		if video_item['video_encoding']['eeid'] == 'ipad-16x9':
			video_url2 = video_item['video_data_url']
		elif video_item['video_encoding']['eeid'] == 'hls-2500k-16x9':
			video_url2 = video_item['video_data_url']
		else:
			pass
	if video_url2 is None:
		video_url2 = video_item['video_data_url']
	video_data2 = connection.getURL(video_url2 + '?format=jsonp&callback=jQuery18303874830141490152_1377946043740')
	video_url3 = simplejson.loads(video_data2.replace('jQuery18303874830141490152_1377946043740(', '').replace(')', ''))['url']
	if '.mp4' in video_url3:
		base_url, playpath_url = video_url3.split('mp4:')
		finalurl = base_url +' playpath=mp4:' + playpath_url + '?player= swfurl=' + SWFURL % video_data['results'][0]['guid'] + ' swfvfy=true'
	else:
		video_data3 = connection.getURL(video_url3)
		video_url4 = m3u8.parse(video_data3)
		for video_index in video_url4.get('playlists'):
			bitrate = int(video_index.get('stream_info')['bandwidth'])
			if bitrate > hbitrate and bitrate <= sbitrate:
				hbitrate = bitrate
				finalurl = video_url3.rsplit('/', 1)[0] + '/' + video_index.get('uri')
	xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path = finalurl))
	if (addon.getSetting('enablesubtitles') == 'true') and (closedcaption is not None) and (closedcaption != ''):
		while not xbmc.Player().isPlaying():
			xbmc.sleep(100)
		xbmc.Player().setSubtitles(ustvpaths.SUBTITLE)

def clean_subs(data):
	br = re.compile(r'<br.*?>')
	tag = re.compile(r'<.*?>')
	space = re.compile(r'\s\s\s+')
	apos = re.compile(r'&amp;apos;')
	gt = re.compile(r'&gt;+')
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
	lines = subtitle_data.find_all('p')
	for i, line in enumerate(lines):
		if line is not None:
			sub = clean_subs(common.smart_utf8(line))
			start_time = common.smart_utf8(line['begin'].replace('.', ','))
			if ',' not in start_time:
				start_time = start_time + ',00'
			end_time = common.smart_utf8(line['end'].replace('.', ','))
			if ',' not in end_time:
				end_time = end_time + ',00'
			str_output += str(i + 1) + '\n' + start_time[:11] + ' --> ' + end_time[:11] + '\n' + sub + '\n\n'
	file = open(ustvpaths.SUBTITLE, 'w')
	file.write(str_output)
	file.close()
