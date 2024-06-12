import lyricsgenius
import csv
import logging
import os
import pandas as pd
import time

# configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# set up credentials
genius_access_token = 'mPSXpz7Jw86bWU1m-s-rcp8PyS4OukGil1tV8Je7he4sb3AMXki8q8243DI3RttJ'

# authentication
genius = lyricsgenius.Genius(genius_access_token)

# get lyrics using lyricsgenius
def get_lyrics(batch):
    lyrics = []
    for artist_name, track_name in batch:
        try:
            song = genius.search_song(track_name, artist_name)
            if song:
                lyrics.append(song.lyrics)
            else:
                lyrics.append('N/A')
        except Exception as e:
            logging.error(f"Error getting lyrics for {track_name} by {artist_name}: {e}")
            lyrics.append('N/A')
        time.sleep(1)
    return lyrics

#load data
input_csv = '../data/song_ids.csv'
songs = pd.read_csv(input_csv)

#search lyrics in batches
batch_size = 10
lyrics = []

for start in range(0, len(songs), batch_size):
    end = start + batch_size
    batch = songs.iloc[start:end][['artist_name', 'track_name']].values.tolist()
    batch_lyrics = get_lyrics(batch)
    lyrics.extend(batch_lyrics)
    logging.info(f"processed batch {start // batch_size + 1}")

#add column for lyrics
songs['lyrics'] = lyrics

#write new data into a csv file
output_csv = '../data/song_lyrics.csv'
songs.to_csv(output_csv, index=False)

print(f"lyrics for {len(songs)} songs written to {output_csv}")