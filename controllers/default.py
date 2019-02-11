# -*- coding: utf-8 -*-
""" streamit! A self-hosted netflix."""

def _get_settings():
	settings = db(db.settings.owner == auth.user).select().first()
	if settings == None:
		return redirect(URL("default", "configuration"))
	return settings

@auth.requires_login()
def index():
	settings = _get_settings()
	response.title = T("Home")
	# For a logged-in user, displays recently watched shows and movies so continue watching will work.
	# This will show only the last 5 shows.
	# Recently watched movies are not implemented yet.
	shows = None
	movies = None
	recent_files = None
	recent_shows = []
	recent_show_ids = []
	recent_episodes = []
	shows = db(db.tv_show.language == settings.language).select(orderby=db.tv_show.show_title)
	movies = db(db.movie.language == settings.language).select(orderby=db.movie.title)
	recent_files = db(db.saved_file.user == auth.user).select(limitby=(0, 5), orderby=~db.saved_file.updated_at)
	for i in recent_files:
		episode = db(db.tv_episode.file == i.file).select().first()
		if episode != None and episode.show.id not in recent_show_ids:
			recent_show_ids.append(episode.show.id)
			recent_shows.append(db(db.tv_show.id == episode.show).select().first())
			recent_episodes.append(episode)
	return dict(message="", share=False, tv_shows=shows, recent_shows=recent_shows, recent_episodes=recent_episodes, movies=movies)

def user():
	return dict(form=auth(), share=False)

@cache.action()
def download():
	file = db(db.media.id == request.args[0]).select().first()
	if file == None:
		raise HTTP(404)
	filename = file.file
	if "http" in filename:
		return redirect(filename)
	return response.stream(filename)

@auth.requires_login()
def show():
	id = request.vars.show
	show = db(db.tv_show.id == id).select().first()
	if show == None:
		return redirect(URL("default", "index"))
	response.title = show.show_title
	seasons = db(db.tv_season.show == show).select()
	return dict(share=False, show=show, seasons=seasons)

@auth.requires_login()
def season():
	show_ = request.vars.show
	season_ = request.vars.season
	show_ = db(db.tv_show.id == show_).select().first()
	season_ = db(db.tv_season.id == season_).select().first()
	if show_ == None or season_ == None:
		return redirect(URL("default", "index"))
	response.title = "{0} - {1}".format(show_.show_title, season_.name)
	episodes = db((db.tv_episode.show == show_) & (db.tv_episode.season_number == season_)).select()
	return dict(share=False, season=season_, episodes=episodes)

@auth.requires_login()
def movie():
	id = request.vars.movie
	movie = db(db.movie.id == id).select().first()
	if movie == None:
		return redirect(URL("default", "index"))
	response.title = movie.title
	return dict(share=False, show=movie)

@auth.requires_login()
def watch():
	id = request.vars.id
	type = request.vars.type
	if type == "tv":
		obj = db(db.tv_episode.id == id).select().first()
		response.title = "{show} - {number}. {name}".format(show=obj.show.show_title, name=obj.name, number=obj.episode_number)
	elif type == "movie":
		obj = db(db.movie.id == id).select().first()
		response.title = obj.title
	if obj == None:
		return redirect(URL("default", "index"))
	existing_file = db((db.saved_file.file == obj.file) & (db.saved_file.type == type) & (db.saved_file.user == auth.user)).select().first()
	return dict(episode=obj, share=False, progress=existing_file)

@auth.requires_login()
def next():
	type = request.vars.type
	cap = request.vars.cap
	if type == "tv":
		episode = db(db.tv_episode.id == cap).select().first()
		existing_file = db((db.saved_file.file == episode.file) & (db.saved_file.type == type) & (db.saved_file.user == auth.user)).delete()
	if episode == None:
		return redirect(URL("default", "watch", vars=dict(id=cap)))
	nexte = db((db.tv_episode.show == episode.show) & (db.tv_episode.episode_number == episode.episode_number + 1) & (db.tv_episode.season_number == episode.season_number)).select().first()
	if nexte == None:
		nexts = db(db.tv_season.season_number == episode.season.season_number+1).select().first()
		nexte = db((db.tv_episode.show == episode.show) & (db.tv_episode.episode_number == 1) & (db.tv_episode.season_number == nexts)).select().first()
	if nexte.file != None:
		return redirect(URL("default", "watch", vars=dict(type=request.vars.type, id=nexte.id)))
	else:
		return redirect(URL("default", "watch", vars=dict(id=cap)))

@auth.requires_login()
def savedata():
	user = request.vars.user
	file_id = request.vars.id
	progress = request.vars.duration
	type = request.vars.type
	file = db(db.media.id == file_id).select().first()
	if type == None or file == None or progress == None:
		return dict()
	existing_file = db((db.saved_file.file == file) & (db.saved_file.type == type) & (db.saved_file.user == user)).select().first()
	if existing_file == None:
		db.saved_file.insert(file=file, user=user, type=type, time=progress)
	else:
		existing_file.update_record(time=progress, updated_at=request.now)

@auth.requires_login()
def configuration():
	response.title = T("Settings")
	settings = db(db.settings.owner == auth.user).select().first()
	if settings != None:
		form = SQLFORM(db.settings, settings)
	else:
		form = SQLFORM(db.settings)
	if form.process().accepted:
		response.flash = T("Your settings have been saved successfully")
		return redirect(URL("default", "index"))
	return dict(share=False, form=form)