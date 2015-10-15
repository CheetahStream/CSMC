#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import connection
import main_turner
from bs4 import BeautifulSoup

SITE = "cartoon"
NAME = "Cartoon Network"
DESCRIPTION = "Cartoon Network (CartoonNetwork.com), currently seen in more than 97 million U.S. homes and 166 countries around the world, is Turner Broadcasting System, Inc.'s ad-supported cable service now available in HD offering the best in original, acquired and classic entertainment for youth and families.  Nightly from 10 p.m. to 6 a.m. (ET, PT), Cartoon Network shares its channel space with Adult Swim, a late-night destination showcasing original and acquired animated and live-action programming for young adults 18-34 "
SHOWS = "http://www.cartoonnetwork.com/video/staged/CN2.mobile.configuration.xml"
EPISODE = "http://www.cartoonnetwork.com/video-seo-svc/episodeservices/getCvpPlaylist?networkName=CN2&id=%s"
CLIPS = "http://www.cartoonnetwork.com/video-seo-svcepisodeSearch/getAllEpisodes?networkName=CN2&filterByPlatform=mobile&filterByEpisodeType=CLI-CLI&offset=0&sortByDate=DESC&filterByCollectionId=%s&filterBySeasonNumber=%s"
FULLEPISODES = "http://www.cartoonnetwork.com/video-seo-svcepisodeSearch/getAllEpisodes?networkName=CN2&filterByPlatform=mobile&filterByEpisodeType=TVE&offset=0&sortByDate=DESC&filterByCollectionId=%s&filterBySeasonNumber=%s"
HLSPATH = "toon"

def masterlist():
	master_db = []
	master_dict = {}
	master_data = connection.getURL(SHOWS)
	master_tree = BeautifulSoup(master_data, 'html.parser')
	master_menu = master_tree.allcollections.find_all('collection')
	for master_item in master_menu:
		master_name = common.smart_utf8(master_item['name'])
		if '[AD]' not in master_name and 'Unlocked' not in master_name:
			tvdb_name = common.get_show_data(master_name, SITE, 'seasons')[-1]
			season_url = master_item['id'] 
			season_url = season_url + '#tveepisodes='
			try:
				for season in master_item.tveepisodes.find_all('season'):
					season_url = season_url + '-' + season['number']
			except:
				pass
			season_url = season_url + '#clips='
			try:
				for season in master_item.clips.find_all('season'):
					if season['number'] != '':
						season_url = season_url + '-' + season['number']
				else:
					season_url = season_url + '-' + '*'
			except:
				pass
			master_db.append((master_name,  SITE, 'seasons', season_url))
	return master_db

def seasons(season_string = common.args.url):
	seasons = []
	collection_id = season_string.split('#')[0]
	tve = season_string.split('#')[1].split('=')[1][1:]
	clips = season_string.split('#')[2].split('=')[1][1:]
	for season in tve.split('-'):
		if season:
			seasons.append(('Season ' + season,  SITE, 'episodes', FULLEPISODES % (collection_id, season),-1,-1))
	for season in clips.split('-'):
		if season:
			if season != '*':
				display = 'Clips Season ' + season
			else:
				display = 'Specials'
			seasons.append((display,  SITE, 'episodes', CLIPS % (collection_id, season.replace('*', '')),-1, -1))
	return seasons

def episodes(url = common.args.url):
	return main_turner.episodes(SITE, url)

def play_video(video_id = common.args.url):
	main_turner.play_video(SITE, EPISODE, HLSPATH)

def list_qualities():
	return main_turner.list_qualities(SITE, EPISODE)
