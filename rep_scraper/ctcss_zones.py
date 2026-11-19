"""
CTCSS zones by county (megye), added to the KML as a single folder (layer)
County boundaries: geoBoundaries HUN ADM1 (CC0), Budapest is inside the Pest polygon
"""
import json
import os
import simplekml

COUNTIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "hu_counties.geojson")

OPACITY = 0.25

# tone: (KML color aabbggrr without alpha -> bbggrr, counties)
ZONES = {
	"74.4": ("40ff9f", ("Somogy", "Baranya", "Tolna")),	# green
	"107.2": ("ffff9f", ("Győr-Moson-Sopron", "Vas", "Zala", "Veszprém", "Komárom-Esztergom", "Fejér")),	# blue
	"114.8": ("a3a3ff", ("Pest", "Nógrád", "Heves", "Borsod-Abaúj-Zemplén", "Jász-Nagykun-Szolnok")),	# pink
	"131.8": ("42e8f0", ("Szabolcs-Szatmár-Bereg", "Hajdú-Bihar", "Bács-Kiskun", "Csongrád-Csanád", "Békés")),	# yellow
}


def add_ctcss_zones(kml: simplekml.Kml):
	with open(COUNTIES_FILE, encoding="utf-8") as f:
		features = {ft["properties"]["shapeName"]: ft["geometry"] for ft in json.load(f)["features"]}

	alpha = f"{round(OPACITY * 255):02x}"
	folder = kml.newfolder(name="CTCSS")
	for tone, (color, counties) in ZONES.items():
		style = simplekml.Style()
		style.polystyle.color = alpha + color
		style.linestyle.color = "ff" + color
		style.linestyle.width = 1
		kml.document.styles.append(style)
		for county in counties:
			geometry = features[county]
			polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
			for rings in polygons:
				pol = folder.newpolygon(name=f"{county} - CTCSS {tone} Hz")
				pol.description = f"CTCSS: {tone} Hz"
				pol.outerboundaryis = [(x, y) for x, y, *_ in rings[0]]
				pol.innerboundaryis = [[(x, y) for x, y, *_ in ring] for ring in rings[1:]]
				pol.style = style
	folder.styles.clear()
