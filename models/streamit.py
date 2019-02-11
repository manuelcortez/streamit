# -*- coding: utf-8 -*-

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
	Field("genre", "string"),
	Field("image", "string"),
	Field("language", "reference languages"))

db.define_table("tv_season",
	Field("show", "reference tv_show", required=True),
	Field("name", "string", required=True),
	Field("season_number", "integer"),
	Field("first_aired", "date"),
	Field("movie_db_id", "string"),
	Field("overview", "text"),
	Field("image", "string"))

db.define_table("media",
	Field("type", "string", required=True, requires=IS_IN_SET(("tv", "movie"))),
	Field("owner", "integer"),
	Field("file", "string", required=True))

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
	Field("file", "reference media"),
	Field("language", "string", requires=IS_IN_DB(db, db.languages.code)))

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
	Field("file", "reference media"))

db.define_table("saved_file",
	Field("file", "reference media"),
	Field("type", "string"),
	Field("user", "reference auth_user"),
	Field("time", "double"),
	Field("updated_at", "datetime", default=request.now))

db.define_table("settings",
	Field("owner", "reference auth_user", required=True, default=auth.user, readable=False, writable=False),
	Field("language", "reference languages", label=T("Language for the site (content will be displayed in this language)"), required=True))