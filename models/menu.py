# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# Customize your APP title, subtitle and menus here
# ----------------------------------------------------------------------------------------------------------------------
import re

if re.compile('\w{2}(\-\w{2})?').match(request.vars.lang or ''): 
    session.language=request.vars.lang
if session.language:
   T.force(session.language)
#response.logo = ""

response.title = request.application.replace('_', ' ').title()
response.subtitle = ''

# ----------------------------------------------------------------------------------------------------------------------
# read more at http://dev.w3.org/html5/markup/meta.name.html
# ----------------------------------------------------------------------------------------------------------------------
response.meta.author = myconf.get('app.author')
response.meta.description = myconf.get('app.description')
response.meta.keywords = myconf.get('app.keywords')
response.meta.generator = myconf.get('app.generator')

# ----------------------------------------------------------------------------------------------------------------------
# your http://google.com/analytics id
# ----------------------------------------------------------------------------------------------------------------------
response.google_analytics_id = None

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

response.menu = [
    (T('Streamit'), False, False, [
    (T('Home'), False, URL('default', 'index'), []),
]),
    (T('Profile'), False, False, [
    (T('Configuration'), False, URL('default', 'configuration'), []),
    (T('Change password'), False, URL('default', 'user', args="change_password"), []),
    (T('LogOut'), False, URL('default', 'user', args="logout"), []),
]),
]

response.admin_menu = [
    (T('Administration'), False, URL('administration', 'index'), []),
    (T('Add TV Show'), False, URL('administration', 'search_show'), []),
    (T('Add Movie'), False, URL('administration', 'search_movie'), []),
]