#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import main_natgeo

SITE = "natgeowild"
NAME = "Nat Geo Wild"
DESCRIPTION = "Experience the best, most intimate encounters with wildlife ever seen on television.  Backed by its unparallel reputation and blue chip programming, Nat Geo Wild brings viewers documentaries entirely focused on the animal kingdom and the world it inhabits.  From the most remote environments, to the forbidding depths of our oceans, to the protected parks in our backyards, Nat Geo Wild uses spectacular cinematography and intimate storytelling to take viewers on unforgettable journeys into the wild world.  Nat Geo Wild launched in August 2006 and is now available in Hong Kong, Singapore, the U.K., Australia, Latin America, France, Italy, Portugal, Turkey and other territories in Europe.  Nat Geo Wild HD launched in the U.K. in March 2009 and is also available in Poland.  Additional launches are expected globally."
SHOWS = "http://video.nationalgeographic.com/video/nat-geo-wild?gs=all"
SPECIALS = "http://video.nationalgeographic.com/video/nat-geo-wild/specials-2/"
BASE = "http://video.nationalgeographic.com/"

def masterlist():
	return main_natgeo.masterlist(SITE, SHOWS, SPECIALS)

def seasons(url = common.args.url):
	return main_natgeo.seasons(SITE, BASE, url)

def episodes(url = common.args.url):
	return main_natgeo.episodes(SITE, url)

def play_video():
	main_natgeo.play_video(SITE)

def list_qualities():
	return main_natgeo.list_qualities(SITE)
