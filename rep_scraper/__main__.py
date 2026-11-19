"""
Repeater list to KML converter by HA7DN

Converts the HA2TO HAM repeater list and/or the NMHH relay list into KML files for maps software and CHIRP CSV files

Requires python3 + requests + maidenhead + simplekml + pyproj

> pip3 install -r requirements.txt
"""

URL_TO_FETCH = "http://ha2to.orbel.hu/content/repeaters/hu/index.html"

import argparse
import sys

from scrape import extract_tables
from parse_table import parse_table
from parse_xml import parse_xml, parse_xml_data, download_nmhh, NMHH_URL
from merge import merge_repeaters
from map_export import export_map
from chirp_export import export_chirp_old, export_chirp_new

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description='Generate KML and CHIRP files from repeater data sources. '
			'Use --ha2to together with --nmhh or --xml to merge the two sources by callsign.')
	parser.add_argument('--ha2to', action='store_true', help=f'scrape the HA2TO website ({URL_TO_FETCH})')
	xml_source = parser.add_mutually_exclusive_group()
	xml_source.add_argument('--nmhh', action='store_true', help=f'download the NMHH relay list ({NMHH_URL})')
	xml_source.add_argument('--xml', metavar='PATH', help='read the relay list from an XML (SpreadsheetML) file')
	parser.add_argument('--ctcss', action='store_true', help='add the CTCSS zones by county as layers to the KML files')
	args = parser.parse_args()

	if not (args.ha2to or args.nmhh or args.xml):
		parser.print_help()
		sys.exit(0)

	ha2to = parse_table(extract_tables(URL_TO_FETCH)[0]) if args.ha2to else None
	if args.nmhh:
		xml = parse_xml_data(download_nmhh())
	elif args.xml:
		xml = parse_xml(args.xml)
	else:
		xml = None

	if ha2to is not None and xml is not None:
		repeaters = merge_repeaters(ha2to, xml)
	else:
		repeaters = ha2to if ha2to is not None else xml

	export_map(repeaters, 'repeaters.kml', 'Átjátszók', ctcss=args.ctcss)
	echolink = [r for r in repeaters if r.echolink_code]
	if echolink:
		export_map(echolink, 'echolink.kml', 'EchoLink átjászók')
	else:
		print('No EchoLink data, skipping echolink.kml')
	export_chirp_old(repeaters)
	export_chirp_new(repeaters)
