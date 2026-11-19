# HA2TO repater scraper

This python script scrapes the page [Magyarországi VHF és UHF rádióamatőr átjátszók](http://ha2to.orbel.hu/content/repeaters/hu/index.html), or reads a local XML relay list, and generates 4 files:
- `repeaters_old_chirp.csv` and `repeaters_new_chirp.csv` for CHIRP (old and new CSV formats)
- `repeaters.kml` with approximate coordinates for mapping software (red pin = 2m repeater, blue pin = 70cm repeater)
- `echolink.kml` similar to `repeaters.kml` but only contains EchoLink-enabled repeaters (web scraping only)

For the maps, see [the generated map on google maps](https://www.google.com/maps/d/edit?mid=1pecdCCsx2C0F0qW0n-bFy2ZnTRufJyo&usp=sharing)

## Setup
```
python3 -m virtualenv env
source env/bin/activate
pip3 install -r requirements.txt
```

## Usage

Scrape the website (default):
```
python3 rep_scraper
```

Read a local XML relay list instead:
```
python3 rep_scraper --xml relay_list.xml
```

### XML input

The file must be an Excel 2003 XML (SpreadsheetML) workbook like `relay_list.xml`, with a header row followed by one repeater per row. These columns are used:

| Column | Content |
|--------|---------|
| 5 | Call sign |
| 7 | Validity date |
| 8 | QTH city |
| 10 | Tx frequency (MHz) |
| 11 | Rx frequency (MHz) |
| 15, 16 | EOV coordinates (X = northing, Y = easting) |

Notes:
- EOV coordinates are converted to a 6-character Maidenhead locator with `pyproj`, so the map positions are approximate, as with web scraping.
- Entries whose validity date has passed, and rows missing a call sign, frequency or coordinates, are skipped.
- The XML has no CTCSS or EchoLink data. CTCSS is left empty and `echolink.kml` is not generated.

Made by HA7DN, 2023
