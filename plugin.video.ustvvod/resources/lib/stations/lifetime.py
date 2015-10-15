#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import main_aenetwork

SITE = "lifetime"
NAME = "Lifetime"
DESCRIPTION = "A leading force in the entertainment industry, Lifetime Television is the highest-rated women's network, followed only by its sister channel, Lifetime Movie Network. Upon its 1984 launch, Lifetime quickly established itself as a pioneer in the growing cable universe to become the preeminent television destination and escape for women and has long been the number one female-targeted network on all of basic cable among Women 18-49, Women 25-54 and Women 18+. The Network, one of television's most widely distributed outlets, is currently seen in nearly 98 million households nationwide. Lifetime is synonymous with providing critically acclaimed, award-winning and popular original programming for women that spans movies and miniseries, dramas, comedies and reality series. In continuing this tradition, the Network has aggressively expanded its original programming slate, and, for the 2009-10 season, has amassed the most powerful line-up in Company history."
SHOWS = "http://wombatapi.aetv.com/shows2/mlt"
SEASONSEPISODE = "https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles/episode/mlt?show_name=%s&get_season"
SEASONSCLIPS = "https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles/clip/mlt?show_name=%s&get_season"
EPISODES = "https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles/episode/mlt?show_name=%s&filter_by=season&filter_value=%d"
CLIPS = "https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles/clip/mlt?show_name=%s&filter_by=season&filter_value=%d"

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
