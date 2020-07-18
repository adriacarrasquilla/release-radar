# -*- coding: utf-8 -*-

import os
import csv
import sys
import getopt
import numpy as np
import secret
import spotipy
import datetime
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

# GLOBALS

username = secret.username

playlists = [{'name': 'hardstyle', 'id': '2m7IlNkYjwT69uIhOyYLMi'},
             {'name': 'tech-house', 'id': '6ujpImBo1z4YfWHK7oiiTD'},
             {'name': 'hardcore', 'id': '1wWcVDacL95OpUb4oHUZpD'},
             {'name': 'techno', 'id': '0HILYg2jeV6mOYiXBw125R'},
             {'name': 'merda', 'id': '67ctnFOT7EIHdfrzrzVWqX'},
             {'name': 'chill', 'id': '2yXIvGjxSR2BqL1UZRinIm'},
             {'name': 'trap', 'id': '3pWw2pJgEu8AEXWit9Nw3x'},
             {'name': 'acoustic', 'id': '3mWAb5gVnxOLZqG5GgLeM6'}]

playlistsNames = ['hardstyle', 'tech-house', 'hardcore', 'techno', 'merda', 'chill', 'trap', 'acoustic']

helptxt = "HELP"


def getTracksFromAlbum(albumID, sp):
    """
    :param albumID:
    :param sp: spotipy.Spotify() object
    :return: track ids
    """
    tracks = sp.album_tracks(albumID)
    trackIDs = []
    trackNames = []
    trackArtists = []
    for track in tracks['items']:
        if len(trackNames) == 0:
            trackIDs.append(track['id'])
            trackNames.append(track['name'].split(" - ")[0])
            trackArtists.append(track['artists'][0]['name'])
        else:
            if track['name'].split(" - ")[0] not in trackNames:
                trackIDs.append(track['id'])
                trackNames.append(track['name'].split(" - ")[0])
                trackArtists.append(track['artists'][0]['name'])

    return trackIDs, trackNames, trackArtists


def getNewTracks(artists):
    """
    Checks new albums(singles) for all artists and returns top 50 newest tracks
    :param artists: csv file with name;id format
    :return: top 50 newest tracks
    """
    client_credentials_manager = SpotifyClientCredentials()
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    newAlbums = []
    with open(artists, encoding='utf-8') as file:
        print('Checking artists new releases.')
        reader = csv.reader(file, delimiter=';')
        for artist in reader:
            birdy_uri = 'spotify:artist:%s' % artist[1]
            tracks = spotify.artist_albums(birdy_uri, 'single')
            albums = tracks['items']
            while tracks['next']:
                tracks = spotify.next(tracks)
                albums.extend(tracks['items'])

            artistAlbums = []
            for album in albums:
                artistAlbums.append([album['release_date'], album['id']])

            artistAlbums = sorted(artistAlbums, key=lambda d: tuple(map(int, d[0].split('-'))), reverse=True)
            for a in artistAlbums[:5]:
                newAlbums.append(a)

    newAlbums = np.array(sorted(newAlbums, key=lambda d: tuple(map(int, d[0].split('-'))), reverse=True), dtype=object)
    newAlbumsFiltered = list(dict.fromkeys(newAlbums[:, 1]))

    newTracksDict = {}
    nameNewTracksDict = {}
    print('Sorting and selecting tracks.')
    for album in newAlbumsFiltered[:100]:
        trackID, trackName, trackArtist = getTracksFromAlbum(album, spotify)
        for i in range(len(trackID)):
            newTracksDict[trackName[i][:10]] = trackID[i]
            nameNewTracksDict[trackName[i][:10]] = trackName[i] + " - " + trackArtist[i]

    print("TRACKS IN QUEUE:")
    for song in list(nameNewTracksDict.values())[:50]:
        print(song)

    return list(newTracksDict.values())[:50]


def removeTracksFromPlaylist(playlistID, spotify):
    print('Removing old tracks.')
    tracks = spotify.user_playlist(username, playlistID, fields='tracks')['tracks']['items']
    removeTracks = []
    for tr in tracks:
        if tr['track'] != None:
        	removeTracks.append(tr['track']['id'])

    remove = spotify.user_playlist_remove_all_occurrences_of_tracks(username, playlistID, removeTracks)


def uploadTracksToPlaylist(playlistID, tracks):
    """

    :param playlistID: playlist to upload
    :param tracks: list of track ids
    :return:
    """
    scope = 'playlist-modify-public'
    try:
        token = util.prompt_for_user_token(username, scope)
    except:
        os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(username, scope)

    spotify = spotipy.Spotify(auth=token)
    spotify.trace = False

    removeTracksFromPlaylist(playlistID, spotify)

    print("Uploading new tracks to playlist.")
    for track in tracks:
        try:
            results = spotify.user_playlist_add_tracks(username, playlistID, [track])
        except:
            print(f"Error uploading track: {track}")
    print("%s tracks added.\n" % len(tracks))


def argParse(argv):
    try:
        opts, args = getopt.getopt(argv[1:], "hap:", ["help", "all", "playlist="])
    except getopt.GetoptError:
        print("\nUnexpected argument values, showing script help...")
        print(helptxt)
        sys.exit(2)

    updateAll = False
    updatePlaylists=[]

    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print(helptxt)
            sys.exit(2)
        elif opt in ["-a", "--all"]:
            updateAll = True
            updatePlaylists = playlists
        elif opt in ["-p", "--playlist"]:
            if updateAll:
                break
            for p in arg.split(" "):
                if p not in playlistsNames:
                    print('Playlist name "%s" invalid.' % p)
                else:
                    updatePlaylists.append(p)
            if len(updatePlaylists) == 0:
                print('There are 0 matches.')
                print(helptxt)
                sys.exit(2)
            else:
                aux = []
                for p in updatePlaylists:
                    aux.append(playlists[playlistsNames.index(p)])
                updatePlaylists = aux

        else:
            print("Not a valid option", helptxt)
            sys.exit(2)

        return updatePlaylists


if __name__ == "__main__":
    os.environ["SPOTIPY_CLIENT_ID"] = secret.client_id
    os.environ["SPOTIPY_CLIENT_SECRET"] = secret.client_secret
    os.environ["SPOTIPY_REDIRECT_URI"] = secret.redirect_uri
    os.chdir('/Users/Adria/Documents/SpotyRadar/')

    updatePlaylists = argParse(sys.argv)

    print("----------------------")
    print("      %s      " % datetime.date.today())
    print("----------------------")

    for p in updatePlaylists:
        print("Updating %s playlist...\n" % p['name'])
        new_tracks = getNewTracks('artistsByGenre/%s.csv' % p['name'])
        uploadTracksToPlaylist(p['id'], new_tracks)
        print("DONE\n")

