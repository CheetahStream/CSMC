#!/usr/bin/python
# -*- coding: utf-8 -*-
import connection
import common
import main_turner
import simplejson
import sys
import urllib

SITE = "tcm"
NAME = "TCM"
DESCRIPTION = "Turner Classic Movies (TCM) is an American movie-oriented basic cable and satellite television network that is owned by the Turner Broadcasting System subsidiary of Time Warner. TCM is headquartered at the Techwood Campus in Atlanta, Georgia's Midtown business district. Historically, the channel's programming consisted mainly of featured classic theatrically released feature films from the Turner Entertainment film library – which comprises films from Warner Bros. Pictures (covering films released before 1950) and Metro-Goldwyn-Mayer (covering films released before May 1986). However, TCM now has licensing deals with other Hollywood film studios as well as its Time Warner sister company Warner Bros. (which now controls the Turner Entertainment library and its own later films), and occasionally shows somewhat more recent films."
MOVIES = "http://api.tcm.com//tcmws/v1/vod/tablet/catalog/orderBy/title.jsonp"
CLIPSSEASON = ""
CLIPS = ""
FULLEPISODES = ""
EPISODE = "http://www.tcm.com/tveverywhere/services/videoXML.do?id=%s"
HLSPATH = "tcm"

def masterlist():
	master_db = []
	master_dict = {}
	master_db.append(('--' + NAME + ' Movies',  SITE, 'episodes', 'Movie#' + MOVIES))
	return master_db

def seasons(url = common.args.url):
	return main_turner.seasons(SITE, FULLEPISODES, CLIPSSEASON, CLIPS, url)

def episodes(url = MOVIES):
	episodes = []
	if '#' in url:
		url = url.split('#')[1]
	episode_data = connection.getURL(url)
	episode_list = simplejson.loads(episode_data)
	episode_menu = episode_list['tcm']['titles']
	for episode_item in episode_menu:
		url = episode_item['vod']['contentId']
		try:
			episode_duration = str(int(episode_item['runtimeMinutes'])*60)
		except:
			episode_duration = -1
		episode_year = episode_item['releaseYear']
		try:
			episode_plot = episode_item['description']
		except:
			episode_plot = ""
		episode_name = episode_item['name']
		try:
			episode_genre = episode_item['tvGenres']
		except:
			episode_genre = ''
		try:
			episode_rating = 'Rated: %s' % episode_item['tvRating']
		except:
			episode_rating = ''
		try:
			episode_director = episode_item['tvDirectors']
		except:
			episode_director = ''
		season_number = -1
		episode_number = -1
		try:
			episode_thumb = episode_item['imageProfiles'][1]['url']
		except:
			episode_thumb = None
		episode_expires = episode_item['vod']['expiryDate']
		try:
			episode_actors = episode_item['tvParticipants'].split(',')
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
						'year' : episode_year,
						'genre' : episode_genre, 
						'mpaa'  : episode_rating,
						'director' : episode_director,
						'cast' : episode_actors}
		infoLabels = common.enrich_infolabels(infoLabels, episode_expires, '%Y-%b-%d %I:%M %p')
		episodes.append((u, episode_name, episode_thumb, infoLabels, 'list_qualities', False, 'Movie'))
	return episodes

def play_video():
	main_turner.play_video(SITE, EPISODE, HLSPATH)

def list_qualities():
	return main_turner.list_qualities(SITE, EPISODE)
