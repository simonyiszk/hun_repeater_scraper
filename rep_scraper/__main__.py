"""
Repeater list to KML converter by HA7DN

Scapes the HA2TO HAM repeater list and converts it into a KML file for maps software

Requires python3 + requests + maidenhead + simplekml

> pip3 install requests maidenhead simplekml
"""

URL_TO_FETCH = "http://ha2to.orbel.hu/content/repeaters/hu/index.html"

from scrape import extract_tables
from parse_table import parse_table
from map_export import export_map
from chirp_export import export_chirp

if __name__ == '__main__':
	repeaters = extract_tables(URL_TO_FETCH)[0]
	repeaters = parse_table(repeaters)
	export_map(repeaters, 'repeaters.kml', 'Átjátszók')
	export_map([r for r in repeaters if r.echolink_code], 'echolink.kml', 'EchoLink átjászók')
	export_chirp(repeaters, 'repeaters.csv')
