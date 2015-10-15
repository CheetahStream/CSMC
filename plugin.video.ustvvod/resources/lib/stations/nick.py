#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import connection
import main_viacom
import re
import simplejson
import sys
import urllib

SITE = "nick"
NAME = "Nickelodeon"
DESCRIPTION = "Nickelodeon, now in its 31st year, is the number-one entertainment brand for kids. It has built a diverse, global business by putting kids first in everything it does. The company includes television programming and production in the United States and around the world, plus consumer products, online, recreation, books and feature films. Nickelodeon's U.S. television network is seen in more than 100 million households and has been the number-one-rated basic cable network for 16 consecutive years."
BASE = "http://nick.com"
FULLEPISODES = "http://www.nick.com/apps/api/v2/content-collection?apiKey=gve7v8ti&rows=40&series=%s&start=0&types=episodes"
SHOWS = "http://www.nick.com/apps/api/v2/editorial-content-categories/stars?apiKey=gve7v8ti"
CLIPS = "http://www.nick.com/apps/api/v2/content-collection?apiKey=gve7v8ti&killDBSequenceNumber=&rows=40&series=%s&start=0&types=video"
FEED = "http://udat.mtvnservices.com/service1/dispatch.htm?feed=nick_arc_player_prime&plugin.stage=live&mgid=%s"
EPISODE_URL ="http://legacy.nick.com/videos/clip/%s.html"

def masterlist():
	master_db = []
	master_data = connection.getURL(SHOWS, header = {'X-Forwarded-For' : '12.13.14.15'})
	showdata = simplejson.loads(master_data)
	for data in showdata:
		master_name = data['title'].replace('&', 'and')
		season_url = data['urlKey']
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons(season_url = common.args.url):
	seasons = []
	season_data = connection.getURL(FULLEPISODES % season_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	try:
		count = int(simplejson.loads(season_data)['meta']['count'])
	except:
		count = 0
	if count > 0:
		season_url2 = FULLEPISODES % season_url + '&start=0&rows=' + str(count)
		seasons.append(('Full Episodes',  SITE, 'episodes', season_url2, -1, -1))
	season_data2 = connection.getURL(CLIPS % season_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	try: 
		count = int(simplejson.loads(season_data2)['meta']['count'])
	except: 
		count = 0
	if count > 0:
		season_url3 = CLIPS % season_url + '&start=0&rows=' + str(count)
		seasons.append(('Clips',  SITE, 'episodes', season_url3, -1, -1))
	return seasons

def episodes(episode_url = common.args.url):
	episodes  = []
	episode_data = connection.getURL(episode_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	episode_menu = simplejson.loads(episode_data)['results']
	for episode_item in episode_menu:
		try:
			show_name = episode_item['seriesTitle']
		except:
			show_name = ''
		try:
			episode_name = episode_item['title'].split(':')[1].replace('"', '')
		except:
			episode_name = episode_item['title']
		url = EPISODE_URL % episode_item['urlKey']
		try:
			episode_plot = episode_item['description']
		except:
			episode_plot = ''
		try:
			image = episode_item['images'][0]['assets'][0]['path']
			episode_thumb = BASE + image
		except:
			episode_thumb = None
		try:
			episode_duration = common.format_seconds(episode_item['duration'])
		except:
			episode_duration = -1
		episode_type = ' '.join(episode_item['urlKey'].split('-')[-2:]).title()
		try:
			episode_number = episode_item['episodeNumber'][1:]
		except:
			episode_number = -1
		try:
			episode_season = episode_item['episodeNumber'][0]
		except:
			episode_season = -1
		try:
			episode_mpaa = episode_item['rating']
		except:
			episode_mpaa = None
		try:
			episode_airdate = episode_item['airDate']
			episode_airdate = common.format_date(episode_airdate.split('.')[0], '%Y-%m-%dT%H:%M:%S')
		except:
			episode_airdate = -1
		try:
			episode_expires = episode_item['availableUntil']
			episode_expires = episode_expires.split('.')[0]
		except:
			episode_expires = -1
		u = sys.argv[0]
		u += '?url="' + urllib.quote_plus(url) + '"'
		u += '&mode="' + SITE + '"'
		u += '&sitemode="play_video"'
		infoLabels = {	'title' : episode_name,
						'plot' : episode_plot,
						'durationinseconds' : episode_duration,
						'TVShowTitle' : show_name,
						'episode' : episode_number,
						'season' : episode_season,
						'mpaa' : episode_mpaa,
						'premiered' : episode_airdate}
		episodes.append((u, episode_name, episode_thumb, infoLabels, 'list_qualities', False, episode_type))
	return episodes

def play_video(video_url = common.args.url):
	video_data = connection.getURL(video_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	video_url2 = re.compile('<meta content="http://media.mtvnservices.com/fb/(.+?).swf" property="og:video"/>').findall(video_data)[0]
	feed_url = FEED % video_url2
	main_viacom.play_video(BASE, feed_url)

def list_qualities(video_url = common.args.url):
	video_data = connection.getURL(video_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	video_url2 = re.compile('<meta content="http://media.mtvnservices.com/fb/(.+?).swf" property="og:video"/>').findall(video_data)[0]
	return main_viacom.list_qualities(BASE, video_url2)
