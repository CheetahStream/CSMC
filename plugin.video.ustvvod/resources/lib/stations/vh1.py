#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import main_viacom

SITE = "vh1"
NAME = "VH1"
DESCRIPTION = "VH1 connects viewers to the music, artists and pop culture that matter to them most with series, specials, live events, exclusive online content and public affairs initiatives. VH1 is available in 90 million households in the U.S. VH1 also has an array of digital services including VH1 Classic, VH1 Soul and VSPOT, VH1's broadband channel. Connect with VH1 at www.VH1.com."
API = "http://api.mtv.com/api/Txb9fUYFsDtE/"
SHOWS = API + "promolist/10395044.json"

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
