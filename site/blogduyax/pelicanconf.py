#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = u'Yax'
AUTHOR_EMAIL = 'kianby@madyanne.fr'
SITENAME = u'Le blog du Yax'
SITESUBTITLE = u'GNU/Linux et autres libertés'

SITEURL = 'http://127.0.0.1:8000'
RELATIVE_URLS = True

TIMEZONE = 'Europe/Paris'
DEFAULT_LANG = u'fr'
TYPOGRIFY = False

ARTICLE_EXCLUDES = (('pages','documents','extra','images'))

# feeds
FEED_DOMAIN = SITEURL
FEED_ALL_ATOM = 'feeds/all.atom.xml'
FEED_ATOM_CUSTOM = 'feeds/%s.atom.xml'
#FEED_MAX_ITEMS = 10

# tags 
TAG_CLOUD_STEPS = 3
TAG_CLOUD_MAX_ITEMS = 50

# sidebar customization
LINKS = ()
SOCIAL = ()

# piwik
PIWIK_URL="www.madyanne.fr/piwik"
PIWIK_SITE_ID=1

# plugins
PLUGIN_PATH = "plugins"
PLUGINS = ['sitemap','planet', 'cacause']

# Configure CaCause plugin
CACAUSE_DIR = "comments"
CACAUSE_GRAVATAR = True

SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly'
    }
}

STATIC_PATHS= ['images','documents','extra/robots.txt','extra/favicon.png', 'extra/redirect.html']
EXTRA_PATH_METADATA = {
            'extra/robots.txt': {'path': 'robots.txt'},
            'extra/favicon.png': {'path': 'favicon.png'},
            'extra/redirect.html': {'path': 'redirect.html'}
}

DELETE_OUTPUT_DIRECTORY = False
DEFAULT_PAGINATION = 10

THEME = 'theme/pure-theme'
