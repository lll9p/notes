#!/usr/bin/env bash
echo 'Build site'
echo "BUILD_TIME = '`env TZ=Asia/Shanghai date`'" >> publishconf.py
pelican content -s publishconf.py
