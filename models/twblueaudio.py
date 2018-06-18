# -*- coding: utf-8 -*-

db.define_table("audio", Field("file", "upload"), Field("stored_key", "string", readable=False, writable=False), Field("filename", readable=False, writable=False), Field("uploaded_by", "integer", readable=False, writable=False), Field("published_on", "datetime", required=True, default=request.now, readable=False, writable=False))
db.define_table("api_keys", Field("userid", "integer", readable=False, writable=False, required=True, notnull=True), Field("key", "string", readable=False, writable=False))
db.define_table("settings", Field("setting", "string", required=True, readable=False, writable=False), Field("content", "string", readable=False, writable=False))

if db(db.settings.id > 0).count() == 0:
	db.settings.insert(setting="allow_registration", content="yes")

allow_reg = db(db.settings.setting == "allow_registration").select().first()
if allow_reg != None:
	if allow_reg.content == "yes":
		auth.settings.actions_disabled.append('register')