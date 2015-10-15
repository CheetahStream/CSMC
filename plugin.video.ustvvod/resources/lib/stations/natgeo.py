#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import main_natgeo

SITE = "natgeo"
NAME = "National Geographic"
DESCRIPTION = "Critically acclaimed non-fiction. Network providing info-rich entertainment that changes the way you see the world.  A trusted source for more than 100 years, National Geographic provides NGC with unique access to the most respected scientists, journalists and filmmakers, resulting in innovative and contemporary programming of unparalleled quality.  NGC HD continues to provide spectacular imagery that National Geographic is known for in stunning high-definition.  A leader on the digital landscape, NGC HD is one of the top five HD networks and is the #1 channel viewers would most like to see in high definition for the fourth year in a row.  Additionally, the channel received some of the highest ratings in key categories, such as 'high quality,' 'information' and 'favorite' in the prestigious benchmark study among all 55 measured cable and broadcast networks. In addition, NGC VOD is a category leader. Building on its success as one of the fastest-growing cable networks year-to-year in ratings and distribution since launching in January 2001, NGC now reaches more than 70 million homes, with carriage on all major cable and satellite television providers.  Highlighted programming in 2010 includes: New episodes of Expedition Great White, the popular series, Taboo and Border Wars.  In addition, new seasons of series' WORLD'S TOUGHEST FIXES and LOCKED UP ABROAD.  2010 specials include DRUGS, INC., LOST GOLD OF THE DARK AGES and GREAT MIGRATIONS  For more information, please visit www.natgeotv.com." 
SHOWS = "http://video.nationalgeographic.com/video/national-geographic-channel?gs=all"
SPECIALS = "http://video.nationalgeographic.com/video/national-geographic-channel/specials-1/"
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
