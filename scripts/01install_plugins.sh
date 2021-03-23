#!/usr/bin/env bash
echo 'Install plugins.'
git clone --depth=1 https://github.com/getpelican/pelican-plugins.git
git clone --depth=1 https://github.com/ingwinlu/pelican-bootstrapify.git pelican-plugins/bootstrapify
