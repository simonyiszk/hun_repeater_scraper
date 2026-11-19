"""
Repeater list to KML converter by HA7DN

Scapes the HA2TO HAM repeater list and converts it into a KML file for maps software

Requires python3 + requests + maidenhead + simplekml + pyproj

> pip3 install -r requirements.txt

Use --xml PATH to read a SpreadsheetML relay list instead of scraping the web.
"""

URL_TO_FETCH = "http://ha2to.orbel.hu/content/repeaters/hu/index.html"

import argparse

from scrape import extract_tables
from parse_table import parse_table
from parse_xml import parse_xml
from map_export import export_map
from chirp_export import export_chirp_old, export_chirp_new

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--xml', metavar='PATH', help='read repeaters from an XML (SpreadsheetML) file instead of scraping the web')
	args = parser.parse_args()

	if args.xml:
		repeaters = parse_xml(args.xml)
	else:
		repeaters = parse_table(extract_tables(URL_TO_FETCH)[0])
	export_map(repeaters, 'repeaters.kml', 'Átjátszók')
	echolink = [r for r in repeaters if r.echolink_code]
	if echolink or not args.xml:
		export_map(echolink, 'echolink.kml', 'EchoLink átjászók')
	else:
		print('XML input has no EchoLink data, skipping echolink.kml')
	export_chirp_old(repeaters)
	export_chirp_new(repeaters)
