#!/usr/bin/env python

from xxkcd import xkcd
import sys


def main():
    xkcd.load_all(True)

    for n in range(1, xkcd.latest() + 1):
        if sys.version_info >= (3,):
            print(xkcd(n).title)
        else:
            print(xkcd(n).title.encode('utf-8'))


if __name__ == '__main__':
    main()
