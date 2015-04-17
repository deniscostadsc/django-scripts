# coding: utf-8
from setuptools import setup
import os


setup(name='django-scripts',
      version='0.1',
      description='Manage script as migrations.',
      long_description=open(os.path.join(os.path.dirname(__file__), "README.md")).read(),
      author="Denis Costa", author_email="deniscostadsc@gmail.com",
      license="MIT",
      packages=[
          'django_scripts',
          'django_scripts.management',
          'django_scripts.management.commands'],
      install_requires=[],
      zip_safe=True,
      platforms='any',
      include_package_data=True,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries'],
      url='http://github.com/deniscostadsc/django-scripts')
