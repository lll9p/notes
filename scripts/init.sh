echo 'Install plugins'
mkdir pelican-plugins
svn checkout https://github.com/ingwinlu/pelican-bootstrapify/trunk/ pelican-plugins/bootstrapify
svn checkout https://github.com/getpelican/pelican-plugins/trunk/tipue_search pelican-plugins/tipue_search
svn checkout https://github.com/getpelican/pelican-plugins/trunk/better_codeblock_line_numbering pelican-plugins/better_codeblock_line_numbering
svn checkout https://github.com/getpelican/pelican-plugins/trunk/always_modified pelican-plugins/always_modified
svn checkout https://github.com/getpelican/pelican-plugins/trunk/gzip_cache pelican-plugins/gzip_cache
svn checkout https://github.com/getpelican/pelican-plugins/trunk/neighbors pelican-plugins/neighbors
svn checkout https://github.com/getpelican/pelican-plugins/trunk/render_math pelican-plugins/render_math
svn checkout https://github.com/getpelican/pelican-plugins/trunk/series pelican-plugins/series
svn checkout https://github.com/getpelican/pelican-plugins/trunk/post_stats pelican-plugins/post_stats
svn checkout https://github.com/getpelican/pelican-plugins/trunk/sitemap pelican-plugins/sitemap
svn checkout https://github.com/getpelican/pelican-plugins/trunk/related_posts pelican-plugins/related_posts
echo 'Install themes'
mkdir pelican-themes
git clone -b dev https://github.com/lll9p/simplify-theme.git pelican-themes/simplify-theme
