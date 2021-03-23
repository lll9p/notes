#!/usr/bin/env bash
echo 'Push to laolilin.github.io'
cd output
git config --global user.email "lll9p.china@gmail.com"
git config --global user.name "lll9p"
git config --global init.defaultBranch master
git init .
git add --all
git commit -m "Generate Pelican site"
git push --force https://lll9p:${PUSH_TOKEN}@github.com/laolilin/laolilin.github.io.git master
