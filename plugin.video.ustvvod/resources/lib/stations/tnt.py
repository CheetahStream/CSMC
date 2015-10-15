#!/usr/bin/python
# -*- coding: utf-8 -*-
import connection
import common
import HTMLParser
import main_turner
import urllib
import sys
from bs4 import BeautifulSoup, SoupStrainer

SITE = "tnt"
NAME = "TNT"
DESCRIPTION = "TNT, one of cable's top-rated networks, is television's destination for drama. Seen in 99.6 million households, the network is home to such original series as The Closer, starring Kyra Sedgwick; Leverage, starring Timothy Hutton; and Dark Blue, starring Dylan McDermott; the upcoming Rizzoli & Isles, starring Angie Harmon and Sasha Alexander; Memphis Beat, with Jason Lee; Men of a Certain Age, with Ray Romano, Andre Braugher and Scott Bakula; and Southland, from Emmy'-winning producer John Wells (ER). TNT also presents such powerful dramas as Bones, Supernatural, Las Vegas, Law & Order, CSI: NY, Cold Case and Numb3rs; broadcast premiere movies; compelling primetime specials, such as the Screen Actors Guild Awards'; and championship sports coverage, including NASCAR and the NBA. The NCAA men's basketball tournament will appear on TNT beginning in 2011. TNT is available in high-definition."
SHOWS = "http://www.tntdrama.com/mobile/smartphone/showList.jsp"
MOVIES = "http://www.tntdrama.com/mobile/ipad/feeds/movies.jsp"
CLIPSSEASON = "http://www.tntdrama.com/mobile/ipad/feeds/getFranchiseCollections.jsp?franchiseID=%s"
CLIPS = "http://www.tntdrama.com/mobile/ipad/feeds/franchiseEpisode.jsp?franchiseID=%s&type=0&collectionId=%s"
FULLEPISODES = "http://www.tntdrama.com/mobile/ipad/feeds/franchiseEpisode.jsp?franchiseID=%s&type=1"
EPISODE = "http://www.tntdrama.com/video/content/services/cvpXML.do?id=%s"
WEBSHOWS = "http://www.tntdrama.com/shows/index.html"
WEBEPISODE = "http://www.tntdrama.com/service/cvpXml?titleId=%s"
HLSPATH = "tnt"

def masterlist():
	return main_turner.masterlist(NAME, MOVIES, SHOWS, SITE, WEBSHOWS)
	
def seasons(url = common.args.url):
	return main_turner.seasons(SITE, FULLEPISODES, CLIPSSEASON, CLIPS, WEBSHOWS, url)

def episodes(url = common.args.url):
	return main_turner.episodes_json(SITE, url)
	
def episodes_web():
	episodes = []
	master_name = common.args.url
	webdata = connection.getURL(WEBSHOWS)
	web_tree =  BeautifulSoup(webdata, 'html.parser', parse_only = SoupStrainer('div', id = 'page-shows'))
	show = web_tree.find('h2', text = master_name).parent.parent
	for item in show.findAll('div', class_ = 'item'):
		print item.find('span')
		if item.find('span', contenttypename = "FullEpisode") is not None:
			url = WEBEPISODE % item.span['titleid']
			print item.find(itemprop = 'duration').string.replace(' minutes', '')
			print int(item.find(itemprop = 'duration').string.replace(' minutes', '')) * 60
			try:
				episode_duration = item.find(itemprop = 'duration').string.replace(' minutes', '').strip()# * 60
			except:
				episode_duration = -1
			try:
				episode_plot = HTMLParser.HTMLParser().unescape(item.find(itemprop = 'description').string)
			except:
				episode_plot = ''
			episode_name = item.img['alt']
			try:
				season_number = int(item.find(itemprop = 'seasonNumber').string)
			except:
				season_number = -1
			try:
				episode_number =  int(item.find(itemprop = 'episodeNumber').string)
			except:
				episode_number = -1
			try:
				episode_thumb = item.find(itemprop = 'thumbnail')['data-standard']
			except:
				episode_thumb = None
			episode_mpaa = item.span['showrating']
			u = sys.argv[0]
			u += '?url="' + urllib.quote_plus(url) + '"'
			u += '&mode="' + SITE + '"'
			u += '&sitemode="play_video"'
			infoLabels={	'title' : episode_name,
							'durationinseconds' : episode_duration,
							'season' : season_number,
							'episode' : episode_number,
							'plot' : episode_plot,
							'mpaa' : episode_mpaa,
							'TVShowTitle' : master_name}
			episodes.append((u, episode_name, episode_thumb, infoLabels, 'list_qualities', False, 'Full Episode'))
	return episodes


def play_video():
	main_turner.play_video(SITE, EPISODE, HLSPATH)

def list_qualities():
	return main_turner.list_qualities(SITE, EPISODE)
