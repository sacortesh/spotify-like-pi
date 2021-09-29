import json
import os

import appdirs
import spotipy
import spotipy.util


class TokenDispenser:
    def __init__(self):
        self._token = None
        self._credentials = None
        self._token_info = None

    @property
    def spotify_token(self):
        if self._token is None:
            token_info = load_token_info()
            token = None
            if token_info:
                token = token_info['access_token']
                token_response = token_info

                if not is_token_valid(token):
                    self._token = token
                    self._token_info = token_response
                    self.refresh_token()

            if token_info is None or not is_token_valid(token):
                token_response = self.get_oauth_token()
                save_token_info(token_response)

            self._token = token_response['access_token']
            self._token_info = token_response

        return self._token

    def get_oauth_token(self):
        sp_oauth = spotipy.oauth2.SpotifyOAuth(
            client_id=self.spotify_client_id,
            client_secret=self.spotify_client_secret,
            redirect_uri=self.spotify_redirect_uri,
            scope="user-library-read playlist-read-private user-read-currently-playing playlist-modify-private playlist-modify-public user-library-modify",
        )
        auth_url = sp_oauth.get_authorize_url()
        print(auth_url)
        response = input('Paste the above link into your browser, then paste the redirect url here: ')

        code = sp_oauth.parse_response_code(response)
        token_data = sp_oauth.get_access_token(code)

        return token_data

    def refresh_token(self):
        print('refreshing token')
        if self._token_info is None:
            return

        print('i can do stuff')

        sp_oauth = spotipy.oauth2.SpotifyOAuth(
            client_id=self.spotify_client_id,
            client_secret=self.spotify_client_secret,
            redirect_uri=self.spotify_redirect_uri,
            scope="user-library-read playlist-read-private user-read-currently-playing playlist-modify-private playlist-modify-public user-library-modify",
        )

        if sp_oauth.is_token_expired(self._token_info):
            self._token_info = sp_oauth.refresh_access_token(self._token_info['refresh_token'])
            self._token = self._token_info['access_token']
            save_token(self._token)
            save_token_info(self._token_info)

    @property
    def credentials(self):
        if self._credentials is None:
            try:
                credentials = load_credentials()
            except CredentialsNotFound as e:
                credentials = ask_for_credentials(**e.credentials_found)
                save_credentials(*credentials)
            self._credentials = credentials
        return self._credentials

    @property
    def spotify_username(self):
        return self.credentials[0]

    @property
    def spotify_client_id(self):
        return self.credentials[1]

    @property
    def spotify_client_secret(self):
        return self.credentials[2]

    @property
    def spotify_redirect_uri(self):
        return self.credentials[3]

    @property
    def spotify_playlist_uid(self):
        return self.credentials[4]


def load_token():
    token_path = get_token_path()
    if not os.path.exists(token_path):
        return None
    with open(token_path) as token_file:
        return token_file.read().strip()

def load_token_info():
    token_path = get_token_info_path()
    if not os.path.exists(token_path):
        return None
    with open(token_path) as token_file:
        try:
            return json.load(token_file)
        except:
            return None

def save_token(token):
    token_path = get_token_path()
    check_directory_exists(token_path)
    with open(token_path, "w") as token_file:
        token_file.write(token)


def save_token_info(token):
    token_path = get_token_info_path()
    check_directory_exists(token_path)
    with open(token_path, "w") as token_file:
        json.dump(
            {
                "access_token": token['access_token'],
                "refresh_token": token['refresh_token'],
                "expires_at": token['expires_at']
            },
            token_file,
        )

def is_token_valid(token):
    try:
        spotify_client = spotipy.Spotify(auth=token)
        spotify_client.current_user()
    except spotipy.client.SpotifyException:
        return False
    return True


def load_credentials():
    credentials_path = get_credentials_path()
    if not os.path.exists(credentials_path):
        raise CredentialsNotFound("Credentials file not found or not readable")
    credentials = {}
    try:
        with open(credentials_path) as credentials_file:
            credentials = json.load(credentials_file)
        return (
            credentials["USERNAME"],
            credentials["CLIENT_ID"],
            credentials["CLIENT_SECRET"],
            credentials["REDIRECT_URI"],
            credentials["PLAYLIST_UID"],
        )
    except (ValueError, KeyError):
        raise CredentialsNotFound("Could not parse credentials file", **credentials)


def ask_for_credentials(**credentials_found):
    print(
        """You need to register as a developer and create a Spotify app in order to use spotify-like-pi.
You may create an app here: https://developer.spotify.com/my-applications/#!/applications/create
Please enter your app credentials:"""
    )
    username = credentials_found.get("USERNAME") or input("Spotify username: ")
    client_id = credentials_found.get("CLIENT_ID") or input("Spotify client ID: ")
    client_secret = credentials_found.get("CLIENT_SECRET") or input(
        "Spotify client secret: "
    )
    redirect_uri = credentials_found.get("REDIRECT_URI") or input(
        "Spotify redirect URI: "
    )
    spotify_playlist_uid = credentials_found.get("PLAYLIST_UID") or input(
        "Target spotify playlist id: "
    )
    return username, client_id, client_secret, redirect_uri, spotify_playlist_uid


def save_credentials(
    username, client_id, client_secret, redirect_uri, spotify_playlist_uid
):
    credentials_path = get_credentials_path()
    print("Saving Spotify and Youtube credentials to", credentials_path)
    check_directory_exists(credentials_path)
    with open(credentials_path, "w") as credentials_file:
        json.dump(
            {
                "USERNAME": username,
                "CLIENT_ID": client_id,
                "CLIENT_SECRET": client_secret,
                "REDIRECT_URI": redirect_uri,
                "PLAYLIST_UID": spotify_playlist_uid,
            },
            credentials_file,
        )


def check_directory_exists(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_credentials_path():
    return get_config_file_path("credentials.json")


def get_token_path():
    return get_config_file_path("spotify.token")

def get_token_info_path():
    return get_config_file_path("spotify.tokeninfo")


def get_config_file_path(filename):
    # We used to store config files in ~/.local, so we still need to
    # support config files stored there
    config_dir = os.path.expanduser("~/.local/share/spotifylikepi/")

    # This is the more modern way of storing config files (cross-platform)
    if not os.path.exists(config_dir):
        config_dir = appdirs.user_config_dir("spotifylikepi")

    return os.path.join(config_dir, filename)


class CredentialsNotFound(Exception):
    def __init__(self, message, **credentials_found):
        super(CredentialsNotFound, self).__init__(message)
        self.credentials_found = credentials_found