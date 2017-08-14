#!/usr/bin/env python

from xxkcd import xkcd
import sys


def main():
    if sys.version_info >= (3,):
        for n in xkcd.range():
            print(xkcd(n).title)
    else:
        for n in xkcd.range():
            print(xkcd(n).title.encode('utf-8'))


if __name__ == '__main__':
    main()
