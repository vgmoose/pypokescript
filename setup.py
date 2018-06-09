from setuptools import setup

setup(
	name='pypokescript',
	version='0.0.1',
	description='edit script files from pokemon games',
	license='GPLv3',
	packages=['pypokescript', 'pypokescript.games', 'pypokescript.games.utils', 'pypokescript.gui'],
	author='VGMoose',
	package_data={'pypokescript.gui': ['main.html', 'index.css', 'editor.html', 'header.html']},
    include_package_data=True,
	author_email='me@vgmoose.com',
	keywords=['pokescript', 'pokemon', 'rom editing'],
	url='https://github.com/vgmoose/pypokescript'
)
