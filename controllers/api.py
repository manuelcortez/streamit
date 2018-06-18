# -*- coding: utf-8 -*-
""" streamit! A self-hosted netflix where you can control what and how to watch your video."""

@auth.requires_login()
def get_movies():
	if request.vars.page == None:
		page = 1
	else:
		page = int(request.vars.page)
	start = (page-1)*10
	pages = db(db.movie).count()/10
	end = page*10
	movies = db(db.movie.file != None).select(orderby=~db.movie.id, limitby=(start, end))
	response.view = "generic.json"
	return dict(results=movies)

@auth.requires_login()
def get_tv_shows():
	if request.vars.page == None:
		page = 1
	else:
		page = int(request.vars.page)
	start = (page-1)*10
	pages = db(db.tv_show).count()/10
	end = page*10
	tv = db(db.tv_show).select(orderby=~db.tv_show.id, limitby=(start, end))
	response.view = "generic.json"
	return dict(results=tv)

@auth.requires_login()
def get_seasons():
	show = request.vars.show
	if show == None: return dict()
	tv = db(db.tv_season.show == show).select()
	response.view = "generic.json"
	return dict(results=tv)

@auth.requires_login()
def get_episodes():
	season = request.vars.season
	if season == None: return dict()
	tv = db((db.tv_episode.season_number == season) & (db.tv_episode.file != None)).select()
	response.view = "generic.json"
	return dict(results=tv)

@auth.requires_login()
def get_episode():
	episode = request.vars.episode
	if episode == None: return dict()
	tv = db(db.tv_episode.id == episode).select()
	response.view = "generic.json"
	return dict(results=tv)

@auth.requires_login()
def get_movie():
	movie = request.vars.movie
	if movie == None: return dict()
	tv = db(db.movie.id == movie).select()
	response.view = "generic.json"
	return dict(results=tv)

@auth.requires_login()
def get_file():
	file = request.vars.file
	if file == None: return dict()
	tv = db(db.media.id == file).select()
	response.view = "generic.json"
	return dict(results=tv)

