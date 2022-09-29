'''
pluginPackages test case

See COPYRIGHT.md for copyright information.
'''
# this module would raise system error due to PEP 366 after python 3.4.3
from . import importTestImported11

def foo():
    print ("imported unpackaged plug-in relative imported 1")

__pluginInfo__ = {
    'name': 'Unpackaged Relative Import 1',
    'version': '0.9',
    'description': "This is a unpackaged relative imported plugin.",
    'license': 'Apache-2',
    'author': 'Mark V Systems',
    'copyright': '(c) Copyright 2011-present Workiva, Inc., All rights reserved.',
    # classes of mount points (required)
    'Import.Unpackaged.Entry6': foo,
    # imported plugins
}
