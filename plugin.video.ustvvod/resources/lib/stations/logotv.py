#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import main_viacom

SITE = "logotv"
NAME = "LogoTV"
ALIAS = ["Logo"]
DESCRIPTION = "Logo TV is an American digital cable and satellite television channel that is owned by Viacom Media Networks. The channel focuses on lifestyle programming aimed primarily at lesbian, gay, bisexual, and transgender people."
API = "http://api.mtv.com/api/hVqrnHigT6Rq/"
SHOWS = API + "promolist/10394912.json"

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
