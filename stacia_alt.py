#!/usr/bin/env python3

import core.irc_stat_bot as bot
import core.stacia_core as sc

if __name__ == '__main__':
    bot.bot_init(sc.ask, sc.greet)