
"""
Export into a KML file
2m and 70cm repeaters will have red/blue markers
Description will contain QTH name (city), downlink, CTCSS and echolink
"""
import simplekml
from typing import List
from repeater import Repeater


STYLE_2m = simplekml.Style()
STYLE_2m.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png"

STYLE_70cm = simplekml.Style()
STYLE_70cm.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/pushpin/blue-pushpin.png"


def export_map(repeaters: List[Repeater], filename: str = "rep.kml", document_name = None):
	kml = simplekml.Kml(open=1)
	if document_name:
		kml.document.name = document_name
	
	for point in repeaters:
		pnt = kml.newpoint()
		pnt.name = point.callsign
		desc = f"{point.qth.name}\nDownlink: {point.freq.downlink} kHz\nCTCSS: {point.ctcss}"
		if point.echolink_code:
			desc += f"\nEchoLink: {point.echolink_code}"
		pnt.description = desc
		pnt.coords = [point.qth.geo_pos]
		pnt.style = STYLE_2m if point.band2m else STYLE_70cm

	kml.save(filename)
