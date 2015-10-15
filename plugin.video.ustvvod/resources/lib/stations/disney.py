#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import main_abcdisney

SITE = "disney"
NAME = "Disney"
ALIAS = ["Disney Channel"]
DESCRIPTION = "Disney Channel is a 24-hour kid-driven, family inclusive television network that taps into the world of kids and families through original series and movies. It is currently available on basic cable and satellite in more than 98 million U.S. homes and in nearly 400 million households via 42 Disney Channels and free-to-air broadcast partners around the world."
BRANDID = "004"
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
