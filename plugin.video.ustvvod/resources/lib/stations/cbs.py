#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import connection
import ordereddict
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
pluginHandle = int(sys.argv[1])

SITE = "cbs"
NAME = "CBS"
DESCRIPTION = "CBS was established in 1928, when founder William Paley purchased 16 independent radio stations and christened them the Columbia Broadcast System. Today, with more than 200 television stations and affiliates reaching virtually every home in the United States, CBS's total primetime network lineup is watched by more than 130 million people a week during the 2010/2011 season. The Network has the #1 drama/scripted program, NCIS; #1 sitcom, TWO AND A HALF MEN; #1 newsmagazine, 60 MINUTES; and #1 daytime drama, THE YOUNG AND THE RESTLESS. Its programming arms include CBS Entertainment, CBS News and CBS Sports."
ACCOUNTNAME = "CBS All Access"
ACCOUNTINFOURL = "www.cbs.com/all-access"
SHOWS = "http://www.cbs.com/carousels/showsByCategory/0/offset/0/limit/100"
ORIGINALS = "http://www.cbs.com/carousels/showsByCategory/4/offset/0/limit/100"
MOVIES = "http://www.cbs.com/carousels/showsByCategory/6/offset/0/limit/100"
BASE  = "http://www.cbs.com"
FULLEPISODES = "http://www.cbs.com/carousels/videosBySection/%s/offset/0/limit/100/xs/0/"
FULLEPISODESWITHSEASON = "http://www.cbs.com/carousels/videosBySection/%s/offset/0/limit/80/xs/0/%s"
EPISODE = "http://link.theplatform.com/s/dJ5BDC/%s?format=SMIL&Tracking=true&mbr=true"
SWFURL = "http://canstatic.cbs.com/chrome/canplayer.swf"
LOGIN_URL = "https://www.cbs.com/account/login/"

def masterlist():
	master_db = []
	master_dict = {}
	dupes = []
	for master_url in (SHOWS, ORIGINALS, MOVIES):
		master_data = connection.getURL(master_url)
		master_menu = simplejson.loads(master_data)['result']['data']
		for master_item in master_menu:
			show_id = master_item['show_id']
			if show_id not in dupes:
				dupes.append(show_id)
				master_name = master_item['title']
				if master_item['navigationItemLink'] and 'video' not in master_item['navigationItemLink'][0]['link'] and master_item['navigationItemLink'][0]['title'] == 'Watch':
					season_url = master_item['navigationItemLink'][0]['link']
				else:
					if master_item['link'][-1:] == '/':
						season_url = master_item['link'] + 'video'
					else:
						season_url =  master_item['link'] + '/video'
				if BASE not in season_url:
					season_url = BASE + season_url
				master_dict[master_name] = season_url
	for master_name, season_url in master_dict.iteritems():
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons(season_urls = common.args.url):
	seasons = []
	root_url = season_urls
	season_data = connection.getURL(season_urls)
	try:
		show_id = re.compile('video.settings.show_id = (.*);').findall(season_data)[0]
		try:
			section_metadata = re.compile('video.section_metadata = (\{.*\});').findall(season_data)[0]
			filter = re.compile('filter: (\[.*\]),').findall(season_data)[0]
			filter_menu = simplejson.loads(filter)
			section_menu = simplejson.loads(section_metadata, object_pairs_hook = ordereddict.OrderedDict)
			for section_data in section_menu.itervalues():
				section_id = section_data['sectionId']
				section_title = section_data['title']
				if section_data['display_seasons'] and filter_menu:
					for season_item in reversed(filter_menu):
						if season_item['premiumCount'] != season_item['total_count'] or addon.getSetting('cbs_use_login') == 'true':
							season_title = season_item['title']
							season_number = season_item['season']
							unlocked_episodes = int(season_item['total_count']) - int(season_item['premiumCount'])
							locked_episodes = season_item['premiumCount']
							season_url = FULLEPISODESWITHSEASON % (section_id, season_number)
							seasons.append((section_title + ' ' + season_title,  SITE, 'episodes', season_url, locked_episodes, unlocked_episodes ))
				else:
					seasons.append((section_title,  SITE, 'episodes', FULLEPISODES % section_id, -1, -1))
		except Exception, e:
			print "Exception: ", e
	except Exception, e:
			print "Exception: ", e
	return seasons

def episodes(episode_url = common.args.url):
	episodes = []
	episode_data = connection.getURL(episode_url)
	episode_json = simplejson.loads(episode_data)['result']
	episode_menu = episode_json['data']
	title = episode_json['title']
	for episode_item in episode_menu:
		if episode_item['status'] == 'AVAILABLE' or (addon.getSetting('cbs_use_login') == 'true' and episode_item['status'] == 'PREMIUM'):
			videourl = episode_item['streaming_url']
			HD = False
			url = BASE + episode_item['url']
			episode_duration = int(common.format_seconds(episode_item['duration']))
			episode_airdate = common.format_date(episode_item['airdate'], '%m/%d/%y')
			if len(episode_item['label']) < len(episode_item['title']) and episode_item['label']:
				episode_name = episode_item['label']
			else:
				episode_name = episode_item['title']
			try:
				season_number = int(episode_item['season_number'])
			except:
				season_number = -1
			try:
				episode_number = int(episode_item['episode_number'])
			except:
				episode_number = -1
			try:
				episode_thumb = episode_item['thumb']['large']
			except:
				episode_thumb = None
			episode_plot = episode_item['description']
			try:
				episode_mpaa = re.compile('\((.*)\)$').findall(episode_plot)[0]
			except:
				episode_mpaa = None
			show_title = episode_item['series_title']
			episode_expires = episode_item['expiry_date']
			episode_type = episode_item['type']
			if url is not None:
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
								'mpaa' : episode_mpaa,
								'TVShowTitle': show_title}
				infoLabels = common.enrich_infolabels(infoLabels, episode_expires)
				episodes.append((u, episode_name, episode_thumb, infoLabels, 'list_qualities', HD, episode_type))
			else:
				pass
	return episodes

