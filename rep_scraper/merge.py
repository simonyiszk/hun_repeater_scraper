from typing import List

from repeater import Repeater


def merge_repeaters(ha2to: List[Repeater], xml: List[Repeater]) -> List[Repeater]:
	"""
	Merge the HA2TO and the XML (NMHH) lists by callsign.
	For callsigns in both, the XML provides the frequencies, modes and ownership,
	HA2TO provides the QTH (name and locator), CTCSS and EchoLink code.
	Callsigns in only one of the lists are kept unchanged.
	"""
	ha2to_by_callsign = {r.callsign: r for r in ha2to}
	merged = []
	for x in xml:
		h = ha2to_by_callsign.pop(x.callsign, None)
		if h is None:
			merged.append(x)
			continue
		merged.append(Repeater(
			x.callsign, h.ctcss, h.qth, x.freq, h.echolink_code,
			x.modes, x.private, has_ctcss=True,
		))
	merged.extend(ha2to_by_callsign.values())
	return merged
