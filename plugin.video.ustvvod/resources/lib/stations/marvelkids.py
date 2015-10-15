#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import connection
import re
import simplejson
import sys
import urllib
import xbmcgui
import xbmcplugin
import xbmcaddon
from bs4 import BeautifulSoup

pluginHandle = int (sys.argv[1])
addon = xbmcaddon.Addon()

SITE = "marvelkids"
NAME = "Marvel Kids"
DESCRIPTION = "Marvel started in 1939 as Timely Publications, and by the early 1950s had generally become known as Atlas Comics. Marvel's modern incarnation dates from 1961, the year that the company launched Fantastic Four and other superhero titles created by Stan Lee, Jack Kirby, Steve Ditko, and others. Marvel counts among its characters such well-known properties as Spider-Man, the X-Men, the Fantastic Four, Iron Man, the Hulk, Thor, Captain America and Daredevil; antagonists such as the Green Goblin, Magneto, Doctor Doom, Galactus, and the Red Skull. Most of Marvel's fictional characters operate in a single reality known as the Marvel Universe, with locations that mirror real-life cities such as New York, Los Angeles and Chicago."
SHOWS = "http://www.marvelkids.com/videos"

def masterlist():
	master_db = []
	master_data = connection.getURL(SHOWS)
	master_menu = BeautifulSoup(master_data, 'html.parser').find_all('h2', text = re.compile('"'))
	for master_item in master_menu:
		master_name = master_item.text.replace('"', '').replace(' Videos', '')
		season_url = master_item.text
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons(season_url = common.args.url):
	seasons = []
	seasons.append(('Clips',  SITE, 'episodes', season_url, -1, -1))
	return seasons

def episodes(episode_url = common.args.url):
	episodes = []
	episode_data = connection.getURL(SHOWS)
	episode_tree = BeautifulSoup(episode_data, 'html.parser')
	episode_carousel = episode_tree.find('h2', text = re.compile(episode_url)).parent.parent
	for episode_item in episode_carousel.find_all('span', class_ = 'col'):
		try:
			episode_name = re.compile('"(.*)"').findall(episode_item.h3.string)[0]
		except:
			episode_name = episode_item.h3.string
		print episode_name
		episode_thumb = episode_item.img['src']
		try:
			episode_url = episode_item.a['href']
		except:
			episode_url = ''
		url = episode_url
		u = sys.argv[0]
		u += '?url="' + urllib.quote_plus(episode_url)  + '"'
		u += '&mode="' + SITE + '"'
		u += '&sitemode="play_video"'
		infoLabels={'title' : episode_name }
		episodes.append((u, episode_name, episode_thumb, infoLabels, None, False, 'Clip'))
	return episodes

def play_video(video_url = common.args.url):
	stored_size = 0
	video_data = connection.getURL(video_url)
	video_model = re.compile('model: *(\[.*\]),\s*videoPlayer: _player,', re.DOTALL).findall(video_data)[0]
	video_model = simplejson.loads(video_model)
	try:
		sbitrate = long(addon.getSetting('quality')) * 1000
	except Exception as e:
		print "Exception: ", e
	hbitrate = -1
	print sbitrate
	for item in video_model[0]['flavors']:
		if item['format'] == 'mp4' and item['security_profile'][0] == 'progressive':
			bitrate = item['bitrate']
			if bitrate > hbitrate and bitrate <= sbitrate:
				hbitrate = bitrate
				url = item['url']
	finalurl = url
	xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path = finalurl))
