# -*- coding: utf-8 -*-
""" streamit! A self-hosted netflix where you can control what and how to watch your video."""
import os
import requests
import tmdbsimple as tmdb
tmdb.API_KEY = myconf.get("settings.tmdb_api_key")
lang = myconf.get("settings.default_language")

def _prepare_image_path():
	""" Checks if the image path exists. Otherwise create it"""
	if os.path.exists(os.path.join(request.folder, "static/imgs")) == False:
		os.mkdir(os.path.join(request.folder, "static/imgs"))

def _get_image(img):
	""" Download image from the movie database and save it in the static images folder for a later usage. If the given image already exists, do nothing."""
	_prepare_image_path()
	imgs = os.listdir(os.path.join(request.folder, "static/imgs"))
	if img not in imgs:
		full_url = "http://image.tmdb.org/t/p/w185/{0}".format(img,)
		r = requests.get(full_url, stream=True)
		if r.status_code == 200:
			with open(os.path.join(request.folder, "static", "imgs", img[1:]), 'wb') as f:
				for chunk in r:
					f.write(chunk)

@auth.requires_login()
def index():
	if auth.user_id != 1: return redirect(URL("default", "index"))
	response.title = T("Administration Dashboard")
	tv_shows = db(db.tv_show).count()
	movies = db(db.movie).count()
	files = db(db.media.file != None).count()
	return dict(share=False, tv_shows=tv_shows, files=files, movies=movies)

@auth.requires_login()
def search_show():
	results = []
	response.title = T("Search TV show")
	form = SQLFORM.factory(Field("search", "string"), Field("language", "reference languages", required=True, requires=IS_IN_DB(db, db.languages.code)))
	if form.validate():
		search = tmdb.Search()
		session.language_for_search = form.vars.language
		r = search.tv(query=form.vars.search, language=form.vars.language)
		results = search.results
	return dict(share=False, form=form, results=results)

@auth.requires_login()
def add_show():
	if auth.user_id != 1: return redirect(URL("default", "index"))
	response.title = T("Add TV Show")
	show = None
	if session.language_for_search != None:
		language = session.language_for_search
	else:
		language = "es"
	if request.vars.tmdbid != None:
		show_es = tmdb.TV(request.vars.tmdbid)
		r = show_es.info(language=language)
		show = tmdb.TV(request.vars.tmdbid)
		r = show.info()
		credits = show.credits()["cast"]
		str_credits = u""
		for i in credits:
			str_credits = str_credits +  u"{0} ({1}), ".format(i["name"], i["character"])
		str_created = u""
		for i in show.created_by:
			str_created = str_created + u"{0}, ".format(i["name"], )
		str_gender = u""
		for i in show_es.genres:
			str_gender = str_gender + u"{0}, ".format(i["name"], )
		titles = show.alternative_titles()["results"]
#		response.write(show)
		img = show.poster_path
		_get_image(img)
		if len(str_created) != 0: str_created = str_created[:-2]
		if len(str_credits) != 0: str_credits = str_credits[:-2]
		if len(str_gender) != 0: str_gender = str_gender[:-2]
	form = SQLFORM(db.tv_show, upload=URL("download"))
	form.vars.language = db(db.languages.code == language).select().first().id
	if show != None:
#		for i in titles:
#			if i["iso_3166_1"] == language.upper(): form.vars.show_title = i["title"]; break
#			else:
		form.vars.show_title = show_es.name
		form.vars.release_date = show.first_air_date
		form.vars.movie_db_id = show_es.id
		form.vars.rating = show_es.vote_average
		form.vars.rating_count = show_es.vote_count
		form.vars.overview = show_es.overview
		form.vars.number_of_seasons = show_es.number_of_seasons
		form.vars.number_of_episodes = show_es.number_of_episodes
		form.vars.episode_run_time = u"-".join([str(i) for i in show.episode_run_time]) + T(" Minutes")
		form.vars.credits = str_credits
		form.vars.created_by = str_created
		form.vars.genre = str_gender
		form.vars.imdb_id = show.external_ids()["imdb_id"]
		form.vars.image = img[1:]
	if form.process().accepted:
		return redirect(URL("default", "index"))
	return dict(form=form, share=False)

