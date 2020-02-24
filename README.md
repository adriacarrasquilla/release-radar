# Release-Radar

Environment for an automatic Spotify playlist that uploads periodically the top 50 newest tracks from a dataset of artists.

It can be used from a genre release radar to a custom made artist dataset radar.


## Usage
### Spotify API

This script uses Spotipy library as main resource to connect with Spotify's API. Check out their documentation here: https://spotipy.readthedocs.io/en/2.9.0/

In order to use its features, a developer account is required. If you don't have one, access here to upgrade your account (free) or create it from 0: https://developer.spotify.com

### Secret
Secret.py contains information about your account so the script is able to run properly according your configuration. It __must__ be filled with your own credentials to make it work.

Variables:

* `client_id` : Client ID of your Spotify developer app

* `client_secret` : Client secret ID of your Spotify developer app

* `redirect_uri` : URL specified in your Spotify developer app's *Redirect URI*

* `username` : ID of your Spotify account

* `playlists` : Python list of dictionaries containing playlists to update info.

```python
[{'name': 'PlaylistToUpdate', 'id': 'PlaylistID'}, ...]
```
* `playlistsNames` : Python list containing only the name of all playlists to update names. __IMPORTANT:__ Make sure the playlist name is the same as the *playlist.csv* file name explained in the following section. 
```python
['PlaylistToUpdate1', 'PlaylistToUpdate2', ...]
```

### getArtists
In order to make the main script work, we need a kind of artists dataset. Due to simplicity of data needs, this info will be stored in a csv containing in each row an artist. Columns:
1. __Artist Name__
2. __Artist ID__

*Separated by ';'*

Artist name is stored in order to ease manual edits of the file.

Getting this information manually can be quite tedious. In order to speed things up we can use getArtists.py. This script saves all artists that appear on a playlist into a csv file following the same rules from above.

Usage:

```
Option     GNU long option    Meaning
-h         --help             Show this message
-i         --id               Id of the playlist to read from
-n         --name             Name of the playlist. Will save a csv with this name
-m <str>   --merge            Given a name, update that list with new playlists 'id1 name1 ...'
```

#### Examples

__Create playlistName from playlist with specified ID__

```
python getArtists.py -i PlaylistID -n PlaylistName
```

__Merge MainPlaylist with playlistAux1 and playlistAux2__

```
python getArtists.py -n MainPlaylist -m 'IDAux1 playlistAux1 IDAux2 playlistAux2'
```

### UpdatePlaylists

This is the main script that will search for new released tracks and update them to the specified playlist.

```
Option      GNU long option     Meaning
-h          --help              Show this message
-a          --all               Update all playlists
-p <str>    --playlist          Update specific playlists by name.
```
#### Examples

__Update all playlists specified on secret.py__

```
python updatePlaylists.py -a
```

__Update only p1, p2 and p3 (if exist in playlists from secret.py)__

```
python updatePlaylists.py -p "p1 p2 p3"
```


#### Script steps
1. Remove tracks from playlist to update if there is any.

2. For each artist in playlist.csv:
    1. Get all single/albums
    2. Sort them by date
    3. Append to list of album the top 5 newest from that artist
3. Once all artists have been checked, sort album list by date and limit its length to 100 albums.
4. For each album in album list, append its track(s) to tracks list.
5. Return first 50 tracks and upload them to specified playlist.

> Note that steps 2, 3 and 4 use python dictionaries and other techniques to avoid duplicated elements and repetitive tracks (e.g. album full of remixes from same song)

#### Make it run periodically with crontab
You can use any job scheduler to update daily, weekly, monthly or any period of your interest so your playlist is always up to date (instead of running the command every single time). For unix users, crontab is a quite simple option.
