"""
Repeater list to KML converter by HA7DN

Scapes the HA2TO HAM repeater list and converts it into a KML file for maps software

Requires python3 + requests + maidenhead + simplekml

> pip3 install requests maidenhead simplekml
"""
import requests
from html.parser import HTMLParser
from dataclasses import dataclass
import maidenhead as mh
import simplekml
import random
from typing import List

URL_TO_FETCH = "http://ha2to.orbel.hu/content/repeaters/hu/index.html"


"""
Table fetching
using requests + html.parser.HTMLParser to extract all tables from the webpage
"""


@dataclass
class Table:
    """
    Dataclass for a table extracted from the HTML page
    title is set by the last h2 / h3 element before the table
    headings are filled from <th> elements
    data are all str
    """
    title: str
    headings: List[str]
    rows: List[List[str]]


class TablesExtractor(HTMLParser):
    current_data = ""
    tables = [Table('', [], [[]])]
    current_row = []

    def handle_starttag(self, tag, attrs):
        # self.current_data = ""
        pass

    def handle_endtag(self, tag):
        if tag == "br":
            return
        if tag == "a":
            return
        self.current_data = self.current_data.replace("\r\n", "")
        if tag in ("h2", "h3"):
            self.tables[-1].title = self.current_data
        if tag == "th":
            self.tables[-1].headings.append(self.current_data)
        if tag == "td":
            self.tables[-1].rows[-1].append(self.current_data)
        if tag == "tr":
            if self.tables[-1].rows[-1]:
                self.tables[-1].rows.append([])
        if tag == "table":
            self.tables.append(Table('', [], [[]]))
        self.current_data = ""

    def handle_data(self, data):
        self.current_data += data


def extract_tables(url):
    data = requests.get(url).text
    te = TablesExtractor()
    te.feed(data)
    te.tables.pop()
    return te.tables


"""
We now have every table from the page
but for now, I only care about the first - the analoge repeaters table
"""
repeaters = extract_tables(URL_TO_FETCH)[0]
# filter empty rows
rows = [row for row in repeaters.rows if row]


@dataclass
class Repeater:
    callsign: str
    lat: float
    long: float
    band2m: bool
    echo: str
    down: str
    ctcss: float
    qthn: str


points = []
for cs, qthn, down, up, _, _, shift, _, ctcss, echo, qth, _, active in rows:
    # filter inactive repeaters
    if "in" in active:
        continue

    band2m = int(shift) == -600

    lat, long = mh.to_location(qth, center=True)
    # move it a bit so the markers won't overlap
    # but make sure it stays in the same grid square
    lat += random.uniform(-1 / 48, 1 / 48)
    long += random.uniform(-2 / 48, 2 / 48)
    assert mh.to_maiden(lat, long, 3).upper() == qth, f"mismatch"

    ctcss = ctcss.split("/")[0]
    points.append(Repeater(cs, lat, long, band2m, echo, down, ctcss, qthn))


"""
Export into a KML file
2m and 70cm repeaters will have red/blue markers
Description will contain QTH name (city), downlink, CTCSS and echolink
"""

kml = simplekml.Kml(open=1)

style_2m = simplekml.Style()
style_2m.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png"

style_70cm = simplekml.Style()
style_70cm.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/pushpin/blue-pushpin.png"

for point in points:
    pnt = kml.newpoint()
    pnt.name = point.callsign
    desc = f"{point.qthn}\nDownlink: {point.down} kHz\nCTCSS: {point.ctcss}"
    if point.echo:
        desc += f"\nEchoLink: {point.echo}"
    pnt.description = desc
    pnt.coords = [(point.long, point.lat)]
    pnt.style = style_2m if point.band2m else style_70cm

kml.save("rep.kml")
