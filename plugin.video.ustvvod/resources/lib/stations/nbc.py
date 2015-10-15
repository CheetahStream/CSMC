#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import common
import connection
import HTMLParser
import m3u8
import ordereddict
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

SITE = "nbc"
NAME = "NBC"
DESCRIPTION = "NBC Entertainment develops and schedules programming for the network's primetime, late-night, and daytime schedules. NBC's quality programs and balanced lineup have earned the network critical acclaim, numerous awards, and ratings success. The network has earned more Emmy Awards than any network in television history. NBC's roster of popular scripted series includes critically acclaimed comedies like Emmy winners The Office, starring Steve Carell, and 30 Rock, starring Alec Baldwin and Tina Fey. Veteran, award-winning dramas on NBC include Law & Order: SVU, Chuck, and Friday Night Lights. Unscripted series for NBC include the hits The Biggest Loser, Celebrity Apprentice, and America's Got Talent. NBC's late-night story is highlighted by The Tonight Show with Jay Leno, Late Night with Jimmy Fallon, Last Call with Carson Daly, and Saturday Night Live. NBC Daytime's Days of Our Lives consistently finishes among daytime's top programs in the valuable women 18-34 category. Saturday mornings the network broadcasts Qubo on NBC, a three-hour block that features fun, entertaining, and educational programming for kids, including the award-winning, 3-D animated series Veggie Tales."
BASE = "http://nbc.com"
SHOWS = "http://www.nbc.com/ajax/dropdowns-global/America-New_York"
EPISODES = "http://www.nbc.com/data/node/%s/video_carousel"
VIDEOPAGE = "http://videoservices.nbcuni.com/player/clip?clear=true&domainReq=www.nbc.com&geoIP=US&clipId=%s"
SMIL_BASE = "http://video.nbcuni.com/"
SMIL = "http://link.theplatform.com/s/NnzsPC/%s?mbr=true&mbr=true&player=Onsite%%20Player&policy=43674&manifest=m3u&format=SMIL&Tracking=true&Embedded=true&formats=MPEG4,F4M,FLV,MP3"
TONIGHT_SHOW_FEED = "%s/content/a/filter-items/?type=video"

def masterlist():
	master_db = []
	master_data = connection.getURL(SHOWS)
	json = simplejson.loads(master_data)['menu_html']
	master_menu =  re.compile('<li class="views-row .*?">.*?<div>\s*<div><a href="(.*?)">.*?<div class="field .*?">\n\s*(.*?)</div>.*?</li>' , re.DOTALL).findall(json)
	for season_url, master_name in master_menu:
		master_name = common.smart_unicode(master_name).strip()
		master_name = HTMLParser.HTMLParser().unescape(master_name)
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons(season_url = common.args.url):
	seasons = []
	base_url = season_url
	season_dict = ordereddict.OrderedDict({})
	if 'the-tonight-show' in season_url:
		seasons = add_show_thetonightshow(season_url)
		return seasons
	has_episodes = False
	video_url = season_url + '/video'
	episode_url = season_url 
	for season_url in (video_url, episode_url ):
		season_data = connection.getURL(season_url)
		season_menu = re.compile('<div class="nbc_mpx_carousel.*?" id="(nbc_mpx_carousel_\d+)">\s*<h2.*?>(.*?)</h2>', re.DOTALL).findall(season_data)
		for season_id, season_title in season_menu:
			try:
				if 'ALSO' not in season_title:
					tag = re.compile(r'<.*?>')
					season_title = tag.sub('', season_title)
					season_title = re.sub(' +',' ', season_title)
					season_title = season_title.strip().title()
					if not (season_title == 'Full Episodes' and has_episodes):
						season_node = season_id.split('_')[-1]
						if season_title not in season_dict.keys():
							season_dict[season_title] =  EPISODES % season_node
							if 'full episodes' == season_title.lower() or 'Season' in season_title:
								has_episodes = True
			except:
				pass
	if not has_episodes:
		episode_data = connection.getURL(base_url + '/episodes')
		episode_menu = re.compile('src="(.*?)".*?<a href="([^"]*?)" class="watch-now-onion-skin">.*?(\d+) min.*?Season (\d+).*?Episode \d+(\d{2}).*?Air date (\d{2}/\d{2}/\d{2}).*?<div class="episode-title dotdotdot"><a href=".*?">(.*?)</a></div>.*?<p>(.*?)</p>', re.DOTALL).findall(episode_data)
		if episode_menu:
			seasons.append(('Full Episodes', SITE, 'episodes',  base_url + '/episodes', -1, -1))
	for season_title in season_dict:
		season_url = season_dict[season_title]
		seasons.append((season_title, SITE, 'episodes',  season_url, -1, -1))
	return seasons

