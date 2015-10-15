#!/usr/bin/python
# -*- coding: utf-8 -*-#
import common
import main_aenetwork

SITE = "history"
NAME = "History"
ALIAS = ["H2"]
DESCRIPTION = "HISTORY and HISTORY HD are the leading destinations for revealing, award-winning original non-fiction series and event-driven specials that connect history with viewers in an informative, immersive and entertaining manner across multiple platforms. Programming covers a diverse variety of historical genres ranging from military history to contemporary history, technology to natural history, as well as science, archaeology and pop culture. Among the network's program offerings are hit series such as Ax Men, Battle 360, How The Earth Was Made, Ice Road Truckers, Pawn Stars and The Universe, as well as acclaimed specials including 102 Minutes That Changed America, 1968 with Tom Brokaw, King, Life After People, Nostradamus: 2012 and Star Wars: The Legacy Revealed. HISTORY has earned four Peabody Awards, seven Primetime Emmy' Awards, 12 News & Documentary Emmy' Awards and received the prestigious Governor's Award from the Academy of Television Arts & Sciences for the network's Save Our History' campaign dedicated to historic preservation and history education. Take a Veteran to School Day is the network's latest initiative connecting America's schools and communities with veterans from all wars. The HISTORY web site, located at www.history.com, is the definitive historical online source that delivers entertaining and informative content featuring broadband video, interactive timelines, maps, games, podcasts and more."
SHOWS = "http://wombatapi.aetv.com/shows2/history"
SEASONSEPISODE = "https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles/episode/history?show_name=%s&get_season"
SEASONSCLIPS = "https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles/clip/history?show_name=%s&get_season"
EPISODES = "https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles/episode/history?show_name=%s&filter_by=season&filter_value=%d"
CLIPS = "https://mobileservices-a.akamaihd.net/jservice/wombattpservice/show_titles/clip/history?show_name=%s&filter_by=season&filter_value=%d"

def masterlist():
	return main_aenetwork.masterlist(SITE, SHOWS)

def seasons(url = common.args.url):
	return main_aenetwork.seasons(SITE, SEASONSEPISODE, SEASONSCLIPS, EPISODES, CLIPS, url)

def episodes(url = common.args.url):
	return main_aenetwork.episodes(SITE, url)

def play_video():
	main_aenetwork.play_video()

def list_qualities():
	main_aenetwork.list_qualities()
