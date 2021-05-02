#!/usr/bin/env python
import pypandoc
import os

# pypandoc.core.PANDOC_PATH = '/usr/local/bin/pandoc'

if __name__ == "__main__":
    # doc = pypandoc.Document()
    # doc.markdown = open('README.md').read()
    # f = open('README.txt','w+')
    output = pypandoc.convert_file('README.md', 'rst')
    # f.write(doc.rst)
    # f.close()
    os.system("python setup.py register")
    os.system("python setup.py sdist upload")
    # os.remove('README.txt')
