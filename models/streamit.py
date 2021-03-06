# -*- coding: utf-8 -*-

# A table representation for a TV show. It shows information regarding general data, but not season and episodes are added right here.
# Hopefully in the future Streamit would be able to update certain information regarding the TV show (for example, number of episodes and seasons)
# Without needing to create a new database entry.
db.define_table("tv_show",
	Field("show_title", "string", required=True),
	Field("release_date", "date"),
	Field("imdb_id", "string"),
	Field("movie_db_id", "string"),
	Field("number_of_seasons", "integer"),
	Field("number_of_episodes", "integer"),
	Field("episode_run_time", "string"),
	Field("created_by", "string"),
	Field("credits", "text"),
	Field("rating", "double"),
	Field("rating_count", "integer"),
	Field("overview", "text"),
	# Genre will be used for searches in the future, so we'll make sure we save it.
	Field("genre", "string"),
	# This will contain an image name. Images are saved in static/imgs and here is just a plain reference to it.
	Field("image", "string"),
	# Useful to diferentiate content by language.
	Field("language", "reference languages"))

# this table holds information about a season for a TV show.
# tv_show is a table reference to an item present in the tv_show table.
# Here we still save just general info, no episodes nor media files are stored here.
db.define_table("tv_season",
	Field("show", "reference tv_show", required=True),
	Field("name", "string", required=True),
	Field("season_number", "integer"),
	Field("first_aired", "date"),
	Field("movie_db_id", "string"),
	Field("overview", "text"),
	Field("image", "string"))

# Media files storage.
# type must be tv or movie, because owner is the ID of the data associated to such file.
db.define_table("media",
	Field("type", "string", required=True, requires=IS_IN_SET(("tv", "movie"))),
	Field("owner", "integer"),
	Field("file", "string", required=True))

# This table holds information about a movie.
db.define_table("movie",
	Field("title", "string", required=True),
	Field("release_date", "date"),
	Field("imdb_id", "string"),
	Field("movie_db_id", "string"),
	Field("run_time", "string"),
	Field("created_by", "string"),
	Field("credits", "text"),
	Field("rating", "double"),
	Field("rating_count", "integer"),
	Field("overview", "text"),
	Field("genre", "string"),
	Field("image", "string"),
	Field("file", "reference media", readable=False, writeable=False),
	Field("language", "reference languages", required=True))

db.define_table("tv_episode",
	Field("show", "reference tv_show", required=True),
	Field("name", "string", required=True),
	Field("episode_number", "integer"),
	Field("season_number", "reference tv_season"),
	Field("first_aired", "date"),
	Field("movie_db_id", "string"),
	Field("rating", "double"),
	Field("rating_count", "integer"),
	Field("overview", "text"),
	Field("image", "string"),
	Field("file", "reference media", readable=False, writeable=False))

db.define_table("saved_file",
	Field("file", "reference media"),
	Field("type", "string"),
	Field("user", "reference auth_user"),
	Field("time", "double"),
	Field("updated_at", "datetime", default=request.now))

db.define_table("settings",
	Field("owner", "reference auth_user", required=True, default=auth.user, readable=False, writable=False),
	Field("language", "reference languages", label=T("Language for the site (content will be displayed in this language)"), required=True))