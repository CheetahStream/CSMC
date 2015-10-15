#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import site
site.addsitedir(os.path.abspath(os.path.join(os.path.dirname(__file__),'resources','lib')))
import common
import contextmenu
import sys
import ustvpaths
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmclibrary

addon = xbmcaddon.Addon()
pluginHandle = int(sys.argv[1])

print '\n\n\n start of USTV VoD plugin'

def modes():
	if sys.argv[2] == '':
		all_description = ''
		networks = common.get_networks()
		networks.sort(key = lambda x: x.SITE.replace('the', ''))
		for network in networks:
			if addon.getSetting(network.SITE) == 'true':
				if network.NAME.endswith(', The'):
					name = 'The ' + network.NAME.replace(', The', '')
				all_description += network.NAME + ', '
		count = 0
		cmlib = [ (common.smart_utf8(addon.getLocalizedString(39034)) % common.smart_utf8(addon.getLocalizedString(39000)), "XBMC.RunPlugin(%s?mode='ForceFavoriteEpisodesLibrary')" % ( sys.argv[0] ) ) ]
		cmlib.append( (common.smart_utf8(addon.getLocalizedString(39035)), "XBMC.RunPlugin(%s?mode='ClearLibrary')" % ( sys.argv[0] ) ) )
		common.add_directory(common.smart_utf8(addon.getLocalizedString(39000)), 'Favorlist', 'NoUrl', thumb = ustvpaths.FAVICON, count = count, description = common.smart_utf8(addon.getLocalizedString(39001)) + '\n' + all_description,  contextmenu = cmlib)
		count += 1
		cmlib = [ (common.smart_utf8(addon.getLocalizedString(39034)) % common.smart_utf8(addon.getLocalizedString(39002)), "XBMC.RunPlugin(%s?mode='AllShowsLibrary')" % ( sys.argv[0] ) ) ]
		cmlib.append( (common.smart_utf8(addon.getLocalizedString(39035)), "XBMC.RunPlugin(%s?mode='ClearLibrary')" % ( sys.argv[0] ) ) )
		common.add_directory(common.smart_utf8(addon.getLocalizedString(39002)), 'Masterlist', 'NoUrl', thumb = ustvpaths.ALLICON, count = count, description = common.smart_utf8(addon.getLocalizedString(39003)) + '\n' + all_description,  contextmenu = cmlib)
		count += 1
		for network in networks:
			network_name = network.NAME
			station_icon = os.path.join(ustvpaths.IMAGEPATH, network.SITE + '.png')
			if network_name.endswith(', The'):
				network_name = 'The ' + network_name.replace(', The', '')
			if addon.getSetting(network.SITE) == 'true':
				cmlib = [ (common.smart_utf8(addon.getLocalizedString(39034)) % network_name, "XBMC.RunPlugin(%s?mode='NetworkLibrary&submode='%s')" % ( sys.argv[0], network.SITE ) ) ]
				cmlib.append( (common.smart_utf8(addon.getLocalizedString(39035)), "XBMC.RunPlugin(%s?mode='ClearLibrary')" % ( sys.argv[0] ) ) )
				common.add_directory(network_name, network.SITE, 'rootlist', thumb = station_icon, fanart = ustvpaths.PLUGINFANART, description = network.DESCRIPTION, count = count, contextmenu = cmlib)
			count += 1
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_PLAYLIST_ORDER)
		common.set_view()
		xbmcplugin.endOfDirectory(pluginHandle)
	elif common.args.mode.startswith('script'):
		try:
			updater = xbmcaddon.Addon('script.ustvvodlibraryautoupdate')
			updater.openSettings()
		except:
			dialog = xbmcgui.Dialog()
			dialog.ok(addon.getAddonInfo('name'), addon.getLocalizedString(39041))
	elif common.args.mode.endswith('Library'):
		xbmclibrary.Main()
	elif common.args.mode == 'Masterlist':
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		common.load_showlist()
		common.set_view('tvshows')
		xbmcplugin.endOfDirectory(pluginHandle)
	elif common.args.sitemode == 'rootlist':
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		common.root_list(common.args.mode)
		xbmcplugin.endOfDirectory(pluginHandle)
	elif common.args.sitemode.startswith('seasons'):
		common.season_list()
		xbmcplugin.endOfDirectory(pluginHandle)
	elif common.args.sitemode.startswith('episodes'):
		try:
			common.episode_list()
		except Exception as e:
			print "Error in Episodes:" + e
		if addon.getSetting('add_episode_identifier') == 'false':
			try:
				xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_DATEADDED)
			except:
				pass
			xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_EPISODE)
			xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_UNSORTED)
			xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
			xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_MPAA_RATING)
			xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_GENRE)
			xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
		xbmcplugin.endOfDirectory(pluginHandle)
	elif common.args.mode == 'Favorlist':   
		xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
		common.load_showlist(favored = 1)
		common.set_view('tvshows')
		xbmcplugin.endOfDirectory(pluginHandle)
	elif common.args.mode == 'contextmenu':
		getattr(contextmenu, common.args.sitemode)()
	elif common.args.mode == 'common':
		getattr(common, common.args.sitemode)()
	else:
		network = common.get_network(common.args.mode)
		if network:
			getattr(network, common.args.sitemode)()
			if 'episodes' in  common.args.sitemode and addon.getSetting('add_episode_identifier') == 'false':
				try:
					xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_DATEADDED)
				except:
					pass
				xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_EPISODE)
				xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_UNSORTED)
			if not common.args.sitemode.startswith('play'):
				xbmcplugin.endOfDirectory(pluginHandle)

try:
	modes()
except:
	sys.modules.clear()
