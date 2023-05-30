from repeater import Repeater
from scrape import Table
from typing import List



def parse_table(table: Table) -> List[Repeater]:
	# filter empty rows
	rows = [row for row in table.rows if row]
	
	reps = []
	for callsign, qth_name, downlink, uplink, _channel_new, _channel_old, shift, _mode, ctcss, echolink, qth_locator, _asl, active in rows:
		if active == "inaktív":
			continue
		reps.append(Repeater.parse(callsign, qth_name, downlink, uplink, shift, ctcss, echolink, qth_locator))
	return reps