def lookup_meta(url):
	if addon.getSetting('cbs_use_login') == 'true':
		loadcookie = True
	else:
		loadcookie = False
	data = connection.getURL(url, loadcookie = loadcookie)
	episode_pid = re.compile("\.pid\s?=\s?'?(.*?)'?[&;]").findall(data)[0]
	return episode_pid

def list_qualities(video_url = common.args.url):
	bitrates = []
	if 'http://' in video_url:
		pid = lookup_meta(video_url)
	else:
		pid = video_url
	video_url = EPISODE % pid
	video_data = connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	if  video_tree.find('param', attrs = {'name' : 'isException', 'value' : 'true'}) is None:
		video_url2 = video_tree.switch.find_all('video')
		for video in video_url2:
			bitrate = video['system-bitrate']
			display = int(bitrate) / 1024
			bitrates.append((display, bitrate))
		return bitrates
	else:
		common.show_exception(video_tree.ref['title'], video_tree.ref['abstract'])

def play_video(video_url = common.args.url):
	if  addon.getSetting('cbs_use_login') == 'true':
		username = addon.getSetting('cbs_username')
		password = addon.getSetting('cbs_password')
		login_values = values = {'j_username' : username, 'j_password' : password, '_remember_me' : '1' }
		login_response = connection.getURL(LOGIN_URL, login_values, savecookie = True)
		response = simplejson.loads(login_response)
		if response['success'] == False:
			common.show_exception(NAME, response['messages'])
	try:
		qbitrate = common.args.quality
	except:
		qbitrate = None
	closedcaption = None
	if 'http://' in video_url:
		pid = lookup_meta(video_url)
	else:
		pid = video_url
	video_url = EPISODE % pid
	video_data = connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	if  video_tree.find('param', attrs = {'name' : 'isException', 'value' : 'true'}) is None:
		video_rtmp = video_tree.meta
		playpath_url = None
		if video_rtmp is not None:
			base_url = video_rtmp['base']
			if qbitrate is None:
				video_url2 = video_tree.switch.find_all('video')
				lbitrate = -1
				hbitrate = -1
				sbitrate = int(addon.getSetting('quality')) * 1024
				for video_index in video_url2:
					bitrate = int(video_index['system-bitrate'])
					if bitrate < lbitrate or lbitrate == -1:
						lbitrate = bitrate
						lplaypath_url = video_index['src']	
					if bitrate > hbitrate and bitrate <= sbitrate:
						hbitrate = bitrate
						playpath_url = video_index['src']	
				if playpath_url is None:
					playpath_url = lplaypath_url
			else:
				bitrate = qbitrate 
				playpath_url = video_tree.switch.find('video', attrs = {'system-bitrate' : qbitrate})['src']
			if '.mp4' in playpath_url:
				playpath_url = 'mp4:' + playpath_url
			else:
				playpath_url = playpath_url.replace('.flv', '')
			try:
				closedcaption = video_tree.find('param', attrs = {'name' : 'ClosedCaptionURL'})['value']
				if closedcaption == '':
					closedcaption = None
			except:
				pass
			if (addon.getSetting('enablesubtitles') == 'true') and (closedcaption is not None):
					convert_subtitles(closedcaption)
			finalurl = base_url + ' playpath=' + playpath_url + ' swfurl=' + SWFURL + ' swfvfy=true'
		item = xbmcgui.ListItem( path = finalurl)
		try:
			item.setThumbnailImage(common.args.thumb)
		except:
			pass
		try:
			item.setInfo('Video', {	'title' : common.args.name,
									'season' : common.args.season_number,
									'episode' : common.args.episode_number})
		except:
			pass
		xbmcplugin.setResolvedUrl(pluginHandle, True, item)
		if (addon.getSetting('enablesubtitles') == 'true') and (closedcaption is not None):
			while not xbmc.Player().isPlaying():
				xbmc.sleep(100)
			xbmc.Player().setSubtitles(ustvpaths.SUBTITLE)
	else:
		common.show_exception(video_tree.ref['title'], video_tree.ref['abstract'])

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
	subtitle_data = connection.getURL(closedcaption, connectiontype = 0)
	subtitle_data = BeautifulSoup(subtitle_data, 'html.parser', parse_only = SoupStrainer('div'))
	srt_output = ''
	lines = subtitle_data.find_all('p')
	for i, line in enumerate(lines):
		if line is not None:
			sub = clean_subs(common.smart_utf8(line))
			start_time = common.smart_utf8(line['begin'].replace('.', ','))
			end_time = common.smart_utf8(line['end'].replace('.', ','))
			str_output += str(i + 1) + '\n' + start_time + ' --> ' + end_time + '\n' + sub + '\n\n'
	file = open(ustvpaths.SUBTITLE, 'w')
	file.write(str_output)
	file.close()
