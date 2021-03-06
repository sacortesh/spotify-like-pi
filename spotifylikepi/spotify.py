import spotipy
import auth
import sched, time
import threading



class Client:
    def __init__(self):
        self._token_dispenser = auth.TokenDispenser()
        self.spotify_username = self._token_dispenser.spotify_username
        self.spotify = spotipy.Spotify(auth=self._token_dispenser.spotify_token)
        self.playlist_id = self._token_dispenser.spotify_playlist_uid
        self.stop_refresh = False
        self.request_token_refresh_async()

    def request_token_refresh_async(self):
        print('>>>Scheduled refresh call')

        self._token_dispenser.refresh_token()
        self.spotify = spotipy.Spotify(auth=self._token_dispenser.spotify_token)

        if not self.stop_refresh:
            t = threading.Timer(3000, self.request_token_refresh_async)
            t.daemon = True
            t.start()
        
        return

    def fetch_now_playing(self):
        current_track = self.spotify.currently_playing(None, None)
        return current_track

    def validate_playlist(self):
        result = False
        try:
            playlist_object = self.spotify.playlist(self.playlist_id)
            result=True
        except:
            result = False
        
        return result

    def fetch_playlist(self):
        result = None
        try:
            result = self.spotify.playlist(self.playlist_id)
        except: 
            result = None

        return result


    def send_like(self, song):
        song_array = []
        song_array.append(song['item']['id'])
        self.spotify.current_user_saved_tracks_add(song_array)
        return

    def persist_song(self, song, playlist):
        if self.playlist_has_song(playlist['id'], song['item']['id']):
            print('>>>Duplicate detected. Ignoring')
            return
        song_array = []
        song_array.append(song['item']['id'])
        self.spotify.playlist_add_items(playlist['id'],song_array)
        return

    def playlist_has_song(self, playlist_id, song_id):
        exists = False
        playlist_data = self.spotify.playlist_tracks(playlist_id, 'items(track(id))')['items']
        
        for x in playlist_data:
            if x['track']['id'] == song_id:
                exists = True

        return exists

