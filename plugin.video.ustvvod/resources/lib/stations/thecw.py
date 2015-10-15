#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import common
import connection
import database
import glob
import m3u8
import os
import re
import shutil
import simplejson
import sys
import time
import urllib
import ustvpaths
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

addon = xbmcaddon.Addon()
player = common.XBMCPlayer()
pluginHandle = int(sys.argv[1])

SITE = "thecw"
NAME = "The CW"
DESCRIPTION = "The CW Network was formed as a joint venture between Warner Bros. Entertainment and CBS Corporation. The CW is America's fifth broadcast network and the only network targeting women 18-34. The network's primetime schedule includes such popular series as America's Next Top Model, Gossip Girl, Hart of Dixie, 90210, The Secret Circle, Supernatural, Ringer, Nikita, One Tree Hill and The Vampire Diaries"
SHOWS = "http://www.cwtv.com/feed/mobileapp/shows?pagesize=100&api_version=3"
VIDEOLIST = "http://www.cwtv.com/feed/mobileapp/videos?show=%s&api_version=3"
VIDEOURL = "http://metaframe.digitalsmiths.tv/v2/CWtv/assets/%s/partner/132?format=json"
RTMPURL = "rtmpe://wbworldtv.fcod.llnwd.net/a2246/o23/"
SWFURL = "http://pdl.warnerbros.com/cwtv/digital-smiths/production_player/vsplayer.swf"
CLOSEDCAPTION = "http://api.digitalsmiths.tv/metaframe/200f2a4d/asset/%s/filter"

def masterlist():
	master_db = []
	master_data = connection.getURL(SHOWS)
	master_menu = simplejson.loads(master_data)['items']
	for master_item in master_menu:
		master_name = master_item['title']
		season_url = master_item['slug']
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons(season_url = common.args.url):
	seasons = []
	fullepisodes = 0
	clips = 0
	season_data = connection.getURL(VIDEOLIST % season_url)
	season_menu = simplejson.loads(season_data)['videos']
	for season_item in season_menu:
		if int(season_item['fullep']) == 1:
			fullepisodes = 1
		else:
			clips = 1
	if fullepisodes == 1:
		seasons.append(('Full Episodes',  SITE, 'episodes', season_url + '#1', -1, -1))
	if clips == 1:
		seasons.append(('Clips',  SITE, 'episodes', season_url + '#0', -1, -1))
	return seasons

def episodes(episode_url = common.args.url):
	episodes = []
	try:
		shutil.rmtree(os.path.join(ustvpaths.DATAPATH,'thumbs'))
	except:
		pass
	episode_data = connection.getURL(VIDEOLIST % episode_url.split('#')[0])
	episode_menu = simplejson.loads(episode_data)['videos']
	try:
		os.mkdir(os.path.join(ustvpaths.DATAPATH,'thumbs'))
	except:
		pass
	for episode_item in episode_menu:
		if int(episode_item['fullep']) == int(episode_url.split('#')[1]):
			show_name = episode_item['series_name']
			url = episode_item['guid']
			episode_duration = int(episode_item['duration_secs'])
			episode_plot = episode_item['description_long']
			episode_name = episode_item['title']
			season_number = int(episode_item['season'])
			episode_thumb = episode_item['large_thumbnail']
			thumb_file = episode_thumb.split('/')[-1]
			thumb_path = os.path.join(ustvpaths.DATAPATH, 'thumbs', thumb_file)
			dbpath = xbmc.translatePath(ustvpaths.DBPATH)
			thumbcount = 0
			for name in glob.glob(os.path.join(dbpath, 'textures[0-9]*.db')):
				thumbcount = thumbcount + database.execute_command('select count(1) from texture where url = ?', [thumb_path,], fetchone = True, dbfile = name)[0]
			if thumbcount == 0:
				thumb_data = connection.getURL(episode_thumb)
				file = open(thumb_path, 'wb')
				file.write(thumb_data)
				file.close()
			try:
				episode_number = int(episode_item['episode'][len(str(season_number)):])
			except:
				episode_number = -1
			try:
				episode_airdate = common.format_date(episode_item['airdate'],'%Y-%b-%d', '%d.%m.%Y')
			except:
				episode_airdate = -1
			if episode_item['fullep'] == 1:
				episode_type = 'Full Episode'
			else:
				episode_type = 'Clip'
			episode_expires = episode_item['expire_time']
			episode_mpaa = episode_item['rating']
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels={	'title' : episode_name,
							'durationinseconds' : episode_duration,
							'season' : season_number,
							'episode' : episode_number,
							'plot' : episode_plot,
							'premiered' : episode_airdate,
							'tvshowtitle': show_name ,
							'TVShowTitle': show_name,
							'mpaa' : episode_mpaa}
			infoLabels = common.enrich_infolabels(infoLabels, episode_expires.split('+')[0], '%Y-%m-%dT%H:%M:%S')
			episodes.append((u, episode_name, thumb_path, infoLabels, None, False, episode_type))
	return episodes

