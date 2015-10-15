#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import main_viacom

SITE = "cmt"
NAME = "CMT"
DESCRIPTION = "CMT's current programming features country music-oriented shows (including country music videos and taped concerts), country lifestyle-oriented shows, older shows and movies that prominently feature country or Southern-rock music, and (especially since the late 2000s) some general entertainment programming, mainly dealing with Southern culture and life."
API = "http://api.mtv.com/api/lsfHZN1SU1bu/"
SHOWS = API + "promolist/10394940.json"

def masterlist():
	return main_viacom.masterlist(SITE, SHOWS)

def seasons(url = common.args.url):
	return main_viacom.seasons(SITE, API, url)

def episodes(url = common.args.url):
	return main_viacom.episodes(SITE, url)

def play():
	main_viacom.play_video2(API, common.args.url)

def list_qualities():
	return main_viacom.list_qualities2(API, common.args.url)
