# HA2TO repater scraper

This python script scrapes the page [Magyarországi VHF és UHF rádióamatőr átjátszók](http://ha2to.orbel.hu/content/repeaters/hu/index.html), or reads a local XML relay list, and generates 4 files:
- `repeaters_old_chirp.csv` and `repeaters_new_chirp.csv` for CHIRP (old and new CSV formats)
- `repeaters.kml` with approximate coordinates for mapping software. Points are grouped into FM, DMR and C4FM folders (layers in Google My Maps), plus a "Digipeater / Simplex" folder for "P" digipeaters (e.g. HG2PBA) and simplex entries (same downlink and uplink); a repeater with several modes appears in each of its layers. Color = band (red = 2m, blue = 70cm). Shape = type: house = private ("egyéni", XML input only), star = multiple modes, square = DMR, triangle = C4FM, circle = FM only
- `echolink.kml` similar to `repeaters.kml` but only contains EchoLink-enabled repeaters (web scraping only)

For the maps, see [the generated map on google maps](https://www.google.com/maps/d/edit?mid=1pecdCCsx2C0F0qW0n-bFy2ZnTRufJyo&usp=sharing)

## Setup
```
python3 -m virtualenv env
source env/bin/activate
pip3 install -r requirements.txt
```

## Usage

Without arguments the help is printed. Choose the data source(s):

| Option | Source |
|--------|--------|
| `--ha2to` | scrape the HA2TO website |
| `--nmhh` | download the NMHH list (https://nmhh.hu/amator/relay_list.xml) |
| `--xml PATH` | read a local XML file (same format as the NMHH list) |
| `--ctcss` | add the CTCSS zones by county as a layer to `repeaters.kml` |

`--nmhh` and `--xml` cannot be combined. `--ha2to` can be combined with either of them, in which case the two lists are merged by call sign:
```
python3 rep_scraper --ha2to
python3 rep_scraper --nmhh
python3 rep_scraper --ha2to --nmhh
python3 rep_scraper --ha2to --xml relay_list.xml
python3 rep_scraper --nmhh --ctcss
```

### CTCSS zones

With `--ctcss`, `repeaters.kml` gets an extra "CTCSS" folder (layer) with the counties colored by their CTCSS tone (semi-transparent polygons):

| Tone | Color | Counties |
|------|-------|----------|
| 74.4 Hz | green | Somogy, Baranya, Tolna |
| 107.2 Hz | blue | Győr-Moson-Sopron, Vas, Zala, Veszprém, Komárom-Esztergom, Fejér |
| 114.8 Hz | pink | Pest (including Budapest), Nógrád, Heves, Borsod-Abaúj-Zemplén, Jász-Nagykun-Szolnok |
| 131.8 Hz | yellow | Szabolcs-Szatmár-Bereg, Hajdú-Bihar, Bács-Kiskun, Csongrád-Csanád, Békés |

The county boundaries are in `data/hu_counties.geojson` (from [geoBoundaries](https://www.geoboundaries.org/), HUN ADM1, CC0). The zones are defined in `rep_scraper/ctcss_zones.py`.

### Merging

For call signs in both sources, the XML provides the frequencies, modes and ownership. HA2TO provides the QTH (site name and locator), the CTCSS tones and the EchoLink code. Call signs in only one source are kept as they are. The CTCSS is shown in the map description whenever it is known.

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
- EOV coordinates are converted to a 6-character Maidenhead locator with `pyproj`, so the map positions are approximate, as with web scraping. The order of the two coordinate columns varies between rows, so northing (< 400000) and easting (> 400000) are detected by value. Rows outside Hungary are skipped with a warning.
- Rows with the same call sign are merged into one repeater. The map description lists every mode (FM, C4FM, DMR) with its downlink and uplink frequency. The CHIRP files use the first row's frequency.
- Only 2m and 70cm rows are used; other bands (e.g. microwave links) are skipped.
- Entries whose validity date has passed, and rows missing a call sign, frequency or coordinates, are skipped.
- The XML has no CTCSS or EchoLink data. CTCSS is left empty and `echolink.kml` is only generated when merged with HA2TO data.

Made by HA7DN, 2023

Contributors: HG3PE Pepó
