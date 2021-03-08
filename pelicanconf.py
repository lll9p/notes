#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
from os import getenv

AUTHOR = 'Lao'
SITENAME = '劳思杂记'
SITEURL = '//' + getenv('SITEURL', default='localhost:8000')

PATH = 'content'

TIMEZONE = 'Asia/Shanghai'
MARKDOWN = {
    'extensions': [
        'markdown.extensions.toc',  # add Table of Content
    ],
    'output_format': 'html5',
}

# THEME = 'pelican-themes/pelican-bootstrap3'
THEME = 'pelican-themes/simplify-theme'
# Tell Pelican to add 'extra/custom.css' to the output dir
STATIC_PATHS = [
    'images',
    'static/favicon.png',
    'extra/robots.txt',
    'extra/CNAME',  # for github pages custom domain.
]
# Tell Pelican to change the path to 'static/custom.css' in the output dir
EXTRA_PATH_METADATA = {
    'static/favicon.png': {'path': 'static/favicon.png'},
    'extra/robots.txt': {'path': 'robots.txt'},
    'extra/CNAME': {'path': 'CNAME'},
}
PAGE_PATHS = [
    'pages'
]

DIRECT_TEMPLATES = ('search', 'index', 'categories',
                    'authors', 'archives', 'tags', 'drafts')
# Cache configs
CACHE_PATH = 'cache'
CACHE_CONTENT = False
LOAD_CONTENT_CACHE = False
GZIP_CACHE = True

DEFAULT_METADATA = {
    'status': 'draft',
}

TIMEZONE = 'Asia/Shanghai'
DATE_FORMATS = {
    'en': '%d %b %Y',
    'jp': '%Y-%m-%d',
    'zh': '%Y年%m月%d日',
}
DEFAULT_LANG = 'en'
#DEFAULT_LANG = 'Chinese (Simplified)'
# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
MENUITEMS = [('草稿', SITEURL + '/drafts.html',)
             ]

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         )

# Social widget
SOCIAL = {'twitter': 'https://twitter.com/lll9p',
          'github': 'https://github.com/lll9p',
          'facebook': 'https://facebook.com/laolilin'}
GITHUB_URL = 'https://github.com/lll9p'
GOOGLE_ANALYTICS = 'UA-181588-5'
DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
JINJA_ENVIRONMENT = {'trim_blocks': True,
                     'lstrip_blocks': True,
                     'extensions': ['jinja2.ext.i18n', ],
                     }
I18N_TEMPLATES_LANG = 'en'
PLUGIN_PATHS = ['pelican-plugins']
PLUGINS = [
    'better_codeblock_line_numbering',
    'always_modified',
    'bootstrapify',  # https://github.com/ingwinlu/pelican-bootstrapify.git
    'gzip_cache',
    'neighbors',
    'render_math',
    'series',
    'post_stats',
    'sitemap',
    'related_posts',
    'tipue_search',
]
GITTALK = True

# Article settings
# The URL to refer to an article.
ARTICLE_URL = 'posts/{date:%Y}/{date:%m}/{slug}.html'
# The place where we will save an article.
ARTICLE_SAVE_AS = 'posts/{date:%Y}/{date:%m}/{slug}.html'

# Setting names
# The location to save the article archives page.
ARCHIVES_SAVE_AS = 'archives.html'
# The location to save per-year archives of your posts.
YEAR_ARCHIVE_SAVE_AS = 'archives/{date:%Y}/index.html'

AUTHORS_URL = 'author/{slug}.html'

SLUG_REGEX_SUBSTITUTIONS = (
    #    (r'C\+\+', 'Cpp'),
    #    (r'c\+\+', 'cpp'),
    #    (r'[^ws-]', ''),  # remove non-alphabetical/whitespace/'-' chars
    #    (r'(?u)As*', ''),  # strip leading whitespace
    #    (r'(?u)s*Z', ''),  # strip trailing whitespace
    #    (r'[-s]+', '-'),  # reduce multiple whitespace or '-' to single '-'
)
OUTPUT_RETENTION = ['.git', '.nojekyll']
PYGMENTS_RST_OPTIONS = {}
SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.7,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly'
    }
}
TOC = {
    'TOC_HEADERS': '^h[1-6]',
    'TOC_RUN': 'true'
}

# simplify-theme settings
FAVICON = 'static/images/favicon.png'
MATH_JAX = {
    'align': 'center',
    'tex_extensions': [
        'color.js',
        'mhchem.js'],
    'source': "'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'",
}
