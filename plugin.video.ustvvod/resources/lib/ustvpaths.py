#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path
import xbmc
import xbmcaddon

#Paths of the USTV VoD plugin
addon = xbmcaddon.Addon(id = 'plugin.video.ustvvod')

PLUGINPATH = addon.getAddonInfo('path')
RESOURCESPATH = os.path.join(PLUGINPATH,'resources')
DATAPATH = os.path.join(RESOURCESPATH,'data')
IMAGEPATH = os.path.join(RESOURCESPATH,'images')
LIBPATH = os.path.join(RESOURCESPATH,'lib')
STATIONPATH = os.path.join(LIBPATH,'stations')

PLUGINFANART = os.path.join(PLUGINPATH,'fanart.jpg')
PLAYFILE = os.path.join(DATAPATH,'play.m3u8')
KEYFILE = os.path.join(DATAPATH,'play%s.key')
SUBTITLE = os.path.join(DATAPATH,'subtitle.srt')
SUBTITLESMI = os.path.join(DATAPATH,'subtitle.smi')
COOKIE = os.path.join(DATAPATH,'cookie%s.txt')
FAVICON = os.path.join(IMAGEPATH,'fav.png')
ALLICON = os.path.join(IMAGEPATH,'allshows.png')

#Paths of the USTV VoD database plugin
DBPATH = xbmc.translatePath('special://home/addons/script.module.free.cable.database/lib/')
DBFILE = os.path.join(DBPATH,'shows.db')
