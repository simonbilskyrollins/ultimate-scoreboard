# ultimate-scoreboard

This is a little script I hacked together while following the D-I ultimate college championship tournament. I noticed that there wasn't a good centralized source for live scores, but basically every team tweets live updates from the sidelines. So, using the Twitter API, I wrote this Python script that looks at the latest tweets from two teams' Twitter accounts and tells you the score of the game between them.

## Install

Installation is pretty simple. First you will need to set up your own Twitter app and store your credentials in `twitter.cfg`. Then install required packages with

    pip install -r requirements.txt

## Usage

    python tweet_parser.py Carleton Wisconsin
    Carleton 15 - 13 Wisconsin

Or, if you don't know who your favorite team is playing at the moment:

    python tweet_parser.py Carleton
    Carleton 15 - 13 Faceless Opponent

## Future work

This project is obviously pretty rough around the edges right now. Next up on the to-do list are:
* Handling failures (i.e. when there isn't a game going on) more elegantly
* Getting and displaying a list of all ongoing games
* Creating some sort of web interface
