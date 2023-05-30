from typing import List
from repeater import Repeater

def csv_escape(inp: str) -> str:
	if ',' in inp or '"' in inp:
		inp_repl = inp.replace('"', '""')
		return f'"{inp_repl}"'
	return inp

def export_chirp(repeaters: List[Repeater], filename: str = "repeaters.csv"):
	with open(filename, "w") as csvfile:
		csvfile.write("Location,Name,Frequency,Duplex,Offset,Tone,rToneFreq,cToneFreq,DtcsCode,DtcsPolarity,Mode,TStep,Skip,Comment,URCALL,RPT1CALL,RPT2CALL,DVCODE,Elt. [kHz]\n")
		
		for loc, rep in enumerate(repeaters, 1):
			csvfile.write(",".join(map(str, [
				loc,								# Location
				csv_escape(rep.callsign),			# Name
				rep.freq.downlink / 1000,			# Frequency [MHz]
				'-' if rep.freq.offset else '',		# Duplex
				abs(rep.freq.offset) / 1000,		# Offset [MHz]
				rep.ctcss.mode.value,				# Tone
				rep.ctcss.ul_tone,					# rToneFreq - transmit tone
				rep.ctcss.dl_tone,					# cToneFreq - receive tone
				'023',								# DtcsCode
				'NN',								# DtcsPolarity
				'FM',								# Mode
				'5.00',								# TStep
				'',									# Skip
				csv_escape(rep.qth.name.strip()),	# Comment
				*(['']*4),
			]))+'\n')

	
