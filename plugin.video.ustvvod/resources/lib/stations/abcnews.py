#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import main_abcdisney

BRANDID = '003'
PARTNERID = '585231'
SITE = 'abcnews'
NAME = "ABC News"
DESCRIPTION = "ABC News is responsible for all of the ABC Television Network's news programming on a variety of platforms: TV, radio and the Internet."

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
