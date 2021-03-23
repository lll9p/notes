#!/usr/bin/env bash
echo 'Install plugins.'
git clone --depth=1 https://github.com/getpelican/pelican-plugins.git
( cd pelican-plugins && git submodule update --init bootstrapify )
