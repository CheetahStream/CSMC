#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import main_abcdisney

BRANDID = "001"
PARTNERID = "585231"
SITE = "abcchannel"
NAME = "ABC"
DESCRIPTION = "ABC Television Network provides broadcast programming to more than 220 affiliated stations across the U.S. The Network encompasses ABC News, which is responsible for news programming on television and other digital platforms; ABC Entertainment Group, a partnership between ABC Studios and ABC Entertainment responsible for the network's primetime and late-night entertainment programming; ABC Daytime, producer of the network's successful cache of daytime programming; as well as ABC Kids, the Network's children's programming platform. ABC's multiplatform business initiative includes the Interactive Emmy Award-winning broadband player on ABC.com."

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
