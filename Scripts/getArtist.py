# -*- coding: utf-8 -*-

import os
import sys
import csv
import math
import getopt
import secret
import spotipy
import spotipy.util as util

username = secret.username

helptxt="Usage: python getArtist [OPTIONS] [VALUES]...\n\n"\
		  "Option 		GNU long option 	Meaning\n" \
 		  "-h 		--help 			Show this message\n" \
 		  "-i 		--id 			id of the playlist to read from\n" \
 		  "-n 		--name 			name of the playlist. Will save a csv\n"\
 		  "					with this name\n" \
 		  "-m <str>	--merge 		Given a name, update that list with\n"\
 		  "				 	new playlists 'id1 name1 ...'"


def mergeCsv(file1, file2):
    artists = {}
    with open(file1, 'r') as f1:
        reader = csv.reader(f1, delimiter=';')
        for line in reader:
            artists[line[0]] = line[1]
        with open(file2, 'r') as f2:
            reader = csv.reader(f2, delimiter=';')
            for line in reader:
                artists[line[0]] = line[1]
    with open(file1, 'w') as f1:
        for a in artists.items():
            f1.write("%s;%s\n" % (a[0], a[1]))


def printTracksFromPlaylist(playlistID):
    scope = 'playlist-modify-public'
    try:
        token = util.prompt_for_user_token(username, scope)
    except:
        os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(username, scope)

    spotify = spotipy.Spotify(auth=token)
    spotify.trace = False

    ntracks = spotify.user_playlist(username, playlistID)['tracks']['total']
    artists = {}
    for chunk in range(math.ceil(ntracks / 100)):
        r = spotify.user_playlist_tracks(username, playlistID, offset=chunk * 100)
        for track in r['items']:
            print(track['track']['album']['id'])


def getArtistsFromPlaylist(genre, playlistID):
    """
    Creates csv file containing artists to check new releases from (name+id)
    :param genre: name of the csv file
    :param playlistID
    :return:
    """
    scope = 'playlist-modify-public'
    try:
        token = util.prompt_for_user_token(username)
    except:
        os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(username, scope)
    spotify = spotipy.Spotify(auth=token)
    spotify.trace = False

    ntracks = spotify.user_playlist(username, playlistID)['tracks']['total']
    artists = {}
    for chunk in range(math.ceil(ntracks / 100)):
        r = spotify.user_playlist_tracks(username, playlistID, offset=chunk * 100)
        for track in r['items']:
            for artist in track['track']['album']['artists']:
                artists[artist['name']] = artist['id']

    with open('../Artists/%s.csv' % genre, 'w') as file:
        for a in artists.items():
            file.write('%s;%s\n' % (a[0], a[1]))


if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hn:i:m:", ["help", "name=", "id=", "merge:"])
    except getopt.GetoptError:
        print("\nUnexpected argument values, showing script help...")
        print(helptxt)
        sys.exit(2)

    pid = None
    name = None
    mergeIDs = None
    mergeNames = None
    merge = False

    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print(helptxt)
            sys.exit(2)
        elif opt in ["-n", "--name"]:
            name = arg
        elif opt in ["-i", "--id"]:
            pid = arg
        elif opt in ["-m", "--merge"]:
        	merge = True
        	mergeIDs= arg.split()[0:][::2]
        	mergeNames= arg.split()[1:][::2]
        	if len(mergeIDs) != len(mergeNames):
        		print('USAGE: --merge "id1 name1 id2 name2 ..."')
        		sys.exit(2)
        else:
            print("Not a valid option", helptxt)
            sys.exit(2)

    print(pid, name, mergeIDs, mergeNames)

    os.environ["SPOTIPY_CLIENT_ID"] = secret.client_id
    os.environ["SPOTIPY_CLIENT_SECRET"] = secret.client_secret
    os.environ["SPOTIPY_REDIRECT_URI"] = secret.redirect_uri

    if merge:
        for i in range(len(mergeIDs)):
            getArtistsFromPlaylist(mergeNames[i], mergeIDs[i])
            mergeCsv("../Artists/%s.csv", "../Artists/%s.csv" % (name , mergeNames[i]))
    else:
    	getArtistsFromPlaylist(name, pid)
