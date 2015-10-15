#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import connection
import main_viacom
import re
import sys
import urllib
from bs4 import BeautifulSoup

SITE = "nickteen"
NAME = "Nick Teen"
ALIAS = ["TeenNick"]
DESCRIPTION = "Launched in April 2002, TeenNick (formerly named The N) features 24-hours of teen programming. Our award-winning and original programming, including Degrassi: The Next Generation, Beyond the Break, The Best Years and The Assistants, presents sharp and thoughtful content that focuses on the real life issues teens face every day. On our Emmy winning website, www.Teennick.com, fans get complete access to behind-the-scenes interviews, pictures and videos, plus a robust community of 2 million members who interact with message boards, user profiles and blogs. TeenNick's broadband channel, The Click, features full-length episodes of the network's hit original series along with outtakes, sneak peeks and webisodes of TeenNick series created exclusively for broadband. The Click provides teens with the ability to create video mash-ups and watch, comment on and share content from their favorite TeenNick shows with all of their friends, wherever they go."
BASE = "http://www.teennick.com"
BASE2 = "http://media.nick.com/"
SHOWS = "http://www.teennick.com/ajax/videos/all-videos?sort=date+desc&start=0&page=1&updateDropdown=true&viewType=collectionAll"
CLIPS = "http://www.teennick.com/ajax/videos/all-videos/%s?type=videoItem"
FULLEPISODES = "http://www.teennick.com/ajax/videos/all-videos/%s?type=fullEpisodeItem"

def masterlist():
	master_db = []
	master_data = connection.getURL(SHOWS)
	master_tree = BeautifulSoup(master_data, 'html.parser')
	master_menu = master_tree.find_all('option')
	master_menu.pop(0)
	for master_item in master_menu:
		master_name = master_item.string
		season_url = master_item['value']
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons(season_url = common.args.url):
	seasons = []
	season_data = connection.getURL(FULLEPISODES % season_url)
	try:
		season_menu = int(BeautifulSoup(season_data, 'html.parser').find('div', class_ = 'total-videos').text.split(' ')[0])
	except:
		season_menu = 0
	if season_menu > 0:
		season_url2 = FULLEPISODES % season_url
		seasons.append(('Full Episodes',  SITE, 'episodes', season_url2, -1, -1))
	season_data2 = connection.getURL(CLIPS % season_url)
	try:
		season_menu2 = int(BeautifulSoup(season_data2, 'html.parser').find('div', class_ = 'total-videos').text.split(' ')[0])
	except:
		season_menu2 = 0
	if season_menu2 > 0:
		season_url3 = CLIPS % season_url
		seasons.append(('Clips',  SITE, 'episodes', season_url3, -1, -1))
	return seasons

def episodes(episode_url = common.args.url):
	episodes = []
	episode_data = connection.getURL(episode_url)
	episode_tree = BeautifulSoup(episode_data, 'html.parser')
	episodes = add_videos(episode_tree.find('ul', class_ = 'large-grid-list'))
	pagedata = episode_tree.find('span', class_ = 'pagination-next')
	if pagedata:
		try:
			episodes.extend(episodes(episode_url.split('?')[0] + pagedata.a['href'] + '&type=' + episode_url.rsplit('=', 1)[1]))
		except:
			pass
	return episodes

def add_videos(episode_tree):
	episodes = []
	episode_menu = episode_tree.find_all('li', recursive = False)
	for episode_item in episode_menu:
		try:
			show_name = common.args.name
		except:
			show_name = None
		episode_link = episode_item.h4.a
		episode_name = episode_link.text
		url = BASE + episode_link['href']
		episode_thumb = episode_item.find('img')['src'].split('?')[0]
		episode_plot = episode_item.find('p', class_ = 'description').text
		u = sys.argv[0]
		u += '?url="' + urllib.quote_plus(url) + '"'
		u += '&mode="' + SITE + '"'
		u += '&sitemode="play_video"'
		infoLabels = {	'title' : episode_name,
						'plot' : episode_plot,
						'tvshowtitle' : show_name }
		episodes.append((u, episode_name, episode_thumb, infoLabels, 'list_qualities', False, 'Full Episode'))
	return episodes

def play_video(video_url = common.args.url):
	video_data = connection.getURL(video_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	mgid = BeautifulSoup(video_data, 'html.parser').find('div', attrs = {'data-uri' : True})['data-uri']
	video_url2 = mgid
	main_viacom.play_video(BASE, video_url2)	

def list_qualities(video_url = common.args.url):
	video_data = connection.getURL(video_url, header = {'X-Forwarded-For' : '12.13.14.15'})
	try:
		video_url2 = re.compile('<meta content="http://media.mtvnservices.com/fb/(.+?).swf" property="og:video"/>').findall(video_data)[0]
	except:
		video_url2 = re.compile("NICK.unlock.uri = '(.+?)';").findall(video_data)[0]
	return main_viacom.list_qualities(BASE, video_url2, media_base = BASE2)
