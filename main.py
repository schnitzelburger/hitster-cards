import json
import os
import random
import shutil
import argparse
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import locale
import datetime

from dotenv import load_dotenv
load_dotenv()

import qrcode
import spotipy
import typst
from spotipy import SpotifyClientCredentials
import qrcode.image.svg
import logging
import calendar

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
random.seed("hitster")


def get_env_var(key):
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Environment variable {key} is required but not set.")
    return value


def resolve_date(date_str: str, month_lang=None, no_day=False) -> tuple[str, str, str]:
    date_parts = date_str.split("-")[::-1]
    parts = [""] * (3 - len(date_parts)) + date_parts

    day = "" if no_day else (f"{int(parts[0])}." if parts[0] else "")
    if parts[1]:
        if month_lang == "de":
            try:
                locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
            except locale.Error:
                pass
        elif month_lang == "en":
            try:
                locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
            except locale.Error:
                pass
        month = calendar.month_name[int(parts[1])]
    else:
        month = ""
    year = parts[2]

    return day, month, year


def get_playlist_songs(sp, playlist_id, verbose=False, month_lang=None, no_day=False, added_after=None) -> list[dict[str, str]]:
    songs = []
    results = sp.playlist_tracks(playlist_id)

    while results:
        # with open("results.json", "w") as f:
        #     json.dump(results, f, indent=4)
        for item in results["items"]:
            track = item["track"]
            if track:
                day, month, year = resolve_date(track["album"]["release_date"], month_lang=month_lang, no_day=no_day)
                added_at = item["added_at"]  # format: "YYYY-MM-DDTHH:MM:SSZ"
                # Only add if added_after is not set or added_at > added_after
                add_song = True
                if added_after:
                    try:
                        added_after_dt = datetime.datetime.strptime(added_after, "%Y-%m-%d")
                        added_at_dt = datetime.datetime.strptime(added_at[:10], "%Y-%m-%d")
                        add_song = added_at_dt > added_after_dt
                    except Exception as e:
                        logger.warning(f"Could not filter by added_after: {e}")
                        add_song = True
                if add_song:
                    song = {
                        "name": track["name"],
                        "artists": [artist["name"] for artist in track["artists"]],
                        "day": day,
                        "month": month,
                        "year": year,
                        "release_date": track["album"]["release_date"],
                        "url": track["external_urls"]["spotify"],
                        "id": track["id"],
                    }
                    songs.append(song)
                    if verbose:
                        artists_str = ', '.join(song['artists'])
                        if len(artists_str) > 24:
                            artists_str = artists_str[:23] + '…'
                        logger.debug(f"Song: {song['name']:<28} | Artists: {artists_str:<24} | Release Date: {song['release_date']}")
        results = sp.next(results) if results["next"] else None

    # Sort songs by release_date (YYYY-MM-DD)
    songs.sort(key=lambda song: song.get("release_date") or "0000-00-00")
    return songs


def generate_qr_codes(songs: list[dict[str, str]], qr_type: str = "url") -> None:
    if os.path.isdir("qr_codes"):
        shutil.rmtree("qr_codes")
    os.mkdir("qr_codes")

    for song in songs:
        if qr_type == "id":
            qr_content = song["id"]
        else: # default to "url"
            qr_content = song["url"]
        img = qrcode.make(qr_content, image_factory=qrcode.image.svg.SvgPathImage)
        with open(f"qr_codes/{song['id']}.svg", "wb") as f:
            img.save(f)


def generate_year_distribution_pdf(songs: list[dict[str, str]], output_pdf: str) -> None:
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
    parser = argparse.ArgumentParser(description="Generate Hitster game cards from a Spotify playlist")
    parser.add_argument("playlist_id", type=str, nargs="?", help="Spotify playlist ID to generate cards from (overrides PLAYLIST_ID env var)", default=None)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output (show each song)")
    parser.add_argument("--cards-pdf", default="hitster-cards.pdf", help="Output PDF filename for cards")
    parser.add_argument("--overview-pdf", default="year-distribution.pdf", help="Output PDF filename for year distribution bar chart")
    parser.add_argument("--month-lang", choices=["de", "en"], default=None, help="Language for month names in release dates (default: system locale)")
    parser.add_argument("--no-day", action="store_true", help="Omit day from release date (set day to empty string)")
    parser.add_argument("--qr-type", choices=["url", "id"], default="url", help="QR code content: url (default) or id")
    parser.add_argument("--added-after", type=str, help="Only include songs added after this date (YYYY-MM-DD)")
    parser.add_argument("--edition", type=str, default=None, help="Edition label to display on the cards (e.g., 'Summer 2025').")
    args = parser.parse_args()

    playlist_id = args.playlist_id or os.getenv("PLAYLIST_ID")
    if not playlist_id:
        parser.error("No playlist_id provided and PLAYLIST_ID env var not set.")

    # Set logging level for this module only
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Overview of used arguments
    logger.info("""
========== Hitster Cards - Argument Overview ==========
Playlist ID:         %s
Month Language:      %s
Day in Release Date: %s
QR Code Content:     %s
Cards PDF Output:    %s
Year Distribution:   %s
Added After:         %s
Edition:             %s
=======================================================
""" % (
        playlist_id,
        args.month_lang if args.month_lang else 'default system locale',
        'omitted' if args.no_day else 'included',
        args.qr_type,
        args.cards_pdf,
        args.overview_pdf,
        args.added_after if args.added_after else 'not set',
        args.edition if args.edition else 'not set',
    ))

    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=get_env_var("CLIENT_ID"),
            client_secret=get_env_var("CLIENT_SECRET"),
        )
    )

    logger.info(f"Starting Spotify song retrieval for playlist: {playlist_id}")
    songs = get_playlist_songs(sp, playlist_id, verbose=args.verbose, month_lang=args.month_lang, no_day=args.no_day, added_after=args.added_after)

    logger.info(f"Number of songs (after filtering): {len(songs)}")

    logger.info("Writing songs to songs.json file")
    with open("songs.json", "w") as file:
        json.dump(songs, file, indent=4)

    logger.info("Generating QR codes")
    generate_qr_codes(songs, qr_type=args.qr_type)

    logger.info("Compiling Cards PDF")
    sys_inputs = {}
    if args.edition:
        sys_inputs["edition"] = args.edition
    typst.compile("hitster-cards.typ", output=args.cards_pdf, sys_inputs=sys_inputs)

    logger.info("Compiling Year Distribution PDF")
    generate_year_distribution_pdf(songs, args.overview_pdf)

    logger.info("Done")


if __name__ == "__main__":
    main()
