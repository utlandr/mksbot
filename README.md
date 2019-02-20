# MksBot - Observing gamers in their natural habitat

MksBot is my Python implementation of a Discord bot. Currently, he works on a single server to entertain my friends and I. I aim to implement more helpful features in the future.

I have no plans to enable other discord channels to access this bot. The poor fella only runs on a raspberry pi and there are plenty of other bots out there that can do specific tasks better (but he doesn't know that). That said, feel free to use the source code/bot cogs however you like, or raise an issue/contact me for more information.
## Features

MksBot has the following features:

- Youtube and local audio streaming (with basic playback and queueing capabilities)
- Reddit web scraping using the PRAW module with multiple formats supported (gifs/images, links and reddit hosted media).
- Randomised replies to users
- Profile information scraping

## Dependencies

MksBot requires the following:

- [discord.py](https://github.com/Rapptz/discord.py/tree/rewrite) v1.0.0 (with voice extension)
- PRAW reddit module (reddit scraper)
- youtube-dl (youtube audio streaming)
- ffmpeg (for audio file conversion and streaming)

These packages themselves may require further dependencies depending on what system you are using. MksBot has been tested on Windows and Linux (specifically Ubuntu 18.04 LTS).

Please note that I use the rewritten (1.0.0) version of [discord.py](https://github.com/Rapptz/discord.py/tree/rewrite). The rewrite is **not** compatible with older versions of the library.

## Installation


If you really want to install a copy of MksBot. You will need a YAML configuration file containing the important credentials and settings required to run the source as it provided. I plan to improve how configuration works on the bot, but for now, a template `config-template.yml` has been provided for you to fill in. Be sure to rename `config-template.yml` to `config.yml` when running an instance of the bot.

## Improvements

I plan to add the following:

- Playlist/youtube radio support
- Improved configuration
- Sensible thread/process handling