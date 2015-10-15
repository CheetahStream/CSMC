#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import main_abcdisney

SITE = "disneyxd"
NAME = "Disney XD"
DESCRIPTION = "Disney XD is a basic cable channel and multi-platform brand showcasing a compelling mix of live-action and animated programming for kids aged 6-14, hyper-targeting boys (while still including girls) and their quest for discovery, accomplishment, sports, adventure and humor. Disney XD branded content spans television, online, mobile and VOD platforms. The programming includes series, movies and short-form, as well as sports-themed programming developed with ESPN."
BRANDID = "009"
PARTNERID = "585231"

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
