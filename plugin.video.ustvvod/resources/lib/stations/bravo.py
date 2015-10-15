#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import connection
import main_nbcu
from bs4 import BeautifulSoup

SITE = "bravo"
NAME = "Bravo"
DESCRIPTION = "With more breakout stars and critically-acclaimed original series than any other network on cable, Bravo's original programming - from hot cuisine to haute couture - delivers the best in food, fashion, beauty, design and pop culture to the most engaged and upscale audience in cable. Consistently one of the fastest growing top 20 ad-supported cable entertainment networks, Bravo continues to translate buzz into reality with critically-acclaimed breakout creative competition and docu-series, including the Emmy and James Beard Award-winning No. 1 food show on cable \"Top Chef,\" two-time Emmy Award winner \"Kathy Griffin: My Life on the D-List,\" the 14-time Emmy nominated \"Inside the Actors Studio,\" the hit series \"Shear Genius,\" \"Top Chef Masters,\" \"Flipping Out,\" \"The Rachel Zoe Project,\" \"Tabatha's Salon Takeover,\" \"Million Dollar Listing,\" \"The Millionaire Matchmaker,\" and the watercooler sensation that is \"The Real Housewives\" franchise. Bravo reaches its incredibly unique audience through every consumer touch point and across all platforms on-air, online and on the go, providing the network's highly-engaged fans with a menu of options to experience the network in a four-dimensional manner. Bravo is a program service of NBC Universal Cable Entertainment, a division of NBC Universal one of the world's leading media and entertainment companies in the development, production, and marketing of entertainment, news and information to a global audience. Bravo has been an NBC Universal cable network since December 2002 and was the first television service dedicated to film and the performing arts when it launched in December 1980. For more information visit www.bravotv.com"
SHOWS = "http://www.bravotv.com/shows"
CLIPS = "http://feed.theplatform.com/f/PHSl-B/QiuoTr7I1m13?count=true&form=json&byCustomValue={fullEpisode}{false},{show}{%s}"
FULLEPISODES = "http://feed.theplatform.com/f/PHSl-B/QiuoTr7I1m13?count=true&form=json&byCustomValue={fullEpisode}{true},{show}{%s}"
SWFURL = "http://pdk.theplatform.com/5.5.11/pdk/swf/flvPlayer.swf"

def masterlist():
	master_db = []
	master_doubles = []
	master_dict = {}
	master_data = connection.getURL(SHOWS)
	master_menu = BeautifulSoup(master_data, 'html.parser').find_all('article', class_ = 'all-shows')
	for master_item in master_menu:
		master_name = master_item.a['title']
		if master_name not in master_doubles:
			tvdb_name = common.get_show_data(master_name, SITE, 'seasons')[-1]
			if tvdb_name not in master_dict.keys():
				master_dict[tvdb_name] = master_name
			else:
				master_dict[tvdb_name] = master_dict[tvdb_name] + ',' + master_name
			master_doubles.append(master_name)
	for master_name in master_dict:
		season_url = master_dict[master_name]
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons(url = common.args.url):
	return main_nbcu.seasons(SITE, FULLEPISODES, CLIPS, None, url)

def episodes(url = common.args.url):
	return main_nbcu.episodes(SITE, url)

def list_qualities():
	return main_nbcu.list_qualities()

def play_video():
	try:
		main_nbcu.play_video(SWFURL)
	except Exception, e:
		print "Exception: ", e
