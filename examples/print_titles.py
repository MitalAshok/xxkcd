#!/usr/bin/env python

from xxkcd import xkcd


def main():
    for n in xkcd.range():
        print(xkcd(n).title)


if __name__ == '__main__':
    main()
