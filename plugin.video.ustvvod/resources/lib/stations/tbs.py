#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import main_turner

SITE = "tbs"
NAME = "TBS"
DESCRIPTION = "TBS, a division of Turner Broadcasting System, Inc., is television's top-rated comedy network and is available in 100.1 million households.  It serves as home to such original comedy series as My Boys, Neighbors from Hell, Are We There Yet? and Tyler Perry's House of Payne and Meet the Browns; the late-night hit Lopez Tonight, starring George Lopez, and the upcoming late-night series starring Conan O'Brien; hot contemporary comedies like Family Guy and The Office; specials like Funniest Commercials of the Year; special events, including star-studded comedy festivals in Chicago; blockbuster movies; and hosted movie showcases."
SHOWS = "http://www.tbs.com/mobile/smartphone/android/showList.jsp"
MOVIES = "http://www.tbs.com/mobile/ipad/feeds/movies.jsp"
CLIPSSEASON = "http://www.tbs.com/mobile/ipad/feeds/getFranchiseCollections.jsp?franchiseID=%s"
CLIPS = "http://www.tbs.com/mobile/ipad/feeds/franchiseEpisode.jsp?franchiseID=%s&type=0&collectionId=%s"
FULLEPISODES = "http://www.tbs.com/mobile/ipad/feeds/franchiseEpisode.jsp?franchiseID=%s&type=1"
EPISODE = "http://www.tbs.com/video/content/services/cvpXML.do?id=%s"
HLSPATH = "tbs"

def masterlist():
	return main_turner.masterlist(NAME, MOVIES, SHOWS, SITE)

def seasons(url = common.args.url):
	return main_turner.seasons(SITE, FULLEPISODES, CLIPSSEASON, CLIPS, None, url)

def episodes(url = common.args.url):
	return main_turner.episodes_json(SITE, url)

def play_video():
	main_turner.play_video(SITE, EPISODE, HLSPATH)

def list_qualities():
	return main_turner.list_qualities(SITE, EPISODE)
