# -*- coding: utf-8 -*-
# @Time    : 2020/6/14 1:35
# @Author  : Hochikong
# @FileName: setup.py

from setuptools import setup, find_packages

setup(
    name='djsc',
    version='0.0.3.2',

    description='Doujinshi Collector Framework',

    author='Hochikong',
    author_email='ckhoidea@hotmail.com',

    url='https://github.com/Hochikong/MetaCollect/tree/master/PythonBaseTools/DoujinshiCollector',

    classifiers=['License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
                 'Programming Language :: Python :: 3.6',
                 'Intended Audience :: Developers',
                 'Environment :: Console',
                 ],

    platforms=['Any'],

    entry_points={
        'console_scripts': [
            'djsc=djscollect.DJSC:run'
        ],
    },

    packages=find_packages(),
    include_package_data=True,

    zip_safe=False,
)
