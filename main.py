import json
import os
import random
import shutil
import argparse
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import qrcode
import spotipy
import typst
from spotipy import SpotifyClientCredentials
import qrcode.image.svg
import logging
import calendar

logging.basicConfig(level=logging.INFO)
random.seed("hitster")


def get_env_var(key):
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Environment variable {key} is required but not set.")
    return value


def resolve_date(date_str):
    date_parts = date_str.split("-")[::-1]
    parts = [""] * (3 - len(date_parts)) + date_parts

    day = f"{int(parts[0])}." if parts[0] else ""
    month = calendar.month_name[int(parts[1])] if parts[1] else ""
    year = parts[2]

    return day, month, year


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

    random.shuffle(songs)
    return songs


def generate_qr_codes(songs):
    if os.path.isdir("qr_codes"):
        shutil.rmtree("qr_codes")
    os.mkdir("qr_codes")

    for song in songs:
        img = qrcode.make(song["url"], image_factory=qrcode.image.svg.SvgPathImage)
        img.save(f"qr_codes/{song['id']}.svg")


def generate_overview_pdf(songs, output_pdf):
    year_counts = Counter(int(song["year"]) for song in songs if "year" in song)

    min_year = min(year_counts.keys())
    max_year = max(year_counts.keys())
    all_years = list(range(min_year, max_year + 1))
    counts = [year_counts.get(year, 0) for year in all_years]

    plt.figure()
    plt.bar(all_years, counts, color="black")
    plt.ylabel("number of songs released")
    plt.xticks()

    with PdfPages(output_pdf) as pdf:
        pdf.savefig()
        plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Generate Hitster game cards from a Spotify playlist",
    )
    
    parser.add_argument("playlist_id",
        help="Spotify playlist ID to generate cards from (overrides PLAYLIST_ID env var)",
        type=str,
        nargs="?",
    )
    
    args = parser.parse_args()
    
    # Use command line argument if provided, otherwise fall back to environment variable
    playlist_id = args.playlist_id if args.playlist_id else get_env_var("PLAYLIST_ID")
    
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=get_env_var("CLIENT_ID"),
            client_secret=get_env_var("CLIENT_SECRET"),
        )
    )

    logging.info(f"Starting Spotify song retrieval for playlist: {playlist_id}")
    songs = get_playlist_songs(sp, playlist_id)

    logging.info("Writing songs to songs.json file")
    with open("songs.json", "w") as file:
        json.dump(songs, file, indent=4)

    logging.info("Generating QR codes")
    generate_qr_codes(songs)

    logging.info("Compiling Cards PDF")
    typst.compile("hitster-cards.typ", output="hitster-cards.pdf")

    logging.info("Compiling Year Overview PDF")
    generate_overview_pdf(songs, "hitster-overview.pdf")

    logging.info("Done")


if __name__ == "__main__":
    main()
