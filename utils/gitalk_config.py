#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pathlib
import socket

path = pathlib.Path(__file__).absolute()
hostname = socket.gethostname()
if hostname == "TheMachine":
    with open(path.parent / "token", mode="r") as file:
        token = file.read().strip("\n")
else:
    token = os.environ["COMMENTS_TOKEN"]
config = dict(
    site_path=path.parent.parent / "output",
    sitemap="sitemap.xml",
    feed="feeds/all.atom.xml",
    token=token,
    username="laolilin",
    repos="comments-blog.laolilin.com",
    pattern="//blog.laolilin.com",
    addtional_label=["Gitalk"],
)
