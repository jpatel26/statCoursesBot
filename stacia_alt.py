#!/usr/bin/env python3

import queryparser.irc_stat_bot as bot
import queryparser.stacia_core as sc

if __name__ == '__main__':
    bot.bot_init(sc.ask, sc.greet)