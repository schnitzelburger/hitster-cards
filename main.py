import json
import os
import shutil
import qrcode
import spotipy
import typst
from spotipy import SpotifyClientCredentials
import qrcode.image.svg
import logging

logging.basicConfig(level=logging.INFO)


def get_env_var(key):
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Environment variable {key} is required but not set.")
    return value


def resolve_date(date_str):
    date_parts = date_str.split("-")[::-1]  # Reverse to get year first
    return tuple(["01"] * (3 - len(date_parts)) + date_parts)


def get_playlist_songs(sp, playlist_id):
    songs = []
    results = sp.playlist_tracks(playlist_id)

    while results:
        for item in results["items"]:
            track = item["track"]
            if track:
                day, month, year = resolve_date(track["album"]["release_date"])
                songs.append(
                    {
                        "name": track["name"],
                        "artists": [artist["name"] for artist in track["artists"]],
                        "day": day,
                        "month": month,
                        "year": year,
                        "release_date": track["album"]["release_date"],
                        "url": track["external_urls"]["spotify"],
                        "id": track["id"],
                    }
                )

        results = sp.next(results) if results["next"] else None

    return songs


def generate_qr_codes(songs):
    if os.path.isdir("qr_codes"):
        shutil.rmtree("qr_codes")
    os.mkdir("qr_codes")

    for song in songs:
        img = qrcode.make(song["url"], image_factory=qrcode.image.svg.SvgPathImage)
        img.save(f"qr_codes/{song["id"]}.svg")


def main():
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=get_env_var("CLIENT_ID"),
            client_secret=get_env_var("CLIENT_SECRET"),
        )
    )

    logging.info("Starting Spotify song retrieval")
    songs = get_playlist_songs(sp, get_env_var("PLAYLIST_ID"))

    logging.info("Writing songs to file")
    with open("songs.json", "w") as file:
        json.dump(songs, file, indent=4)

    logging.info("Generating QR codes")
    generate_qr_codes(songs)

    logging.info("Compiling PDF")
    typst.compile("hitster.typ", output="hitster.pdf")

    logging.info("Done")


if __name__ == "__main__":
    main()
