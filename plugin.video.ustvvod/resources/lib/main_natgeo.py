#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import connection
import m3u8
import re
import sys
import urllib
import xbmcaddon
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

addon = xbmcaddon.Addon()
pluginHandle = int(sys.argv[1])

BASE = 'http://video.nationalgeographic.com'

def masterlist(SITE, SHOWS, SPECIALS = None):
	master_db = []
	root_dict = {}
	root_url = SHOWS
	root_data = connection.getURL(root_url)
	root_tree = BeautifulSoup(root_data, 'html.parser', parse_only = SoupStrainer('div', id = 'grid-frame'))
	root_menu = root_tree.find_all('div', class_ = 'media-module')
	for root_item in root_menu:
		root_name = root_item.find('div', class_ = 'title').text
		season_url = BASE + root_item.a['href']
		if '-1' not in season_url:
			tvdb_name = common.get_show_data(root_name, SITE, 'seasons')[-1]
			root_name = root_name + '#' + season_url 
			if tvdb_name not in root_dict.keys():
				root_dict[tvdb_name] = root_name
			else:
				root_dict[tvdb_name] = root_dict[tvdb_name] + '|' + root_name
	for root_name in root_dict:
		season_url = root_dict[root_name]
		master_db.append((root_name, SITE, 'seasons', season_url))
	more = root_tree.find('a', class_ = 'load-more')
	if more:
		master_db.extend(masterlist(SITE, BASE + more['href']))
	return master_db

def seasons(SITE, BASE, season_urls):
	seasons = []
	for season_url in season_urls.split('|'):
		season_data = connection.getURL(season_url.split('#')[1])
		season_tree = BeautifulSoup(season_data, 'html.parser')
		season_menu = season_tree.find('ul', class_ = 'grid-sections')
		for season_item in season_menu.find_all('li', class_ = ""):
			season_name = season_item.a.string.strip()
			if '|' in season_urls:
				season_name = season_url.split('#')[0] + ' ' + season_name  
			season_url = BASE + season_item.a['href']
			seasons.append((season_name,  SITE, 'episodes', season_url, -1, -1))
	return seasons

def episodes(SITE, episode_url = common.args.url):
	episodes = []
	if '#' in episode_url:
		episode_url = episode_url.split('#')[1]
	episode_data = connection.getURL(episode_url)
	episode_tree = BeautifulSoup(episode_data, 'html.parser', parse_only = SoupStrainer('div', class_ = 'show'))
	try:
		episodes = add_videos(episode_tree, SITE)
	except:
		print "Can't add video"
	more = episode_tree.find('a', class_ = 'load-more')
	if more:
		episode_data = connection.getURL(BASE + more['href'])
		episode_tree = BeautifulSoup(episode_data, 'html.parser')
		episodes = add_videos(episode_tree, SITE)
	return episodes

def add_videos(episode_tree, SITE):
	episodes = []
	episode_menu = episode_tree.find_all('div', class_ = 'media-module')
	show_name = episode_tree.find('h1').text
	for episode_item in episode_menu:
		episode_name = episode_item.a['data-title']
		episode_thumb = urllib.unquote_plus(episode_item.a.img['data-src'].split('url=')[1])
		try:
			episode_duration = common.format_seconds(episode_item.find('div', class_='timestamp').text.strip())
		except:
			episode_duration = -1
		url = episode_item.a['href']
		u = sys.argv[0]
		u += '?url="' + urllib.quote_plus(url) + '"'
		u += '&mode="' + SITE + '"'
		u += '&sitemode="play_video"'
		infoLabels = {	'title' : episode_name,
						'durationinseconds' : episode_duration,
						'TVShowTitle' : show_name }
		episodes.append((u, episode_name, episode_thumb, infoLabels, 'list_qualities', False, 'Full Episode'))
	return episodes
	
def play_video(SITE):
	video_url = common.args.url
	try:
		qbitrate = common.args.quality
	except:
		qbitrate = None
	hbitrate = -1
	lbitrate = -1
	sbitrate = int(addon.getSetting('quality'))
	video_data = connection.getURL(video_url)
	smil_url =  re.compile('video_auth_playlist_url = "(.*)"').findall(video_data)[0]
	smil_data = connection.getURL(smil_url + '&manifest=m3u')
	video_tree2 = BeautifulSoup(smil_data, 'html.parser')
	video_url3 = video_tree2.video['src']
	video_data3 = connection.getURL(video_url3)
	video_url4 = m3u8.parse(video_data3)
	video_url5 = None
	for video_index in video_url4.get('playlists'):
		bitrate = int(video_index.get('stream_info')['bandwidth'])
		if qbitrate is None:
			try:
				codecs =  video_index.get('stream_info')['codecs']
			except:
				codecs = ''
			if (bitrate < lbitrate or lbitrate == -1) and 'mp4a.40.2' != codecs:
						lbitrate = bitrate
						lvideo_url5 = video_index.get('uri')
			if bitrate > hbitrate and bitrate <= (sbitrate * 1000) and codecs != 'mp4a.40.2':
				hbitrate = bitrate
				video_url5 = video_index.get('uri')
		elif  bitrate == qbitrate:
				video_url5 = video_index.get('uri')
	if video_url5 is None:
		video_url5 = lvideo_url5
	finalurl = video_url5
	item = xbmcgui.ListItem(path = finalurl)
	if qbitrate is not None:
		item.setThumbnailImage(common.args.thumb)
		item.setInfo('Video', {	'title' : common.args.name,
						'season' : common.args.season_number,
						'episode' : common.args.episode_number,
						'TVShowTitle' : common.args.show_title })
	xbmcplugin.setResolvedUrl(pluginHandle, True, item)

def list_qualities(SITE):
	video_url = common.args.url
	bitrates = []
	video_data = connection.getURL(video_url)
	smil_url =  re.compile("window.video_auth_playlist_url = '(.*)'").findall(video_data)[0]
	smil_data = connection.getURL(smil_url + '&manifest=m3u')
	video_tree2 = BeautifulSoup(smil_data, 'html.parser')
	video_url3 = video_tree2.video['src']
	video_data3 = connection.getURL(video_url3)
	video_url4 = m3u8.parse(video_data3)
	for video_index in video_url4.get('playlists'):
		try:
			codecs =  video_index.get('stream_info')['codecs']
		except:
			codecs = ''
		if  codecs != 'mp4a.40.2':
			bitrate = int(video_index.get('stream_info')['bandwidth'])
			display = int(bitrate) / 1000
			bitrates.append((display, bitrate))
	return bitrates
