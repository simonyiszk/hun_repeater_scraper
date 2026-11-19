
"""
Export into a KML file
Color shows the band: red = 2m, blue = 70cm
Shape shows the type: house = private, star = multiple modes,
square = DMR, triangle = C4FM, circle = FM only (or unknown)
Description will contain QTH name (city), downlink, CTCSS and echolink
"""
import simplekml
from typing import Dict, List, Tuple
from repeater import Repeater


SHAPES_URL = "http://maps.google.com/mapfiles/kml/shapes/"
SHAPE_HOUSE = "homegardenbusiness.png"
SHAPE_MULTI = "star.png"
SHAPE_BY_MODE = {
	"DMR": "placemark_square.png",
	"C4FM": "triangle.png",
	"FM": "placemark_circle.png",
}

# KML colors are aabbggrr
COLOR_2m = simplekml.Color.red
COLOR_70cm = simplekml.Color.blue


def shape_for(repeater: Repeater) -> str:
	if repeater.private:
		return SHAPE_HOUSE
	names = {name for name, _freq in repeater.modes}
	if len(names) > 1:
		return SHAPE_MULTI
	if names:
		return SHAPE_BY_MODE.get(names.pop(), SHAPE_BY_MODE["FM"])
	return SHAPE_BY_MODE["FM"]


def export_map(repeaters: List[Repeater], filename: str = "rep.kml", document_name = None):
	kml = simplekml.Kml(open=1)
	if document_name:
		kml.document.name = document_name

	styles: Dict[Tuple[str, str], simplekml.Style] = {}

	def get_style(color: str, shape: str) -> simplekml.Style:
		if (color, shape) not in styles:
			style = simplekml.Style()
			style.iconstyle.icon.href = SHAPES_URL + shape
			style.iconstyle.color = color
			styles[(color, shape)] = style
		return styles[(color, shape)]

	for point in repeaters:
		pnt = kml.newpoint()
		pnt.name = point.callsign
		desc = point.qth.name
		if point.modes:
			desc += "\nPrivate" if point.private else "\nCommunity"
			for mode, freq in point.modes:
				desc += f"\n{mode}: {freq.downlink} kHz (uplink {freq.uplink} kHz)"
		else:
			desc += f"\nDownlink: {point.freq.downlink} kHz\nCTCSS: {point.ctcss}"
		if point.echolink_code:
			desc += f"\nEchoLink: {point.echolink_code}"
		pnt.description = desc
		pnt.coords = [point.qth.geo_pos]
		pnt.style = get_style(COLOR_2m if point.band2m else COLOR_70cm, shape_for(point))

	kml.save(filename)
