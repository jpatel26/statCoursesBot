#!/usr/bin/env python3
import queryparser.stacia_core as sc

if __name__ == '__main__':
    print(sc.greet())
    while True:
        query = input()
        status, content = sc.ask(query)
        print("StaCIA:", content)
        if status == 'END':
            exit()
