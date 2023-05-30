from dataclasses import dataclass
from enum import Enum
import maidenhead
import random


class CTCSS_MODE(Enum):
	NONE = ""		# no rx, no tx
	TONE = "Tone"	# only transmit
	TSQL = "TSQL"	# rx and tx
	
@dataclass
class CTCSS:
	mode: CTCSS_MODE	# CTCSS mode for CHIRP
	dl_tone: float		# downlink CTCSS tone
	ul_tone: float		# uplink CTCSS tone

	@classmethod
	def parse_setting(_cls, setting: str) -> 'CTCSS':
		dl, ul = setting.replace('--', '0').split('/')
		dl, ul = float(dl), float(ul)
		if dl and ul:
			return CTCSS(CTCSS_MODE.TSQL, dl, ul)
		elif ul:
			return CTCSS(CTCSS_MODE.TONE, 88.5, ul)
		else:
			return CTCSS(CTCSS_MODE.NONE, 88.5, 88.5)
			
	def __str__(self):
		return f"{self.dl_tone or '--'}/{self.ul_tone or '--'}"

@dataclass
class QTH:
	name: str		# name of QTH
	locator: str	# maidenhead locator code
	
	def get_geo_pos(self, center:bool = True, randomize:bool = True) -> (float, float):
		lat, long = maidenhead.to_location(self.locator, center=center)
		if randomize:
			lat += random.uniform(-1 / 48, 1 / 48)
			long += random.uniform(-2 / 48, 2 / 48)
		return long, lat
	geo_pos = property(get_geo_pos)
	

@dataclass
class FREQ:
	downlink: float
	uplink: float
	
	@property
	def offset(self) -> float:
		return self.uplink - self.downlink
		
	
@dataclass
class Repeater:
	callsign: str
	ctcss: CTCSS
	qth: QTH
	freq: FREQ
	
	echolink_code: str
	
	@classmethod
	def parse(_cls, callsign, qth_name, downlink, uplink, shift, ctcss, echolink, qth_locator) -> 'Repeater':
		assert(FREQ(float(downlink), float(uplink)).offset == float(shift)), f"Offset is not valid for repeater {callsign}:\n\t{uplink=}\n\t{downlink=}\n\t{shift=}"
		return Repeater(callsign, CTCSS.parse_setting(ctcss), QTH(qth_name, qth_locator), FREQ(float(downlink), float(uplink)), echolink)
	
	@property
	def band2m(self):
		return self.freq.downlink < 400_000
			
