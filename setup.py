from distutils.core import setup

setup(
    name = 'tag_utils',
    version = '0.1',
    description = 'Utility library for creating template tags for the Django templating language.',
    url = 'http://github.com/chrisdickinson/tag_utils/tree/master',
    download_url = 'http://cloud.github.com/downloads/chrisdickinson/tag_utils/tag_utils-0.1.tar.gz',
    packages = ['tag_utils'],
    package_dir = {'tag_utils':'tag_utils'},
    author = 'Chris Dickinson',
    author_email = 'christopher.s.dickinson@gmail.com',
    license = 'BSD',
    install_requires = [
        'surlex>=0.1.0',
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
