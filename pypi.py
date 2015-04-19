#!/usr/bin/env python
import pandoc
import os

pandoc.core.PANDOC_PATH = '/usr/local/bin/pandoc'

if __name__ == "__main__":
    doc = pandoc.Document()
    doc.markdown = open('README.md').read()
    f = open('README.txt','w+')
    f.write(doc.rst)
    f.close()
    os.system("python setup.py register")
    os.system("python setup.py sdist upload")
    os.remove('README.txt')
