#!/usr/bin/python
# -*- coding: utf-8 -*-
import connection
import pyamf
from pyamf import remoting

class ViewerExperienceRequest(object):
	def __init__(self, URL, contentOverrides, experienceId, playerKey, TTLToken = ''):
		self.TTLToken = TTLToken
		self.URL = URL
		self.deliveryType = float(0)
		self.contentOverrides = contentOverrides
		self.experienceId = experienceId
		self.playerKey = playerKey

class ContentOverride(object):
	def __init__(self, contentId, contentType = 0, target = 'videoPlayer'):
		self.contentType = contentType
		self.contentId = contentId
		self.target = target
		self.contentIds = None
		self.contentRefId = None
		self.contentRefIds = None
		self.contentType = 0
		self.featureId = float(0)
		self.featuredRefId = None

def get_episode_info(video_player_key, video_content_id, video_url, video_player_id, const):
	envelope = build_amf_request(video_player_key, video_content_id, video_url, video_player_id, const)
	connection_url = "http://c.brightcove.com/services/messagebroker/amf?playerKey=" + video_player_key
	values = bytes(remoting.encode(envelope).read())
	header = {'Content-Type' : 'application/x-amf'}
	response = remoting.decode(connection.getURL(connection_url, values, header, amf = True)).bodies[0][1].body
	return response

def build_amf_request(video_player_key, video_content_id, video_url, video_player_id, const):
	pyamf.register_class(ViewerExperienceRequest, 'com.brightcove.experience.ViewerExperienceRequest')
	pyamf.register_class(ContentOverride, 'com.brightcove.experience.ContentOverride')
	content_override = ContentOverride(int(video_content_id))
	viewer_exp_req = ViewerExperienceRequest(video_url, [content_override], int(video_player_id), video_player_key)
	env = remoting.Envelope(amfVersion=3)
	env.bodies.append(
		(
			"/1",
			remoting.Request(
				target = "com.brightcove.experience.ExperienceRuntimeFacade.getDataForExperience",
				body = [const, viewer_exp_req],
				envelope = env
			)
		)
	)
	return env