def episodes(episode_url = common.args.url):
	episodes = []
	if 'the-tonight-show' in episode_url:
		if 'Clips' in episode_url:
			return add_videos_thetonightshow(episode_url.split('#')[0], 'segment')
		else:
			return add_videos_thetonightshow(episode_url.split('#')[0], 'episode')
		return
	episode_data = connection.getURL(episode_url)
	if 'video_carousel' in episode_url:
		episode_json = simplejson.loads(episode_data)
		episode_menu = episode_json['entries']
		for episode_item in episode_menu:
			try:
				episode_restricted = episode_item['restricted']
			except:
				episode_restricted = 'free'
			try:
				if  episode_restricted != 'auth':
					pid = episode_item['mainReleasePid']	
					url = SMIL % pid	
					try:
						episode_duration = int(episode_item['duration'].replace(' min','')) * 60
					except:
						episode_duration = -1
					episode_plot = HTMLParser.HTMLParser().unescape(episode_item['description'])
					epoch = int(episode_item['pubDate']) / 1000
					episode_airdate = common.format_date(epoch = epoch)
					episode_name = HTMLParser.HTMLParser().unescape(episode_item['title'])
					show_title = episode_item['showShortName']
					try:
						season_number = int(episode_item['season'])
					except:
						season_number = -1
					try:
						episode_number = int(episode_item['episode'])
					except:
						episode_number = -1
					try:
						episode_thumb = episode_item['images']['big']
					except:
						episode_thumb = None
					episode_type = episode_item['contentType']
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
									'TVShowTitle' : show_title
								}
					episodes.append((u, episode_name, episode_thumb, infoLabels,  'list_qualities', False, episode_type))
			except Exception as e:
				print "Episode item error",e
	else:
		episodes = []
		show_title = re.compile('<h2 class="show-title"><a href=".*?">(.*?)</a></h2>').findall(episode_data)[0]
		episode_menu = re.compile('src="(.*?)".*?<a href="([^"]*?)" class="watch-now-onion-skin">.*?(\d+) min.*?Season (\d+).*?Episode \d+(\d{2}).*?Air date (\d{2}/\d{2}/\d{2}).*?<div class="episode-title dotdotdot"><a href=".*?">(.*?)</a></div>.*?<p>(.*?)</p>', re.DOTALL).findall(episode_data)
		for episode_thumb, episode_url, episode_duration,season_number, episode_number, episode_airdate, episode_name, episode_plot in episode_menu:
			episode_name = HTMLParser.HTMLParser().unescape(episode_name)
			try:
				episode_duration = int(episode_duration) * 60
			except:
				episode_duration = -1
			season_number = int(season_number)
			episode_number =  int(episode_number)
			episode_airdate = common.format_date(episode_airdate,'%m/%d/%y')
			try:
				url = BASE + episode_url
				u = sys.argv[0]
				u += '?url="' + urllib.quote_plus(url) + '"'
				u += '&mode="' + SITE + '"'
				u += '&sitemode="play_video"'
				infoLabels={	'title' : episode_name,
								'durationinseconds' : episode_duration,
								'season' : season_number,
								'episode' : episode_number,
								'plot' : episode_plot,
								'TVShowTitle' : show_title,
								'premiered' : episode_airdate
							}
				episodes.append((u, episode_name, episode_thumb,  infoLabels, 'list_qualities', False, 'Full Episode'))
			except:
				pass
	return episodes

def add_show_thetonightshow(url):
	seasons = []
	seasons.append(('Full Episodes',  SITE, 'episodes', url + '#FullEpisode', -1, -1))
	seasons.append(('Clips',  SITE, 'episodes', url + '#Clips', -1, -1))
	return seasons

