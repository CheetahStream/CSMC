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

getSetting          = xbmcaddon.Addon().getSetting
player              = common.XBMCPlayer()
pluginHandle        = int(sys.argv[1])

AUTHURL = 'http://www.tbs.com/processors/cvp/token.jsp'
SWFURL = 'http://z.cdn.turner.com/xslo/cvp/plugins/akamai/streaming/osmf1.6/2.10/AkamaiAdvancedStreamingPlugin.swf'
BASE = 'http://ht.cdn.turner.com/tbs/big/'
HLSBASE = 'http://androidhls-secure.cdn.turner.com/%s/big/'

def masterlist(NAME, MOVIES, SHOWS, SITE, WEBSHOWS = None ):
	master_db = []
	master_dict = {}
	master_db.append(('--' + NAME + ' Movies',  SITE, 'episodes', 'Movie#' + MOVIES))
	master_data = connection.getURL(SHOWS)
	master_menu = simplejson.loads(master_data)
	for master_item in master_menu:
		master_name = common.smart_utf8(master_item['title'])
		if 'ondemandEpisodes' in master_item['excludedSections']:
			has_full_eps = 'false'
		else:
			has_full_eps = 'true'
		if (getSetting('hide_clip_only') == 'false' and 'clips' not in master_item['excludedSections']) or has_full_eps == 'true' or WEBSHOWS is not None:
			season_url = master_name + '#' + master_item['ID'] + '#' + has_full_eps
			master_db.append((master_name,  SITE, 'seasons', season_url))
	return master_db

def seasons(SITE, FULLEPISODES, CLIPSSEASON, CLIPS, WEBSHOWS = None, show_id = common.args.url):
	seasons = []
	master_name = show_id.split('#')[0]
	has_full_eps = show_id.split('#')[2]
	show_id = show_id.split('#')[1]
	if has_full_eps == 'true':
		seasons.append(('Full Episodes',  SITE, 'episodes', master_name + '#' + FULLEPISODES % show_id, -1, -1))
	elif WEBSHOWS is not None:
		try:

			webdata = connection.getURL(WEBSHOWS)
			web_tree =  BeautifulSoup(webdata, 'html.parser', parse_only = SoupStrainer('div', id = 'page-shows'))
			show = web_tree.find('h2', text = master_name)
			episodes = show.findNext('p', attrs = {'data-id' : 'num-full-eps-avail'})['data-value']
			if int(episodes) > 0:
				seasons.append(('Full Episodes',  SITE, 'episodes_web', master_name, -1, -1))
		except:
			pass

	clips_data = connection.getURL(CLIPSSEASON % show_id)
	clips_menu = simplejson.loads(clips_data)
	for season in clips_menu:
		clip_name = common.smart_utf8(season['title'])
		seasons.append((clip_name,  SITE, 'episodes', master_name + '#' + CLIPS % (show_id, season['id']), -1, -1))

	return seasons

def episodes_json(SITE, episode_url = common.args.url):


	episodes = []
	master_name = episode_url.split('#')[0]
	episode_url = episode_url.split('#')[1]
	episode_data = connection.getURL(episode_url)
	episode_menu = simplejson.loads(episode_data)
	for episode_item in episode_menu:
		url = episode_item['episodeID']
		try:

			episode_duration = episode_item['length']
		except:
			episode_duration = -1
		try:

			episode_airdate = common.format_date(episode_item['airDate'].split('on ')[1],'%B %d, %Y')
		except:
			episode_airdate = -1
		try:

			episode_plot = episode_item['summary']
		except:
			episode_plot = episode_item['shortdescription']
		episode_name = episode_item['title']
		if episode_name == master_name:
			video_url = EPISODE % url
			video_data = connection.getURL(video_url)
			video_tree = BeautifulSoup(video_data, 'html.parser')
			episode_name = video_tree.headline.string
		elif episode_name == "":
			episode_name = episode_plot
		try:

			season_number = int(episode_item['identifier'].split(',')[0].split(' ')[1])
		except:
			season_number = -1
		try:

			episode_number =  int(episode_item['identifier'].split(', ')[1].split(' ')[1].replace(' Episode ', ''))
		except:
			try:

				episode_number =  int(episode_item['identifier'].split(', ')[1].split(' ')[1])
			except:
				episode_number = -1
		if episode_number > 100:
			try:

				episode_number = int(re.compile('episode-(\d*)').findall(connection.getRedirect(episode_item['shareURL']))[0])

			except:
				try:
					web_data = _connection.getURL(episode_item['shareURL'])
					web_tree = BeautifulSoup(web_data, 'html.parser')
					episode_number = web_tree.find('h2', text = episode_name).findNext(itemprop = 'episodeNumber').string
					season_number = web_tree.find('h2', text = episode_name).findNext(itemprop = 'seasonNumber').string
				except:
					pass
		try:

			episode_thumb = episode_item['640x360_jpg']
		except:
			episode_thumb = None
		episode_mpaa = episode_item['rating']
		try:
			episode_type = episode_item['type']
		except:
			episode_type = None
		if 'Movie' in master_name:
			type = 'Movie'
		elif episode_type == 1:
			type = 'Full Episode'
		else:
			type = 'Clips'
		if type != 'Movie':
			show_title = master_name
		else:
			show_title = None
		try:
			episode_year = episode_item['year']
		except:
			episode_year = None
		try:
			episode_actors = episode_item['actors'].split(',')
		except:
			episode_actors = []
		u = sys.argv[0]
		u += '?url="' + urllib.quote_plus(url) + '"'
		u += '&mode="' + SITE + '"'
		u += '&sitemode="play_video"'
		infoLabels={    'title' : episode_name,
						'durationinseconds' : episode_duration,
						'season' : season_number,
						'episode' : episode_number,
						'plot' : episode_plot,
						'premiered' : episode_airdate ,
						'year' : episode_year,
						'mpaa' : episode_mpaa,
						'TVShowTitle': show_title,
						'cast' : episode_actors}
		episodes.append((u, episode_name, episode_thumb, infoLabels, 'list_qualities', False, type ))
	return episodes




