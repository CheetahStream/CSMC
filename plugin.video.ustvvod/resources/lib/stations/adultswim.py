#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import connection
import main_turner
import plistlib
from bs4 import BeautifulSoup

SITE = "adultswim"
NAME = "Adult Swim"
DESCRIPTION = "Cartoon Network (CartoonNetwork.com), currently seen in more than 97 million U.S. homes and 166 countries around the world, is Turner Broadcasting System, Inc.'s ad-supported cable service now available in HD offering the best in original, acquired and classic entertainment for youth and families.  Nightly from 10 p.m. to 6 a.m. (ET, PT), Cartoon Network shares its channel space with Adult Swim, a late-night destination showcasing original and acquired animated and live-action programming for young adults 18-34 "
SHOWS = "http://www.adultswim.com/mobile/tools/feeds/shows.plist"
SEASONSCLIPS = "http://www.adultswim.com/videos/api/v0/videos?limit=0&offset=0&sortByDate=DESC&filterByEpisodeType=PRE,CLI&filterByCollectionId=%s&networkName=AS&filterByAuthType=true"
SEASONSEPISODES = "http://www.adultswim.com/videos/api/v0/videos?limit=0&offset=0&sortByDate=DESC&filterByEpisodeType=EPI,TVE&filterByCollectionId=%s&networkName=AS&filterByAuthType=true"
SEASONSCLIPSEXTRA = "http://www.adultswim.com/videos/api/v0/videos?limit=1&offset=0&sortByDate=DESC&filterByEpisodeType=PRE,CLI&filterByCollectionId=%s&networkName=AS&filterByAuthType=true"
SEASONSEPISODESEXTRA = "http://www.adultswim.com/videos/api/v0/videos?limit=1&offset=0&sortByDate=DESC&filterByEpisodeType=EPI&filterByCollectionId=%s&networkName=AS&filterByAuthType=true"
CLIPS = "http://www.adultswim.com/videos/api/v0/videos?limit=50&offset=0&sortByDate=DESC&filterByEpisodeType=CLI&filterByCollectionId=%s&filterByAuthType=true&networkName=AS"
FULLEPISODES = "http://www.adultswim.com/videos/api/v0/videos?limit=50&offset=0&sortByDate=DESC&filterByEpisodeType=EPI,TVE&filterByCollectionId=%s&filterByAuthType=true&networkName=AS&filterByPlatform=mobile"
EPISODE = "http://www.adultswim.com/videos/api/v0/assets?id=%s&networkName=AS"
HLSPATH = "adultswim"

def masterlist():
	master_db = []
	master_dict = {}
	master_data = connection.getURL(SHOWS)
	master_tree = plistlib.readPlistFromString(master_data)
	for master_item in master_tree:
		master_name = common.smart_utf8(master_item['name'])
		tvdb_name = common.get_show_data(master_name, SITE, 'seasons')[-1]
		if tvdb_name not in master_dict.keys():
			master_dict[tvdb_name] = master_item['show-id']
		else:
			master_dict[tvdb_name] = master_dict[tvdb_name] + ',' + master_item['show-id']
	for master_name in master_dict:
		season_url = master_dict[master_name]
		master_db.append((master_name,  SITE, 'seasons', season_url))
	return master_db

def seasons(collection_ids = common.args.url):
	seasons = []
	for collection_id in collection_ids.split(','):
		if ',' not in collection_ids:
			season_url = SEASONSEPISODES
		else:
			season_url = SEASONSEPISODESEXTRA
		season_data = connection.getURL(season_url % collection_id)
		season_tree = BeautifulSoup(season_data, 'html.parser')
		episode_count = int(season_tree.episodes['totalitems'])
		if episode_count > 0:
			if ',' not in collection_ids:
				display = 'Episodes'
			else:
				display = 'Episodes - %s' % season_tree.episode['collectiontitle']
			seasons.append((display,  SITE, 'episodes', FULLEPISODES % collection_id, -1, -1))
	for collection_id in collection_ids.split(','):
		if ',' not in collection_ids:
			seasonclips_url = SEASONSCLIPS
		else:
			seasonclips_url = SEASONSCLIPSEXTRA
		season_data2 = connection.getURL(seasonclips_url % collection_id)
		season_tree2 = BeautifulSoup(season_data2, 'html.parser')
		episode_count = int(season_tree2.episodes['totalitems'])
		if episode_count > 0:
			if ',' not in collection_ids:
				display = 'Clips'
			else:
				display = 'Clips - %s' % season_tree2.episode['collectiontitle']
			seasons.append((display,  SITE, 'episodes', CLIPS % collection_id, -1, -1))

	return seasons

def episodes(url = common.args.url):
	return main_turner.episodes(SITE, url)

def play_video():
	main_turner.play_video(SITE, EPISODE, HLSPATH)

def list_qualities():
	return main_turner.list_qualities(SITE, EPISODE)
