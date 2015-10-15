#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import main_aenetwork

SITE = "aetv"
NAME = "A&E"
ALIAS = ["AETV"]
DESCRIPTION = "A&E is Real Life. Drama.  Now reaching more than 99 million homes, A&E is television that you can't turn away from; where unscripted shows are dramatic and scripted dramas are authentic.  A&E offers a diverse mix of high quality entertainment ranging from the network's original scripted series to signature non-fiction franchises, including the Emmy-winning 'Intervention,' 'Dog The Bounty Hunter,' 'Hoarders,' 'Paranormal State' and 'Criss Angel Mindfreak,' and the most successful justice shows on cable, including 'The First 48' and 'Manhunters.'  The A&E website is located at www.aetv.com."
SHOWS = "http://wombatapi.aetv.com/shows2/ae"
SEASONSEPISODE = "https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles2/episode/ae?show_name=%s&get_season"
SEASONSCLIPS = "https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles2/clip/ae?show_name=%s&get_season"
EPISODES = "https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles2/episode/ae?show_name=%s&filter_by=season&filter_value=%d"
CLIPS = "https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles2/clip/ae?show_name=%s&filter_by=season&filter_value=%d"

def masterlist():
	return main_aenetwork.masterlist(SITE, SHOWS)

def seasons(url = common.args.url):
	return main_aenetwork.seasons(SITE, SEASONSEPISODE, SEASONSCLIPS, EPISODES, CLIPS, url)

def episodes(url = common.args.url):
	return main_aenetwork.episodes(SITE, url)

def play_video():
	main_aenetwork.play_video()

def list_qualities():
	main_aenetwork.list_qualities()
