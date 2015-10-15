#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import main_abcdisney

SITE = "disneyjunior"
NAME = "Disney Junior"
DESCRIPTION = "Disney Junior, part of Disney Channels Worldwide, is a global television and online brand expressly for kids age 2-7. Disney Junior invites mom and dad to join their child in the Disney experience of magical, musical and heartfelt stories and characters, both classic and new, while incorporating specific learning and development themes designed for young children"
BRANDID = "008"
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
