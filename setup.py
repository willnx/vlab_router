#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
router RESTful API
"""
from setuptools import setup, find_packages


setup(name="vlab-router-api",
      author="Nicholas Willhite,",
      author_email='willnx84@gmail.com',
      version='2019.06.24',
      packages=find_packages(),
      include_package_data=True,
      package_files={'vlab_router_api' : ['app.ini']},
      description="router",
      install_requires=['flask', 'ldap3', 'pyjwt', 'uwsgi', 'vlab-api-common',
                        'ujson', 'cryptography', 'vlab-inf-common', 'celery']
      )
