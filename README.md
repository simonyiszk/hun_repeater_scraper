# HA2TO repater scraper

This python script scrapes the page [Magyarországi VHF és UHF rádióamatőr átjátszók](http://ha2to.orbel.hu/content/repeaters/hu/index.html) and generates 3 files:
- `repeaters.csv` for ChIRP
- `repeaters.kml` with approximate coordinates for mapping software (red pin = 2m repeater, blue pin = 70cm repeater)
- `echolink.kml` similar to `repeaters.kml` but only contains EchoLink-enabled repeaters

For the maps, see [the generated map on google maps](https://www.google.com/maps/d/edit?mid=1pecdCCsx2C0F0qW0n-bFy2ZnTRufJyo&usp=sharing)

Made by HA7DN, 2023
