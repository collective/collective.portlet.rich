# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version = '0.5dev0'

long_description = (
    read('README.txt')
    + '\n' +
    read('docs/HISTORY.txt')
#    + '\n' +
#    read('CONTRIBUTORS.txt')
    )

setup(
    name='collective.portlet.rich',
    version=version,
    description="Rich-text portlet for Plone",
    long_description=long_description,
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
      "Framework :: Plone",
      "Framework :: Zope2",
      "Framework :: Zope3",
      "Programming Language :: Python",
      "Topic :: Software Development :: Libraries :: Python Modules",
      ],
    keywords='',
    author='Plone Foundation',
    author_email='pellekrogholt@gmail.com',
    url='https://github.com/collective/collective.portlet.rich/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.portlet'],
    include_package_data=True,
    zip_safe=False,
    #TODO: set up a dependecy of the special plone.app.form branch that supports kupu/wysiwyg
    install_requires=[
        'Products.CMFPlone',
        'collective.formlib.link',
        'setuptools',
        ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target=plone
    """,
    )