def add_videos_thetonightshow(url, type_, page = 1, added_episodes = []):
	episodes = []
	this_url = (TONIGHT_SHOW_FEED % url) + '&offset=' + str((page-1) * 10)
	root_data = connection.getURL(this_url)
	data = simplejson.loads(root_data)
	for video in data['content']:
		if video['type'] == type_:
			if type_ == 'episode':
				episode_name = video['name']
				episode_id = video['episodeNumber']
			else:
				episode_name = video['title']
				episode_id = video['id']
			if episode_id in added_episodes:
				continue
			added_episodes.append(episode_id)
			pid = video['videos'][0]['mpxPublicId']
			episode_url = SMIL % pid
			try:
				episode_plot = BeautifulSoup(video['description']['value'], 'html.parser').p.string
			except:
				episode_plot = ''
			try:
				episode_airdate = common.format_date(video['airDate'][:-6],'%Y-%m-%dT%H:%M:%S','%d.%m.%Y')
			except:
				episode_airdate = -1
			try:
				season_number = int(video['season'])
			except:
				season_number = -1
			try:
				episode_number = int(video['episodeNumber'])
			except:
				episode_number = -1
			try:
				episode_thumb = video['images'][0]['bitImageSmall']
			except:
				episode_thumb = None
			if video['type'] == 'episode':
				episode_type = 'Full Episode'
			else:
				episode_type = 'Clip'
			show_name = video['images'][0]['description']
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(episode_url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels={	'title' : episode_name,
							'season' : season_number,
							'episode' : episode_number,
							'plot' : episode_plot,
							'premiered' : episode_airdate,
							'TVShowTitle' : show_name
						}
			episodes.append((u, episode_name, episode_thumb, infoLabels, 'list_qualities', False, episode_type))
	if page < int(addon.getSetting('maxpages')):
		episodes.extend(add_videos_thetonightshow(url, type_, page + 1, added_episodes))
	return episodes

def play_video(video_url = common.args.url, tonightshow = False):
	try:
		qbitrate = common.args.quality
	except:
		qbitrate = None
	closedcaption = None
	video_data = connection.getURL(video_url)
	if 'link.theplatform.com' not in video_url:
		video_tree =  BeautifulSoup(video_data, 'html.parser')
		player_url = video_tree.find('div', class_ = 'video-player-full')['data-mpx-url']
		player_data = connection.getURL(player_url)
		player_tree =  BeautifulSoup(player_data, 'html.parser')
		smil_url = player_tree.find('link', type = "application/smil+xml")['href']
		video_data = connection.getURL(smil_url + '&manifest=m3u&format=SMIL')
	smil_tree = BeautifulSoup(video_data, 'html.parser')
	if smil_tree.find('param', attrs = {'name' : 'isException', 'value' : 'true'}) is None:
		video_url2 = smil_tree.video['src']	
		try:
			closedcaption = smil_tree.textstream['src']
		except:
			pass
		if addon.getSetting('sel_quality') == 'true' or qbitrate is not None or  int(xbmc.getInfoLabel( "System.BuildVersion" )[:2]) < 14 or common.use_proxy() :
			print "*****************Selection"
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
		else:
			print "******************************** bypass selection"
			player._localHTTPServer = False
			finalurl = video_url2
		if (addon.getSetting('enablesubtitles') == 'true') and (closedcaption is not None):
			convert_subtitles(closedcaption)
			player._subtitles_Enabled = True
		item = xbmcgui.ListItem(path = finalurl)
		try:

			item.setThumbnailImage(common.args.thumb)
		except:
			pass
		try:
			item.setInfo('Video', {	'title' : common.args.name,
									'season' : common.args.season_number,
									'episode' : common.args.episode_number,
									'TVShowTitle' : common.args.show_title})
		except:
			pass
		xbmcplugin.setResolvedUrl(pluginHandle, True, item)
		while player.is_active:
				player.sleep(250)
	else:
		common.show_exception(smil_tree.ref['title'], smil_tree.ref['abstract'])

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

def list_qualities(video_url = common.args.url):
	video_data = connection.getURL(video_url)
	if 'link.theplatform.com' not in video_url:
		video_tree =  BeautifulSoup(video_data, 'html.parser')
		player_url = video_tree.find('div', class_ = 'video-player-full')['data-mpx-url']
		player_data = connection.getURL(player_url)
		player_tree =  BeautifulSoup(player_data, 'html.parser')
		smil_url = player_tree.find('link', type = "application/smil+xml")['href']
		video_data = connection.getURL(smil_url + '&manifest=m3u&format=SMIL')
	bitrates = []
	smil_tree = BeautifulSoup(video_data, 'html.parser')
	video_url2 = smil_tree.video['src']
	clip_id = smil_tree.video.find('param', attrs = {'name' : 'clipId'})
	if clip_id is not None:
		clip_id = clip_id['value']
		video_url = VIDEOPAGE % clip_id
		video_data = connection.getURL(video_url)
		video_tree = BeautifulSoup(video_data, 'html.parser')
		clip_url = SMIL_BASE + video_tree.clipurl.string	
		smil_data = connection.getURL(clip_url)
		smil_tree = BeautifulSoup(smil_data, 'html.parser')
		video_url2 = smil_tree.find_all('video')
		for video_index in video_url2:
			bitrate = int(video_index['system-bitrate'])
			display = int(bitrate)/1024
			bitrates.append((display, bitrate))
	else:
		m3u_master_data = connection.getURL(video_url2)
		m3u_master = m3u8.parse(m3u_master_data)
		for video_index in m3u_master.get('playlists'):
			try:
				codecs =  video_index.get('stream_info')['codecs']
			except:
				codecs = ''
			if  codecs != 'mp4a.40.2':
				bitrate = int(video_index.get('stream_info')['bandwidth'])
				display = int(bitrate)/1024
				bitrates.append((display, bitrate))
	return bitrates
