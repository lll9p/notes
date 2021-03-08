#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import pathlib
import xml.etree.ElementTree as ET
from collections import namedtuple
from hashlib import md5
import urllib.request as request
import urllib.parse as parse


from gitalk_config import config


class Gitalk:

    """
        Gtalk auto initiallization. 
        python ./gitalk.py
    """

    def __init__(self):
        self.script_path = pathlib.Path(__file__).parent.absolute()
        self.site_path = config.get('site_path').absolute()
        self.sitemap_file = self.site_path/config.get('sitemap')
        self.feed_file = self.site_path/config.get('feed')
        self.pattern = config.get('pattern')
        self.token = config.get('token')
        self.username = config.get('username')
        self.repos = config.get('repos')
        self.addtional_label = config.get('addtional_label')
        self.get_posts()

    def get_posts(self):
        feed = ET.parse(self.feed_file)
        root = feed.getroot()
        atom_namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', namespaces=atom_namespaces)
        posts = []

        class Post:
            def __init__(self, uri, uri_hash, title, issued):
                self.uri = uri
                self.uri_hash = uri_hash
                self.title = title
                self.issued = issued
        for entry in entries:
            title = entry.find('atom:title', namespaces=atom_namespaces).text
            uri = entry.find('atom:link[@href]',
                             namespaces=atom_namespaces).attrib['href']
            uri_hash = md5(('/'+uri.lstrip(self.pattern)).encode('utf-8'))\
                .hexdigest()
            posts.append(Post(uri, uri_hash, title, True))
        self.posts = posts

    def form_issues(self, post):
        issue = {'title': f'Comments of {post.title}',
                 'body': post.uri,
                 'assignees': [self.username],
                 'labels': self.addtional_label+[post.uri_hash],
                 }
        return issue

    def check_issued(self, post):
        def search_issue(uri_hash):
            url = f'https://api.github.com/search/issues?q=label:{uri_hash}'
            url += f'+repo:{self.repos}+user:{self.username}'
            url += f'&access_token={self.token}'
            with request.urlopen(url) as response:
                res = json.load(response)
            flag = res.get('total_count')
            if flag is None:
                label_exist = True
            elif flag >= 1:
                label_exist = True
            elif flag == 0:
                label_exist = False
            else:
                label_exist = True
            return label_exist
        return search_issue(post.uri_hash)

    def create_issue(self, issue):
        url = f'https://api.github.com/repos/{self.username}/{self.repos}/issues'
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.symmetra-preview+json"
        }
        req = request.Request(url, data=json.dumps(issue).encode(),
                              headers=headers, method='POST')
        with request.urlopen(req) as response:
            if response.status == 202 or 201:
                print(f'''Successfully created Issue "{issue['title']}"''')
            else:
                print(f'''Could not create Issue "{issue['title']}"''')
                print('Response:', response.content)

    def init_issue(self):
        for post in self.posts:
            if self.check_issued(post):
                print(f'{post.title} is issued')
                continue
            else:
                issue = self.form_issues(post)
                self.create_issue(issue)


if __name__ == "__main__":
    gitalk = Gitalk()
    gitalk.init_issue()
