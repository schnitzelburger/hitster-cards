# This is a sample Python script.
import json

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import typst

songs = [
    {
        "name": "Das Geht Ab (Wir Feiern Die Ganze Nacht) - Real Booty Babes Edit",
        "url": "https://open.spotify.com/track/3YdyHxOzSMglzwI9qMpuc0",
        "year": 2009,
        "artists": [
            "Frauenarzt",
            "Manny Marc"
        ]
    },
    {
        "name": "Play Hard (feat. Ne-Yo & Akon)",
        "url": "https://open.spotify.com/track/5YPMEOJ58kfl56VHxTgwx3",
        "year": 2012,
        "artists": [
            "David Guetta",
            "Ne-Yo",
            "Akon"
        ]
    },
    {
        "name": "Disco Pogo - Atzen Musik Mix",
        "url": "https://open.spotify.com/track/66sA9JeAeRuN1ZMtvthPQM",
        "year": 2010,
        "artists": [
            "Die Atzen"
        ]
    },
    {
        "name": "Sweat - Snoop Dogg vs David Guetta Remix",
        "url": "https://open.spotify.com/track/0R7YVi7w41Dr9jU5vblAok",
        "year": 2011,
        "artists": [
            "Snoop Dogg",
            "David Guetta"
        ]
    },
    {
        "name": "Sexy And I Know It",
        "url": "https://open.spotify.com/track/70Vdd1gx5tn84jkAU31ASv",
        "year": 2011,
        "artists": [
            "LMFAO"
        ]
    },
    {
        "name": "Call Me Maybe",
        "url": "https://open.spotify.com/track/20I6sIOMTCkB6w7ryavxtO",
        "year": 2012,
        "artists": [
            "Carly Rae Jepsen"
        ]
    },
    {
        "name": "I Gotta Feeling",
        "url": "https://open.spotify.com/track/70cTMpcgWMcR18t9MRJFjB",
        "year": 2009,
        "artists": [
            "Black Eyed Peas"
        ]
    },
    {
        "name": "Would I Lie to You - Radio Edit",
        "url": "https://open.spotify.com/track/4PdJSsESm34djLfBde9Pr2",
        "year": 2016,
        "artists": [
            "David Guetta",
            "Cedric Gervais",
            "Chris Willis"
        ]
    },
    {
        "name": "Don't Be So Shy - Filatov & Karas Remix",
        "url": "https://open.spotify.com/track/5Sod5qQTp8Nj4n5dTjttQG",
        "year": 2015,
        "artists": [
            "Imany",
            "Filatov & Karas"
        ]
    },
    {
        "name": "Sorry",
        "url": "https://open.spotify.com/track/09CtPGIpYB4BrO8qb1RGsF",
        "year": 2015,
        "artists": [
            "Justin Bieber"
        ]
    },
    {
        "name": "Danza Kuduro",
        "url": "https://open.spotify.com/track/2a1o6ZejUi8U3wzzOtCOYw",
        "year": 2010,
        "artists": [
            "Don Omar",
            "Lucenzo"
        ]
    }
]


def main():

    data = json.dumps(songs)
    sys_inputs: dict[str, str] = {"data": data}

    typst.compile("hello.typ", output="hello.pdf", sys_inputs=sys_inputs)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
