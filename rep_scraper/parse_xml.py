import datetime
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

import maidenhead
from pyproj import Transformer

from repeater import Repeater, CTCSS, CTCSS_MODE, QTH, FREQ

NS = {'ss': 'urn:schemas-microsoft-com:office:spreadsheet'}
SS_INDEX = '{urn:schemas-microsoft-com:office:spreadsheet}Index'

COL_CALLSIGN = 4
COL_VALIDITY = 6
COL_CITY = 7
COL_MODE = 8
COL_TX = 9
COL_RX = 10
# EOV northing and easting. Rows are inconsistent about which column holds which.
COL_EOV_A = 14
COL_EOV_B = 15

# Hungary bounding box, used to reject bad coordinates
LAT_RANGE = (45.7, 48.6)
LON_RANGE = (16.0, 23.0)
# 2m and 70cm bands in kHz, other rows (e.g. microwave links) are ignored
BANDS_KHZ = ((144_000, 146_000), (430_000, 440_000))

_eov_to_wgs84 = Transformer.from_crs("EPSG:23700", "EPSG:4326", always_xy=True)


def _row_values(row: ET.Element) -> List[str]:
	values: List[str] = []
	for cell in row.findall('ss:Cell', NS):
		index = cell.get(SS_INDEX)
		if index:
			values.extend([''] * (int(index) - 1 - len(values)))
		data = cell.find('ss:Data', NS)
		values.append((data.text or '').strip() if data is not None else '')
	return values


def eov_to_locator(a: float, b: float) -> Optional[str]:
	"""
	Convert EOV coordinates (in either order) to a locator.
	EOV northing is always below 400000 and easting above, so the order can be detected.
	Returns None if the position is outside Hungary.
	"""
	northing, easting = min(a, b), max(a, b)
	lon, lat = _eov_to_wgs84.transform(easting, northing)
	if not (LAT_RANGE[0] <= lat <= LAT_RANGE[1] and LON_RANGE[0] <= lon <= LON_RANGE[1]):
		return None
	return maidenhead.to_maiden(lat, lon, precision=3)


def mode_label(designator: str) -> str:
	d = designator.upper()
	if 'C4FM' in d:
		return 'C4FM'
	if d.startswith('7K60FX'):
		return 'DMR'
	return 'FM'


def parse_xml(path: str) -> List[Repeater]:
	root = ET.parse(path).getroot()
	rows = root.findall('.//ss:Worksheet/ss:Table/ss:Row', NS)
	today = datetime.date.today()

	by_callsign: Dict[str, Repeater] = {}
	for row in rows[1:]:
		v = _row_values(row)
		v += [''] * (COL_EOV_B + 1 - len(v))
		callsign = v[COL_CALLSIGN]
		if not (callsign and v[COL_TX] and v[COL_RX] and v[COL_EOV_A] and v[COL_EOV_B]):
			print(f'Skipping {callsign or "?"}: missing data')
			continue
		if v[COL_VALIDITY] and datetime.date.fromisoformat(v[COL_VALIDITY][:10]) < today:
			continue
		downlink = round(float(v[COL_TX]) * 1000, 3)
		uplink = round(float(v[COL_RX]) * 1000, 3)
		if not any(lo <= downlink <= hi for lo, hi in BANDS_KHZ):
			print(f'Skipping {callsign}: {downlink} kHz is not a 2m/70cm frequency')
			continue
		locator = eov_to_locator(float(v[COL_EOV_A]), float(v[COL_EOV_B]))
		if locator is None:
			print(f'Skipping {callsign}: coordinates {v[COL_EOV_A]}, {v[COL_EOV_B]} are not valid EOV in Hungary')
			continue

		freq = FREQ(downlink, uplink)
		mode = (mode_label(v[COL_MODE]), freq)
		rep = by_callsign.get(callsign)
		if rep is None:
			by_callsign[callsign] = Repeater(
				callsign,
				CTCSS(CTCSS_MODE.NONE, 88.5, 88.5),
				QTH(v[COL_CITY], locator),
				freq,
				'',
				[mode],
			)
		elif mode not in rep.modes:
			rep.modes.append(mode)
	return list(by_callsign.values())