def episodes(SITE, episode_url = common.args.url):
	episodes = []
	try:
		season_number = int(episode_url.split('filterBySeasonNumber=')[1])
	except:
		season_number = 0 
	episode_data = connection.getURL(episode_url)
	episode_tree = BeautifulSoup(episode_data, 'html.parser')
	episode_menu = episode_tree.find_all('episode')
	for episode_item in episode_menu:
		try:

			episode_season_number = int(episode_item['episeasonnumber'])
		except:
			episode_season_number = 0
		try:
			type = episode_item['episodeType']
		except:
			type = episode_item['episodetype']

		if episode_season_number == season_number or 'filterBySeasonNumber'  not in episode_url:
			segments = episode_item.find_all('segment')
			if len(segments) == 0:
				if type == 'EPI':
					continue
				else:
					url = episode_item['id']
			else:
				url = ''
				for segment in segments:
					url = url + ',' + segment['id']
				url = url[1:]
			try:

				episode_duration = episode_item['duration']
				episode_duration = int(common.format_seconds(episode_duration))
			except:
				episode_duration = 0
				for segment_duration in segments:
					episode_duration += float(segment_duration['duration'])
			try:

				episode_airdate = common.format_date(episode_item['originalpremieredate'].split(' ')[0],'%m/%d/%Y')
			except:
				try:

					episode_airdate = common.format_date(episode_item['launchdate'].split(' ')[0],'%m/%d/%Y')
				except:

					episode_airdate = -1

			episode_expires = episode_item['expirationdate']
			episode_name = episode_item['title']
			try:
				season_number = int(episode_item['episeasonnumber'])
			except:
				season_number = -1
			try:

				episode_number = int(episode_item['episodenumber'][:2])
				
				if episode_number == 0:
					try:
						episode_number = int(re.compile('Ep (\d)').findall(episode_name)[0])
					except:
						episode_number = int(episode_item['subepisodenumber']) 
			except:
				try:
					try:
						episode_number = int(re.compile('Ep (\d)').find_all(episode_name))
					except:
						episode_number = int(episode_item['subepisodenumber'])  - 1
				except:
					episode_number = -1
			try:

				episode_thumb = episode_item['thumbnailurl']
			except:
				episode_thumb = None
			episode_plot = episode_item.description.text.strip()
			try:
				show_title = common.replace_signs(episode_item['collectiontitle'])
			except:
				show_title = None
			episode_rating = episode_item['ranking']
			episode_mpaa = episode_item['rating'].upper()
			if type == 'EPI' or 'TVE':
				episode_type = 'Full Episode'
			else:
				episode_type = 'Clip'
			url = urllib.quote_plus(url)
			u = sys.argv[0]
			u += '?url="' + url + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels={    'title' : episode_name,
							'durationinseconds' : episode_duration,
							'season' : season_number,
							'episode' : episode_number,
							'plot' : episode_plot,
							'premiered' : episode_airdate,
							'TVShowTitle' : show_title,
							'rating' : episode_rating,
							'mpaa' : episode_mpaa}
			infoLabels = common.enrich_infolabels(infoLabels, episode_expires, '%m/%d/%Y %I:%M %p')			
			episodes.append((u, episode_name, episode_thumb, infoLabels, 'list_qualities', False, episode_type))
	return episodes

