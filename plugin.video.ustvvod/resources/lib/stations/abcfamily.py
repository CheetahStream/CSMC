#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import main_abcdisney

BRANDID = "002"
PARTNERID = "585231"
SITE = "abcfamily"
NAME = "ABC Family"
DESCRIPTION = "ABC Family's programming is a combination of network-defining original series and original movies, quality acquired series and blockbuster theatricals. ABC Family features programming reflecting today's families, entertaining and connecting with adults through relatable stories about today's relationships, told with a mix of diversity, passion, humor and heart. Targeting Millennial viewers ages 14-34, ABC Family is advertiser supported."

def masterlist():
	return main_abcdisney.masterlist(SITE, BRANDID)

def seasons(url = common.args.url):
	return main_abcdisney.seasons(SITE, BRANDID, url)

def episodes(url = common.args.url):
	return main_abcdisney.episodes(SITE, url)

def play_video():
	main_abcdisney.play_video(SITE, BRANDID, PARTNERID)

def list_qualities():
	return main_abcdisney.list_qualities(SITE, BRANDID, PARTNERID)
