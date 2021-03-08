#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os
import pathlib
import shutil
import sys
from contextlib import contextmanager

from fabric import Connection
from invoke import run as local
from invoke import task
from invoke.util import cd
from pelican.server import ComplexHTTPRequestHandler, RootedHTTPServer

CONFIG = {
    # Local path configurations (can be absolute or relative to tasks.py)
    'deploy_path': 'output',
    'cache_path': 'cache',
    'alters_path': 'alters/templates-bootstrap3',
    'theme_path': 'pelican-themes/pelican-bootstrap3',
    'commit_message': "'Publish site on {}'".format(
        datetime.date.today().isoformat()),
    # Port for `serve`
    'port': 8000,
}
@contextmanager
def alter_template():
    templates_path = pathlib.Path(CONFIG['theme_path']) / 'templates'
    includes_path = pathlib.Path(
        CONFIG['theme_path']) / 'templates' / 'includes'
    alters_path = pathlib.Path(CONFIG['alters_path'])
    shutil.move(includes_path / 'comments.html',
                includes_path / 'comments.copy.html')
    shutil.copy(alters_path / 'comments.html',
                includes_path / 'comments.html')
    shutil.copy(alters_path / 'drafts.html',
                templates_path / 'drafts.html')
    yield
    os.remove(includes_path / 'comments.html')
    os.remove(templates_path / 'drafts.html')
    shutil.move(includes_path / 'comments.copy.html',
                includes_path / 'comments.html')


def update_repo():
    if os.environ.get('TRAVIS', 'false') != 'true':
        with cd(f"{CONFIG['deploy_path']}"):
            local('git pull')


@task
def clean(c):
    """Remove generated files and cache"""
    if os.path.isdir(CONFIG['deploy_path']):
        shutil.rmtree(CONFIG['deploy_path'])
        os.makedirs(CONFIG['deploy_path'])
    if os.path.isdir(CONFIG['cache_path']):
        shutil.rmtree(CONFIG['cache_path'])
        os.makedirs(CONFIG['cache_path'])


@task
def build(c):
    """Build local version of site"""
    local('pelican --settings pelicanconf.py')


@task
def rebuild(c):
    """`build` with the delete switch"""
    local('pelican --delete-output-directory --settings pelicanconf.py')


@task
def regenerate(c):
    """Automatically regenerate site upon file modification"""
    local('pelican --autoreload --settings pelicanconf.py')


@task
def serve(c):
    """Serve site at http://localhost:8000/"""
    class AddressReuseTCPServer(RootedHTTPServer):
        allow_reuse_address = True
    server = AddressReuseTCPServer(
        CONFIG['deploy_path'],
        ('', CONFIG['port']),
        ComplexHTTPRequestHandler)
    sys.stderr.write('Serving on port {port} ...\n'.format(**CONFIG))
    server.serve_forever()


@task
def reserve(c):
    """`build`, then `serve`"""
    build(c)
    serve(c)


@task
def publish(c):
    """Publish to production"""
    update_repo()
    clean(c)
    with alter_template() as _:
        local('pelican -s publishconf.py')
    search_path = pathlib.Path(
        CONFIG['deploy_path']) / 'tipuesearch_content.js'
    search_path_fix = pathlib.Path(
        CONFIG['deploy_path']) / 'tipuesearch_content.json'
    if os.path.isfile(search_path):
        shutil.move(search_path, search_path_fix)
    # Detect if in local machine or in travis-ci
    if os.environ.get('TRAVIS', 'false') != 'true':
        with cd(f"{CONFIG['deploy_path']}"):
            local('git checkout master')
            local('git add --all')
            local(f'''git commit -m "{CONFIG['commit_message']}"''')
            local('git push -u github master --quiet')
    local('python ./utils/gitalk.py')
