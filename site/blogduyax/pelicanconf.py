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

STATIC_PATHS= [
            'images',
            'documents',
            'extra/robots.txt',
            'extra/redirect.html',
            'extra/apple-touch-icon-120x120.png',
            'extra/apple-touch-icon-114x114.png',
            'extra/apple-touch-icon-144x144.png',
            'extra/apple-touch-icon-152x152.png',
            'extra/apple-touch-icon-57x57.png',
            'extra/apple-touch-icon-60x60.png',
            'extra/apple-touch-icon-72x72.png',
            'extra/apple-touch-icon-76x76.png',
            'extra/apple-touch-icon.png',
            'extra/apple-touch-icon-precomposed.png',
            'extra/browserconfig.xml',
            'extra/favicon-160x160.png',
            'extra/favicon-16x16.png',
            'extra/favicon-196x196.png',
            'extra/favicon-32x32.png',
            'extra/favicon-96x96.png',
            'extra/favicon.ico',
            'extra/mstile-144x144.png',
            'extra/mstile-150x150.png',
            'extra/mstile-310x150.png',
            'extra/mstile-310x310.png',
            'extra/mstile-70x70.png'
]
EXTRA_PATH_METADATA = {
            'extra/robots.txt': {'path': 'robots.txt'},
            'extra/redirect.html': {'path': 'redirect.html'},
            'extra/apple-touch-icon-114x114.png': {'path': 'apple-touch-icon-114x114.png'},
            'extra/apple-touch-icon-120x120.png': {'path': 'apple-touch-icon-120x120.png'},
            'extra/apple-touch-icon-144x144.png': {'path': 'apple-touch-icon-144x144.png'},
            'extra/apple-touch-icon-152x152.png': {'path': 'apple-touch-icon-152x152.png'},
            'extra/apple-touch-icon-57x57.png': {'path': 'apple-touch-icon-57x57.png'},
            'extra/apple-touch-icon-60x60.png': {'path': 'apple-touch-icon-60x60.png'},
            'extra/apple-touch-icon-72x72.png': {'path': 'apple-touch-icon-72x72.png'},
            'extra/apple-touch-icon-76x76.png': {'path': 'apple-touch-icon-76x76.png'},
            'extra/apple-touch-icon.png': {'path': 'apple-touch-icon.png'},
            'extra/apple-touch-icon-precomposed.png': {'path': 'apple-touch-icon-precomposed.png'},
            'extra/browserconfig.xml': {'path': 'browserconfig.xml'},
            'extra/favicon-160x160.png': {'path': 'favicon-160x160.png'},
            'extra/favicon-16x16.png': {'path': 'favicon-16x16.png'},
            'extra/favicon-196x196.png': {'path': 'favicon-196x196.png'},
            'extra/favicon-32x32.png': {'path': 'favicon-32x32.png'},
            'extra/favicon-96x96.png': {'path': 'favicon-96x96.png'},
            'extra/favicon.ico': {'path': 'favicon.ico'},
            'extra/mstile-144x144.png': {'path': 'mstile-144x144.png'},
            'extra/mstile-150x150.png': {'path': 'mstile-150x150.png'},
            'extra/mstile-310x150.png': {'path': 'mstile-310x150.png'},
            'extra/mstile-310x310.png': {'path': 'mstile-310x310.png'},
            'extra/mstile-70x70.png': {'path': 'mstile-70x70.png'}
}

DELETE_OUTPUT_DIRECTORY = False
DEFAULT_PAGINATION = 10

THEME = 'theme/pure-theme'
