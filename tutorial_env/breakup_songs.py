import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv
import random
import logging
import os

# configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# set up credentials
spotify_client_id = '62675215c6744e379289fe777b01a02f'
spotify_client_secret = 'b4437aac85b04594bacca57b94a87ea9'

# authentication
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

# setting up keywords and limits
keywords = ["breakup", "break up", "heartbreak"]
limit = 50
total_results = 20

# search for playlists by word
def search_playlists_by_keyword(word, limit, total_results):
    playlists = []
    for offset in range(0, total_results, limit):
        results = sp.search(q=f'playlists:{word}', type='playlist', limit=limit, offset=offset)
        playlists.extend([
            {
                'name':playlist['name'],
                'id':playlist['id'],
                'url':playlist['external_urls']['spotify']
            }
            for playlist in results['playlists']['items']
            if any(keyword.lower() in playlist['name'].lower() for keyword in keywords)
        ])
        if len(results['playlists']['items']) < limit:
            break
    return playlists

# get tracks from playlists
def get_playlist_tracks(playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    while results:
        tracks.extend(results['items'])
        if results['next']:
            results = sp.next(results)
        else:
            results = None
    return tracks

# get audio features for tracks
def get_audio_features(track_ids):
    features = {}
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i:i + 100]
        try:
            results = sp.audio_features(batch)
            features.update({feature['id']: feature for feature in results if feature})
        except Exception as e:
            logging.error(f"error getting audio features for batch at index {i}: {e}")
    return features

#get metadata from tracks
def get_track_metadata(tracks):
    track_data = []
    track_ids = [item['track']['id'] for item in tracks if item['track']]
    audio_features = get_audio_features(track_ids)
    for item in tracks:
        track = item['track']
        if track: # some items may be null
            features = audio_features.get(track['id'], {})
            track_info = {
                'track_name': track.get('name', 'N/A'),
                'track_id': track.get('id', 'N/A'),
                'album_name': track['album'].get('name', 'N/A') if track.get('album') else 'N/A',
                'album_id': track['album'].get('id', 'N/A') if track.get('album') else 'N/A',
                'artist_name': track['artists'][0].get('name', 'N/A') if track.get('artists') else 'N/A',
                'artist_id': track['artists'][0].get('id', 'N/A') if track.get('artists') else 'N/A',
                'track_popularity': track.get('popularity', 'N/A'),
                'explicit' : track.get('explicit', False),
                'track_url': track['external_urls'].get('spotify', 'N/A') if track.get('external_urls') else 'N/A',
                'danceability': features.get('danceability', 'N/A'),
                'energy': features.get('energy', 'N/A'),
                'key': features.get('key', 'N/A'),
                'loudness': features.get('loudness', 'N/A'),
                'mode': features.get('mode', 'N/A'),
                'speechiness': features.get('speechiness', 'N/A'),
                'acousticness': features.get('acousticness', 'N/A'),
                'instrumentalness': features.get('instrumentalness', 'N/A'),
                'liveness': features.get('liveness', 'N/A'),
                'valence': features.get('valence', 'N/A'),
                'tempo': features.get('tempo', 'N/A'),
                
            }
            track_data.append(track_info)
    return track_data

# search for playlists by word
all_playlists = []
for word in keywords:
    all_playlists.extend(search_playlists_by_keyword(word, limit, total_results))

# randomly pick 50 playlists
if len(all_playlists) > 50:
    all_playlists = random.sample(all_playlists, 50)

# print playlist query results
print(f"playlists:")

for idx, playlist in enumerate(all_playlists):
    print(f"{idx+1}. {playlist['name']}")
    print(f"   playlist id: {playlist['id']}")
    print(f"   link: {playlist['url']}\n")

# extract track metadata from each playlist and compile metadata
all_tracks_metadata = []
for playlist in all_playlists:
    tracks = get_playlist_tracks(playlist['id'])
    track_metadata = get_track_metadata(tracks)
    all_tracks_metadata.extend(track_metadata)

# write track metadata into csv file to perform data mining
csv_file = 'breakup_tracks_metadata.csv'
try:
    os.mkdir("./data")
except OSError as e:
    print(f"Directory exists")

with open("../data/" + csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['track_name', 'track_id', 'album_name', 'album_id', 'artist_name', 'artist_id', 'track_popularity', 'explicit', 'track_url','danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo'])
    writer.writeheader()
    writer.writerows(all_tracks_metadata)

print(f"metadata for {len(all_tracks_metadata)} tracks written to {csv_file}")
