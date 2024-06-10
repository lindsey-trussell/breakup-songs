import lyricsgenius
import csv
import logging
import os

# configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# set up credentials
genius_access_token = 'mPSXpz7Jw86bWU1m-s-rcp8PyS4OukGil1tV8Je7he4sb3AMXki8q8243DI3RttJ'

# authentication
genius = lyricsgenius.Genius(genius_access_token)