@auth.requires_login()
def add_season():
	if auth.user_id != 1: return redirect(URL("default", "index"))
	id = request.vars.show
	show = db(db.tv_show.id == id).select().first()
	if show == None:
		return redirect(URL("default", "index"))
	response.title = T("Add season")
	form = SQLFORM.factory(Field("season", "integer"))
	if form.validate():
		season_en = tmdb.TV_Seasons(show.movie_db_id, season_number=form.vars.season)
		info_en = season_en.info()
		season_es = tmdb.TV_Seasons(show.movie_db_id, season_number=form.vars.season)
		info_es = season_es.info(language=show.language.code)
		for i in range(0, len(info_es["episodes"])):
			for z in info_es["episodes"][i].keys():
				if type(info_es["episodes"][i][z]) == str and len(info_es["episodes"][i][z]) == 0: info_es["episodes"][i][z] = info_en["episodes"][i][z]
		s = db.tv_season.insert(show=show, name=info_es["name"], season_number=info_es["season_number"], first_aired=info_es["air_date"], movie_db_id=info_es["id"], overview=info_es["overview"], image=info_es["poster_path"][1:])
		_get_image(info_es["poster_path"][1:])
		for i in info_es["episodes"]:
			db.tv_episode.insert(show=show, name=i["name"], episode_number=i["episode_number"], season_number=s, first_aired=i["air_date"], movie_db_id=i["id"], rating=i["vote_average"], rating_count=i["vote_count"], overview=i["overview"], image=i["still_path"][1:])
			_get_image(i["still_path"][1:])
		return redirect(URL("default", "show", vars=dict(show=show.id)))
	return dict(form=form, share=False)

@auth.requires_login()
def add_file():
	if auth.user_id != 1: return redirect(URL("default", "index"))
	id = request.vars.id
	if request.vars.type == "tv":
		episode = db(db.tv_episode.id == id).select().first()
		if episode == None:
			return redirect(URL("default", "index"))
		response.title = "{0}: {1}".format(episode.episode_number, episode.name)
	elif request.vars.type == "movie":
		movie = db(db.movie.id == id).select().first()
		if movie == None:
			return redirect(URL("default", "index"))
		response.title = movie.title
	form = SQLFORM(db.media, fields=["file"])
	form.vars.type = request.vars.type
	form.vars.owner = auth.user_id
	if form.process().accepted:
		if request.vars.type == "tv":
			episode.update_record(file=db(db.media).select().last())
			return redirect(URL("default", "index"))
		elif request.vars.type == "movie":
			movie.update_record(file=db(db.media).select().last())
			return redirect(URL("default", "index"))
	return dict(form=form, share=False)

@auth.requires_login()
def search_movie():
	results = []
	response.title = T("Search Movie")
	form = SQLFORM.factory(Field("search", "string"))
	if form.validate():
		search = tmdb.Search()
		r = search.movie(query=form.vars.search, language="es")
		results = search.results
	return dict(share=False, form=form, results=results)

@auth.requires_login()
def add_movie():
	if auth.user_id != 1: return redirect(URL("default", "index"))
	response.title = T("Add Movie")
	movie = None
	if request.vars.tmdbid != None:
		movie_es = tmdb.Movies(request.vars.tmdbid)
		r = movie_es.info(language="es")
		movie = tmdb.Movies(request.vars.tmdbid)
		r = movie.info()
		credits = movie.credits()["cast"]
		str_credits = u""
		for i in credits:
			str_credits = str_credits +  u"{0} ({1}), ".format(i["name"], i["character"])
		str_created = u""
		for i in movie.production_companies:
			str_created = str_created + u"{0}, ".format(i["name"], )
		str_gender = u""
		for i in movie_es.genres:
			str_gender = str_gender + u"{0}, ".format(i["name"], )
		titles = movie.alternative_titles()["titles"]
#		response.write(movie)
		img = movie.poster_path
		_get_image(img)
		if len(str_created) != 0: str_created = str_created[:-2]
		if len(str_credits) != 0: str_credits = str_credits[:-2]
		if len(str_gender) != 0: str_gender = str_gender[:-2]
	form = SQLFORM(db.movie, upload=URL("download"))
	if movie_es != None and hasattr(movie_es, "title"):
		form.vars.title = movie_es.title
	else:
		form.vars.title = movie.original_title
	if movie != None:
#		for i in titles:
#			if i["iso_3166_1"] == "ES": form.vars.title = i["title"]; break
		form.vars.release_date = movie.release_date
		form.vars.movie_db_id = movie_es.id
		form.vars.rating = movie_es.vote_average
		form.vars.rating_count = movie_es.vote_count
		form.vars.overview = movie_es.overview
		form.vars.run_time = movie.runtime
		form.vars.credits = str_credits
		form.vars.created_by = str_created
		form.vars.genre = str_gender
		form.vars.imdb_id = movie.imdb_id
		form.vars.image = img[1:]
	if form.process().accepted:
		return redirect(URL("default", "index"))
	return dict(form=form, share=False)

@auth.requires_login()
def manage_files():
	if auth.user_id != 1: return redirect(URL("default", "index"))
	response.title = T("Manage files")
	files = db(db.media).select()
	return dict(share=False, files=files)