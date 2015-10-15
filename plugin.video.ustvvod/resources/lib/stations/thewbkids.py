#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import connection
import simplejson
import sys
import urllib
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup

pluginHandle = int(sys.argv[1])

SITE = "thewbkids"
NAME = "WB Kids, The"
DESCRIPTION = "The KidsWB Collection of Scooby-Doo, Looney Toons, Batman: The Brave and the Bold, Hanna-Barbera, DC and Warner stars under one roof."
SHOWS = "http://www.kidswb.com/video"
EPISODES = "http://www.kidswb.com/video/playlists?pid=channel&chan="
VIDEOURL = "http://metaframe.digitalsmiths.tv/v2/WBtv/assets/%s/partner/11?format=json"

def masterlist():
	master_db = []
	master_data = connection.getURL(SHOWS)
	master_tree = BeautifulSoup(master_data, 'html.parser').find('ul', id = 'channelCarousel_ul')
	master_menu = master_tree.find_all('a')
	for master_item in master_menu:
		master_name = master_item.img['alt'].strip()
		season_url = master_item['title']
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db
	
def seasons(episode_url = common.args.url):
	return [('Clips',  SITE, 'episodes', episode_url, -1, -1)]

def episodes(episode_url = common.args.url):
	episodes = []
	episode_data = connection.getURL(EPISODES + episode_url)
	episode_data2 = simplejson.loads(episode_data)['list_html']
	episode_tree = BeautifulSoup(episode_data2, 'html.parser').find('ul', id = 'videoList_ul')
	if episode_tree:
		episode_menu = episode_tree.find_all('li', recursive = False)
		for episode_item in episode_menu:
			infoLabels={}
			url = episode_item['id'][6:]
			episode_thumb = episode_item.img['src'].replace('103x69', '640x480')
			episode_name = episode_item.span.string
			episode_plot = episode_item.find(id = 'viddesc_' + url).string
			show_name = episode_item.find(id = 'vidtitle_' + url).string
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels={	'title' : episode_name,
							'plot' : episode_plot,
							'TVShowTitle' : show_name }
			episodes.append((u, episode_name, episode_thumb, infoLabels, None, False, 'Clip'))
	return episodes

def play_video(video_url = common.args.url):
	video_data = connection.getURL(VIDEOURL % video_url.split('/')[-1])
	video_tree = simplejson.loads(video_data)['videos']['limelight700']['uri']
	rtmpsplit = video_tree.split('mp4:')
	finalurl = rtmpsplit[0] + ' playpath=mp4:' + rtmpsplit[1]
	xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path = finalurl))
