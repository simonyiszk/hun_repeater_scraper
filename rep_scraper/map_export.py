
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


LAYER_OTHER = "Digipeater / Simplex"	# "P" digipeaters and simplex entries, not in the mode layers

SHAPES_URL = "http://maps.google.com/mapfiles/kml/shapes/"
SHAPE_HOUSE = "homegardenbusiness.png"
SHAPE_MULTI = "star.png"
SHAPE_BY_MODE = {
	"DMR": "placemark_square.png",
	"C4FM": "triangle.png",
	"FM": "placemark_circle.png",
}

LAYERS = ("FM", "DMR", "C4FM", LAYER_OTHER)	# one KML folder (Google My Maps layer) each

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
	folders: Dict[str, simplekml.Folder] = {}

	def get_style(color: str, shape: str) -> simplekml.Style:
		if (color, shape) not in styles:
			style = simplekml.Style()
			style.iconstyle.icon.href = SHAPES_URL + shape
			style.iconstyle.color = color
			styles[(color, shape)] = style
			# shared styles must live at the Document level, not inside a Folder (Google My Maps ignores them otherwise)
			kml.document.styles.append(style)
		return styles[(color, shape)]

	for point in repeaters:
		desc = point.qth.name
		if point.modes:
			desc += "\nPrivate" if point.private else "\nCommunity"
			for mode, freq in point.modes:
				desc += f"\n{mode}: {freq.downlink} kHz (uplink {freq.uplink} kHz)"
			if point.has_ctcss:
				desc += f"\nCTCSS: {point.ctcss}"
		else:
			desc += f"\nDownlink: {point.freq.downlink} kHz\nCTCSS: {point.ctcss}"
		if point.echolink_code:
			desc += f"\nEchoLink: {point.echolink_code}"
		style = get_style(COLOR_2m if point.band2m else COLOR_70cm, shape_for(point))

		# one layer per mode, a repeater with several modes appears in each of them
		present = {m for m, _f in point.modes}
		if point.digipeater or point.simplex:
			point_layers = [LAYER_OTHER]
		else:
			point_layers = [name for name in LAYERS if name in present] or ["FM"]
		for layer in point_layers:
			if layer not in folders:
				folders[layer] = kml.newfolder(name=layer)
			pnt = folders[layer].newpoint()
			pnt.name = f"{point.qth.name.strip()} {point.callsign}"
			pnt.description = desc
			pnt.coords = [point.qth.geo_pos]
			pnt.style = style

	for folder in folders.values():
		folder.styles.clear()	# simplekml also attaches the styles to the folder

	kml.save(filename)
