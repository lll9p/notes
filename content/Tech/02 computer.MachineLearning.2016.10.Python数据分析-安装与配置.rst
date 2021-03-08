Python数据分析-安装与配置
#############################
:date: 2016-09-22 08:45
:modified: 2016-10-29 17:34
:status: published
:category: Tech
:tags: Python, Machine learning, Data Mining
:series: Python机器学习
:slug: python-install-config-for-data-analysis
:authors: lao
:summary: Python机器学习安装配置教程
:toc: show

前言
=====

本文针对 ``python3.5`` 的数据分析需求进行配置，尽量满足分析及学习的需求（本人的）。

创建 ``venv`` 环境
============================

``venv`` 是 ``python3.4`` 以上的版本自带的功能，之前的版本需要安装 ``virtualenv`` 。它可以将工作环境及系统的python环境隔离开来，在这个环境下工作很方便，安装包也不需要 ``root权限`` 。

.. code-block:: bash

   # 一条命令完成venv的创建
   python -m venv venvoflao
   # 进入venv
   source ./venvoflao/bin/activate
   # 退出venv
   deactivate

添加以下代码到 ``~/.bashrc`` ，1.主要是自动更新全部包的命令，这样就可以通过 ``pip_update`` 来一键更新所有库；2.后面三行是编译 ``numpy`` 和 ``scipy`` 的必须品： ``LAPACK`` 、 ``BLAS`` ：先安装好 ``LAPACK`` 和 ``BLAS`` 然后添加后三行到 ``~.bashrc`` ，然后 ``source .bashrc`` 生效。

.. code-block:: bashrc

   alias pip_update="pip list --outdated | grep --invert-match '^\-e' | cut --delimiter ' ' --fields 1 | xargs --max-args 1 pip install --upgrade --trusted-host pypi.douban.com"
   export LAPACK=/usr/lib/liblapack.so
   #export ATLAS=/usr/lib/libatlas.so
   export BLAS=/usr/lib/libblas.so

基本Python库安装
================

以下的操作都是在 ``venv`` 下进行的。

以下代码安装常用的机器学习的库， ``numpy`` 和 ``scipy`` 编译需要较长时间，耐心等待即可。

.. code-block:: bash

   pip install numpy, pandas, scipy, sympy,\
               matplotlib, seaborn, plotly, networkx, Pillow,\
               scikit-learn, scikit-image, Theano, Keras, treeinterpreter,\
               notebook, qtconsole,\
               jupyter-contrib-nbextensions, jupyter-nbextensions-configurator,\
               requests, beautifulsoup4,\
               openpyxl, xlrd, xlwt, XlsxWriter

``matplotlib`` 中文配置
========================

``matplotlib`` 是一个很常用的画图库，可惜对中文支持不好，其实只要添加中文字体并稍微设置一下即可解决。

安装 ``文泉驿微米黑`` 字体，
再 ``touch .config/matplotlib/matplotlibrc`` 再添加以下几行到里面即可。

.. code-block:: config

    backend      : TkAgg
    font.family         : sans-serif
    font.sans-serif     : WenQuanYi Micro Hei, Bitstream Vera Sans, Lucida Grande, Verdana, Geneva, Lucid, Arial, Helvetica, Avant Garde, sans-serif
    axes.unicode_minus  : True
    figure.dpi       : 96

``jupyter notebook`` 配置
==========================

``jupyter notebook`` 是一个很方便的工具，可以在上面直接运行、调试代码，基本上写好之后稍微改下就成了一篇挺好的笔记了，可以导出为 ``pdf`` 、 ``html`` 等格式（需要安装 ``pandoc`` ）。

生成配置文件： ``jupyter notebook --generate-config`` 并修改 ``~/.jupyter/jupyter_notebook_config.py`` 下面相应的几行。

.. code-block:: python

    c = get_config()
    c.NotebookApp.notebook_dir = '/home/lao/Notebook'
    c.NotebookApp.enable_mathjax = True

完成 ``nbextensions`` 的安装：

.. code-block:: bash

   jupyter nbextensions_configurator enable
   jupyter contrib nbextension install --user
