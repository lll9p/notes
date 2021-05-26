#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

from datetime import datetime
import os
import sys
import time
sys.path.append(os.curdir)
from pelicanconf import *

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

SITEURL = "//blog.laolilin.com"
RELATIVE_URLS = False

FEED_DOMAIN = SITEURL
FEED_ALL_ATOM = 'feeds/all.atom.xml'
FEED_ALL_RSS = 'feeds/all.rss.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'

DELETE_OUTPUT_DIRECTORY = True
GITTALK = True
BUILD_TIME = str(
    datetime.fromtimestamp(
        time.time(),
        datetime.timezone.utc))
