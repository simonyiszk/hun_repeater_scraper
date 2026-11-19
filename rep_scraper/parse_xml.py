import datetime
import xml.etree.ElementTree as ET
from typing import List

import maidenhead
from pyproj import Transformer

from repeater import Repeater, CTCSS, CTCSS_MODE, QTH, FREQ

NS = {'ss': 'urn:schemas-microsoft-com:office:spreadsheet'}
SS_INDEX = '{urn:schemas-microsoft-com:office:spreadsheet}Index'

COL_CALLSIGN = 4
COL_VALIDITY = 6
COL_CITY = 7
COL_TX = 9
COL_RX = 10
COL_EOV_X = 14  # northing
COL_EOV_Y = 15  # easting

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


def eov_to_locator(northing: float, easting: float) -> str:
	lon, lat = _eov_to_wgs84.transform(easting, northing)
	return maidenhead.to_maiden(lat, lon, precision=3)


def parse_xml(path: str) -> List[Repeater]:
	root = ET.parse(path).getroot()
	rows = root.findall('.//ss:Worksheet/ss:Table/ss:Row', NS)
	today = datetime.date.today()

	reps = []
	for row in rows[1:]:
		v = _row_values(row)
		v += [''] * (COL_EOV_Y + 1 - len(v))
		callsign = v[COL_CALLSIGN]
		if not (callsign and v[COL_TX] and v[COL_RX] and v[COL_EOV_X] and v[COL_EOV_Y]):
			continue
		if v[COL_VALIDITY]:
			if datetime.date.fromisoformat(v[COL_VALIDITY][:10]) < today:
				continue
		downlink = round(float(v[COL_TX]) * 1000, 3)
		uplink = round(float(v[COL_RX]) * 1000, 3)
		locator = eov_to_locator(float(v[COL_EOV_X]), float(v[COL_EOV_Y]))
		reps.append(Repeater(
			callsign,
			CTCSS(CTCSS_MODE.NONE, 88.5, 88.5),
			QTH(v[COL_CITY], locator),
			FREQ(downlink, uplink),
			'',
		))
	return reps
