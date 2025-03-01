import json
import os

import spotipy
import typst
from spotipy import SpotifyClientCredentials


def get_env_var(key):
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Environment variable {key} is required but not set.")
    return value


def format_german_date(date_str):
    date_parts = date_str.split("-")

    if len(date_parts) == 3:
        return f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"
    elif len(date_parts) == 2:
        return f"{date_parts[1]}.{date_parts[0]}"
    elif len(date_parts) == 1:
        return date_parts[0]
    return date_str


def get_playlist_tracks(sp, playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)

    while results:
        for item in results["items"]:
            track = item["track"]
            if track:
                tracks.append({
                    "name": track["name"],
                    "artist": ", ".join([artist["name"] for artist in track["artists"]]),
                    "release_date": format_german_date(track["album"]["release_date"]),
                    "url": track["external_urls"]["spotify"]
                })

        results = sp.next(results) if results["next"] else None

    return tracks


def main():
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=get_env_var("CLIENT_ID"),
            client_secret=get_env_var("CLIENT_SECRET"),
        )
    )

    songs = get_playlist_tracks(sp, get_env_var("PLAYLIST_ID"))

    with open("response.json", "w") as file:
        json.dump(songs, file, indent=4)

    typst.compile("hello.typ", output="hello.pdf")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
