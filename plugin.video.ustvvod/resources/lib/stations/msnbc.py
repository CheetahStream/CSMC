#!/usr/bin/python
# -*- coding: utf-8 -*-
import common
import connection
import main_nbcu
import re
import simplejson
import sys
import ustvpaths
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

addon = xbmcaddon.Addon()
pluginHandle = int(sys.argv[1])


SITE = "msnbc"
NAME = "MSNBC"
DESCRIPTION = "MSNBC is an American basic cable and satellite news television channel that is owned by the NBCUniversal News Group, a unit of the NBCUniversal Television Group division of NBCUniversal. The channel features news, information, and political opinion programming. Its name was derived from the most common abbreviations for Microsoft and the National Broadcasting Company. MSNBC and msnbc.com were founded in 1996 as partnerships of Microsoft and General Electric's NBC unit, which is now NBCUniversal. The online partnership of msnbc.com ended on July 16, 2012 and the site was rebranded as NBCNews.com. MSNBC shares the NBC logo of a rainbow peacock with its sister channels NBC, CNBC, and NBC Sports Network. Beginning in the mid-2000s, MSNBC assumed an increasingly liberal stance in its opinion programming. In October 2010, it publicly acknowledged this with a marketing campaign it called \"Lean Forward\". Further, in September of 2013, MSNBC launched its revamped official website under the tagline, \"What Progressives Have Been Waiting For.\" As of August 2013, approximately 94,519,000 American households (82.77% of households with television) receive MSNBC"
SHOWS = "http://www.msnbc.com/api/1.0/shows.json"
BASE = "http://www.msnbc.com/"
PLAYLIST = "http://data.nbcnews.com/VideoRendering/PlaylistTemplate/%s"
FEED = "http://feed.theplatform.com/f/2E2eJC/%s?form=json"

def masterlist():
	master_db = []
	master_data = connection.getURL(SHOWS)
	master_menu = simplejson.loads(master_data)['shows']
	for master_item in master_menu:
		master_name = master_item['show']['title']
		season_url = season_url = BASE + master_item['show']['path']
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def seasons(season_url = common.args.url):
	seasons = []
	season_data = connection.getURL(season_url)
	try:
		playlist = re.compile('"playlists":\s*(\[.*?\])', re.DOTALL).findall(season_data)[0]
		season_menu = simplejson.loads(playlist)
		for season_item in season_menu:
			seasons.append((season_item['name'],  SITE, 'episodes', FEED % season_item['guid'], -1, -1))
	except:
		try:
			season_tree = BeautifulSoup(season_data, 'html.parser', parse_only = SoupStrainer('div'))
			season_source = season_tree.find('div', id = 'TPVideoPlaylistTaxonomyContainer')['source']
			playlist_url = PLAYLIST % season_source
			playlist_data = connection.getURL(playlist_url)
			playlist_data = playlist_data.replace('$pdk.NBCplayer.ShowPlayerTaxonomy.GetList(', '').replace(');', '')
			season_menu = simplejson.loads(playlist_data)
			for season_item in season_menu['playlistTaxonomy']:
				season_name =  season_item['reference']['name']
				season_url = FEED % season_item['reference']['feed']
				seasons.append((season_name, SITE, 'episodes', season_url, -1, -1))
		except Exception:
			pass
	return seasons

def episodes(url = common.args.url):
	try:
		return main_nbcu.episodes(SITE, url, False)
	except Exception as e:
		print "Exception: ", e
	
def play_video(video_url = common.args.url):
	hbitrate = -1
	sbitrate = int(addon.getSetting('quality')) * 1024
	closedcaption = None
	video_data = connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	finalurl = video_tree.video['src']
	try:
		closedcaption = video_tree.find('textstream', type = 'text/vtt')['src']
	except:
		pass
	if (addon.getSetting('enablesubtitles') == 'true') and (closedcaption is not None):
			convert_subtitles(closedcaption)
	xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path = finalurl))
	if (addon.getSetting('enablesubtitles') == 'true') and (closedcaption is not None):
		while not xbmc.Player().isPlaying():
			xbmc.sleep(100)
		xbmc.Player().setSubtitles(ustvpaths.SUBTITLE)
		
def clean_subs(data):
	br = re.compile(r'<br.*?>')
	tag = re.compile(r'<.*?>')
	apos = re.compile(r'&amp;apos;')
	gt = re.compile(r'&gt;')
	sub = br.sub('\n', data)
	sub = tag.sub(' ', sub)
	sub = apos.sub('\'', sub)
	sub = gt.sub('>', sub)
	return sub

def convert_subtitles(closedcaption):
	str_output = ''
	subtitle_data = connection.getURL(closedcaption, connectiontype = 0)
	str_output = clean_subs(subtitle_data)
	file = open(ustvpaths.SUBTITLE, 'w')
	file.write(str_output)
	file.close()