def play_video(SITE, EPISODE, HLSPATH = None):
	localhttpserver = False
	try:
		qbitrate = common.args.quality
	except:
		qbitrate = None
	stack_url = ''
	for v, video_id in enumerate(common.args.url.split(',')):
		if 'http' not in video_id:
			video_url = EPISODE % video_id
		else:
			video_url = video_id
		hbitrate = -1
		sbitrate = int(getSetting('quality'))
		closedcaption = None
		video_data = connection.getURL(video_url)
		video_tree = BeautifulSoup(video_data, 'html.parser')
		hbitrate = -1
		lbitrate = -1
		file_url = None
		if video_tree.find('file', text = re.compile('mp4:')) is not None:
			hasRTMP = False
		else:
			hasRTMP = True
		if (getSetting('preffered_stream_type') == 'RTMP' and int(getSetting('connectiontype')) == 0) or hasRTMP:
			if qbitrate is  None:
				video_menu = video_tree.find_all('file')
				for video_index in video_menu:
					try:
						try:
							play_mode = video_index['play_mode']
						except:
							play_mode = ''
						if play_mode != 'window':
							bitrate = int(video_index['bitrate'])
							if bitrate < lbitrate or lbitrate == -1:
								lbitrate = bitrate,sbitrate
								lfile_url = video_index.string
							if bitrate > hbitrate and bitrate <= sbitrate:
								hbitrate = bitrate
								file_url = video_index.string
					except:
						pass
				if file_url is None:
					file_url = lfile_url 
			else:
				file_url = video_tree.find('file', attrs = {'bitrate' : qbitrate}).string
			if 'mp4:'  in file_url:
				filename = file_url[1:len(file_url)-4]
				serverDetails = video_tree.find('akamai')
				server = serverDetails.find('src').string.split('://')[1]
				tokentype = serverDetails.find('authtokentype').string
				window = serverDetails.find('window').string
				aifp = serverDetails.find('aifp').string
				auth=getAUTH(aifp,window,tokentype,video_id,filename.replace('mp4:',''), SITE) 
				rtmp = 'rtmpe://' + server + '?' + auth + ' playpath=' + filename + ' swfurl=' + SWFURL + ' swfvfy=true'
				segurl = rtmp
			elif 'http' not in file_url:
				segurl = BASE + file_url
			else:
				segurl = file_url
		else:
			video = video_tree.find('file', bitrate = 'androidtablet').string
			video_url = HLSBASE % HLSPATH + video[1:]
			m3u8_data = connection.getURL(video_url)
			m3u8 = m3u8.parse(m3u8_data)
			uri = None
			for video_index in m3u8.get('playlists'):
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
			master = video_url.split('/')[-1]
			segurl = video_url.replace(master, playpath_url)
			if int(getSetting('connectiontype')) > 0:
				localhttpserver = True
				play_data = connection.getURL(segurl)
				relative_urls = re.compile('(.*ts)\n').findall(play_data)
				relative_k_urls = re.compile('"(.*key)"').findall(play_data)
				proxy_config = common.proxyConfig()
				for i, video_item in enumerate(relative_urls):
					absolueurl =  video_url.replace(master, video_item)
					newurl = base64.b64encode(absolueurl)
					newurl = urllib.quote_plus(newurl)
					newurl = newurl + '/' + proxy_config
					newurl = 'http://127.0.0.1:12345/proxy/' + newurl
					play_data = play_data.replace(video_item,  newurl)
				for i, video_item in enumerate(relative_k_urls):
					absolueurl =  video_url.replace(master, video_item)
					key_data = connection.getURL(absolueurl)        
					key_file = open(ustvpaths.KEYFILE % (str(v) + '-' + str(i)), 'wb')
					key_file.write(key_data)
					key_file.close()
					play_data = play_data.replace(video_item,  'http://127.0.0.1:12345/play%s.key' % (str(v) + '-' + str(i)))
				file_name = ustvpaths.PLAYFILE.replace('.m3u8', str(v) + '.m3u8')
				playfile = open(file_name, 'w')
				playfile.write(play_data)
				playfile.close()
				segurl = 'http://127.0.0.1:12345/' + file_name.split('\\')[-1]
		stack_url += segurl.replace(',', ',,') + ' , '
	if ', ' in stack_url:
		stack_url = 'stack://' + stack_url
	finalurl = stack_url[:-3]
	if localhttpserver:
		filestring = 'XBMC.RunScript(' + os.path.join(ustvpaths.LIBPATH,'proxy.py') + ', 12345)'
		xbmc.executebuiltin(filestring)
		time.sleep(20)
	item = xbmcgui.ListItem(path = finalurl)
	try:
		item.setThumbnailImage(common.args.thumb)
	except:
		pass
	try:
		item.setInfo('Video', {    'title' : common.args.name,
						'season' : common.args.season_number,
						'episode' : common.args.episode_number,
						'TVShowTitle' : common.args.show_title})
	except:
		pass
	xbmcplugin.setResolvedUrl(pluginHandle, True, item)
	if localhttpserver:
			while player.is_active:
				player.sleep(250)

def list_qualities(SITE, EPISODE):
	try:
		video_id = common.args.url.split(',')[0]
	except:
		video_id = common.args.url
	video_url = EPISODE % video_id
	video_data = connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	video_menu = video_tree.find_all('file')
	bitrates = []
	for video_index in video_menu:
		try:
			try:
				play_mode = video_index['play_mode']
			except:
				play_mode = ''
			if play_mode != 'window':
				bitrate = video_index['bitrate']
				display = int(bitrate)
				bitrates.append((display,int(bitrate)))
		except:
			pass
	return bitrates

def getAUTH(aifp, window, tokentype, vid, filename, site):
	parameters = {'aifp' : aifp,
				'window' : window,
				'authTokenType' : tokentype,
				'videoId' : vid,
				'profile' : site,
				'path' : filename
				}
	link = connection.getURL(AUTHURL, parameters)
	return re.compile('<token>(.+?)</token>').findall(link)[0]