def play_video(video_url = common.args.url):
	hbitrate = -1
	lbitrate =- 1
	playpath_url = None
	if addon.getSetting('enablesubtitles') == 'true':
		convert_subtitles(video_url)
		player._subtitles_Enabled = True
	sbitrate = int(addon.getSetting('quality'))
	video_data = connection.getURL(VIDEOURL % video_url)
	video_tree = simplejson.loads(video_data)
	for video_key in video_tree['videos']:
		try:
			video_index = video_tree['videos'][video_key]
			bitrate = int(video_index['bitrate'])
			if bitrate < lbitrate or lbitrate == -1:
				lbitrate = bitrate
				lplaypath_url = video_index['uri'].split('mp4:')[1].replace('Level3', '')
			if bitrate > hbitrate and bitrate <= sbitrate:
				hbitrate = bitrate
 				playpath_url = video_index['uri'].split('mp4:')[1].replace('Level3', '')
		except:
			playpathm3u8 = video_index['uri']
	if addon.getSetting('preffered_stream_type') == 'HLS':
		playpath_url = None
		lplaypath_url = None
		m3u8_data = connection.getURL(playpathm3u8)
		m3u8_obj = m3u8.parse(m3u8_data)
		uri = None
		for video_index in m3u8_obj.get('playlists'):
			if int(video_index.get('stream_info')['bandwidth']) > 64000:
				bitrate = int(video_index.get('stream_info')['bandwidth']) /1024
				if bitrate < lbitrate or lbitrate == -1:
					lbitrate = bitrate
					lplaypath_url = video_index.get('uri')
				if bitrate > hbitrate and bitrate <= sbitrate:
					hbitrate = bitrate
					playpath_url = video_index.get('uri')
	if playpath_url is None:
		playpath_url = lplaypath_url
	if addon.getSetting('preffered_stream_type') == 'RTMP':
		finalurl = RTMPURL + ' playpath=mp4:' + playpath_url + ' swfurl=' + SWFURL + ' swfvfy=true'
		player._localHTTPServer = False
	else:
		play_data = connection.getURL(playpath_url)
		key_url = re.compile('URI="(.*?)"').findall(play_data)[0]
		key_data = connection.getURL(key_url)		
		key_file = open(ustvpaths.KEYFILE % '0', 'wb')
		key_file.write(key_data)
		key_file.close()
		relative_urls = re.compile('(.*ts)\n').findall(play_data)
		name = playpath_url.split('/')[-1]
		proxy_config = common.proxyConfig()
		for i, video_item in enumerate(relative_urls):
			absolueurl =  playpath_url.replace(name, video_item)
			if int(addon.getSetting('connectiontype')) > 0:
				newurl = base64.b64encode(absolueurl)
				newurl = urllib.quote_plus(newurl)
				newurl = newurl + '/' + proxy_config
				newurl = 'http://127.0.0.1:12345/proxy/' + newurl
			else:
				newurl = absolueurl
			play_data = play_data.replace(video_item,  newurl)
		localhttpserver = True
		filestring = 'XBMC.RunScript(' + os.path.join(ustvpaths.LIBPATH,'proxy.py') + ', 12345)'
		xbmc.executebuiltin(filestring)
		time.sleep(20)
		play_data = play_data.replace(key_url, 'http://127.0.0.1:12345/play0.key')
		playfile = open(ustvpaths.PLAYFILE, 'w')
		playfile.write(play_data)
		playfile.close()
		finalurl = ustvpaths.PLAYFILE
	item = xbmcgui.ListItem(path = finalurl)
	try:
		item.setInfo('Video', {	'title' : common.args.name,
						'season' : common.args.season_number,
						'episode' : common.args.episode_number,
						'TVShowTitle' : common.args.show_title})
	except:
		try:
			item.setInfo('Video', {	'title' : common.args.name})
		except:
			pass
	xbmcplugin.setResolvedUrl(pluginHandle, True, item)
	while player.is_active:
		player.sleep(250)

def convert_subtitles(video_guid):
	try:
		file = None
		dialog = xbmcgui.DialogProgress()
        	dialog.create(common.smart_utf8(addon.getLocalizedString(39026)))
		dialog.update(0, common.smart_utf8(addon.getLocalizedString(39027)))
		str_output = ''
		subtitle_data = connection.getURL(CLOSEDCAPTION % video_guid, connectiontype = 0)
		subtitle_data = simplejson.loads(subtitle_data)
		lines_total = len(subtitle_data)
		dialog.update(0, common.smart_utf8(addon.getLocalizedString(39028)))
		for i, subtitle_line in enumerate(subtitle_data):
			if subtitle_line is not None and 'Text' in subtitle_line['metadata']:
				if (dialog.iscanceled()):
					return
				if i % 10 == 0:
					percent = int( (float(i*100) / lines_total) )
					dialog.update(percent, common.smart_utf8(addon.getLocalizedString(30929)))
				sub = common.smart_utf8(subtitle_line['metadata']['Text'])
				start_time = common.smart_utf8(str(subtitle_line['startTime'])).split('.')
				start_minutes, start_seconds = divmod(int(start_time[0]), 60)
				start_hours, start_minutes = divmod(start_minutes, 60)
				start_time = '%02d:%02d:%02d,%02d' % (start_hours, start_minutes, start_seconds, int(start_time[1][0:2]))
				end_time = common.smart_utf8(str(subtitle_line['endTime'])).split('.')
				end_minutes, end_seconds = divmod(int(end_time[0]), 60)
				end_hours, end_minutes = divmod(end_minutes, 60)
				end_time = '%02d:%02d:%02d,%02d' % (end_hours, end_minutes, end_seconds, int(end_time[1][0:2]))
				str_output += str(i + 1) + '\n' + start_time + ' --> ' + end_time + '\n' + sub + '\n\n'
		file = open(ustvpaths.SUBTITLE, 'w')
		file.write(str_output)
		file.close()
	except Exception, e:
		print "Exception: " + unicode(e)
		common.show_exception(NAME, addon.getLocalizedString(39030))
	finally:
		if file is not None:
			file.close()
