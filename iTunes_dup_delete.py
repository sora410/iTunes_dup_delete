# coding: utf-8

from bs4 import BeautifulSoup
from collections import namedtuple
import subprocess
import urllib.parse

BLACKWORD_NAME = ['[Blank]']
BLACKWORD_ARTIST = []
BLACKWORD_ALBUM = []

XML_PATH = '~/Music/iTunes/iTunes Music Library.xml'

MusicModel = namedtuple("MusicModel","name,time,artist,album,path")

class RunCommandError(Exception):
	pass

def _rm(dirname):
	try:
		subprocess.call(['rm', '-rf', dirname])
	except subprocess.CalledProcessError:
		raise RunCommandError('at \'rm\'')

def print_inline(t): print(t, end='', flush=True)

def g_parse_iTunes_Library_xml(xml_path, b_name, b_artist, b_album):
	with open(xml_path) as f:
		soup = BeautifulSoup(f,'lxml')

	dup = dict()
	for d in soup.dict.dict.find_all('dict'):
		name, time, artist, album, path = None, None, None, None, None
		i_d = iter(d.contents)
		while True:
			try:
				el_key = next(i_d)
			except StopIteration:
				break
			if el_key.name == 'key':
				if el_key.string == 'Total Time':
					time   = next(i_d).string
				elif el_key.string == 'Name':
					name   = next(i_d).string
				elif el_key.string == 'Artist':
					artist = next(i_d).string
				elif el_key.string == 'Album':
					album  = next(i_d).string
				elif el_key.string == 'Location':
					# file://を無視する7:
					path   = urllib.parse.unquote(next(i_d).string[7:])
		dup_key = (name, time, artist, album)
		if dup_key not in dup.keys():
			dup[dup_key] = True
		else:
			if name not in b_name and artist not in b_artist and album not in b_album:
				yield MusicModel(name,time,artist,album,path)

def remove_duplication_item(duplication_list):
	for d in duplication_list:
		_rm(d.path)

def main():
	print_inline('parsing %s...' % XML_PATH)
	duplication_list = [m for m in g_parse_iTunes_Library_xml(XML_PATH, BLACKWORD_NAME, BLACKWORD_ARTIST, BLACKWORD_ALBUM)]
	print('ok')
	if input('Are you sure to delete duplicated item(s)? (y/N)') == 'y':
		print_inline('deleting items...')
		remove_duplication_item(duplication_list)
		print('ok')
		print('%d item(s) were deleted.' % len(duplication_list))
	else:
		print('stopped.')

main()