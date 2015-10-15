#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import connection
import main_nbcu
import re
import ustvpaths
from bs4 import BeautifulSoup, SoupStrainer

SITE = "oxygen"
NAME = "Oxygen"
DESCRIPTION = "Oxygen Media is a multiplatform lifestyle brand that delivers relevant and engaging content to young women who like to \"live out loud.\" Oxygen is rewriting the rulebook for women's media by changing how the world sees entertainment from a young woman's point of view.  Through a vast array of unconventional and original content including \"Bad Girls Club,\" \"Dance Your Ass Off\" and \"Tori & Dean: Home Sweet Hollywood,\" the growing cable network is the premier destination to find unique and groundbreaking unscripted programming.   A social media trendsetter, Oxygen is a leading force in engaging the modern young woman, wherever they are, with popular features online including OxygenLive, shopOholic, makeOvermatic, tweetOverse and hormoneOscope.  Oxygen is available in 76 million homes and online at www.oxygen.com, or on mobile devices at wap.oxygen.com.  Oxygen Media is a service of NBC Universal."
SHOWS = "http://feed.theplatform.com/f/AqNl-B/7rsRlZPHdpCt/categories?form=json&sort=order"
CLIPS = "http://feed.theplatform.com/f/AqNl-B/iyAsU_4kQn1I?count=true&form=json&byCustomValue={fullEpisode}{false}&byCategories=%s"
FULLEPISODES = "http://feed.theplatform.com/f/AqNl-B/iyAsU_4kQn1I?count=true&form=json&byCustomValue={fullEpisode}{true}&byCategories=%s"
SWFURL = "http://features.oxygen.com/videos/pdk/swf/flvPlayer.swf"

def masterlist():
	return main_nbcu.masterlist(SITE, SHOWS)

def seasons(season_url = common.args.url):
	return main_nbcu.seasons(SITE, FULLEPISODES, CLIPS,  None, season_url)

def episodes(episode_url = common.args.url):
	return main_nbcu.episodes(SITE, episode_url)

def list_qualities():
	return main_nbcu.list_qualities()

def play_video():
	try:
		main_nbcu.play_video(SWFURL)
	except Exception, e:
		print "Exception", e
		print traceback.format_exc()

def clean_subs(data):
	br = re.compile(r'<br.*?>')
	tag = re.compile(r'<.*?>')
	space = re.compile(r'\s\s\s+')
	apos = re.compile(r'&amp;apos;')
	sub = br.sub('\n', data)
	sub = tag.sub(' ', sub)
	sub = space.sub(' ', sub)
	sub = apos.sub('\'', sub)
	return sub

def convert_subtitles(closedcaption):
	str_output = ''
	subtitle_data = connection.getURL(closedcaption, connectiontype = 0)
	subtitle_data = BeautifulSoup(subtitle_data, 'html.parser', parse_only = SoupStrainer('div'))
	lines = subtitle_data.find_all('p')
	for i, line in enumerate(lines):
		if line is not None:
			sub = clean_subs(common.smart_utf8(line))
			start_time_rest, start_time_msec = line['begin'].rsplit(':',1)
			start_time = common.smart_utf8(start_time_rest + ',' + start_time_msec)
			try:
				end_time_rest, end_time_msec = line['end'].rsplit(':',1)
				end_time = common.smart_utf8(end_time_rest + ',' + end_time_msec)
			except:
				continue
			str_output += str(i + 1) + '\n' + start_time + ' --> ' + end_time + '\n' + sub + '\n\n'
	file = open(ustvpaths.SUBTITLE, 'w')
	file.write(str_output)
	file.close()
