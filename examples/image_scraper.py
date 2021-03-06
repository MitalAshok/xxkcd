#!/usr/bin/env python

import os
import multiprocessing

from xxkcd import xkcd


def download_image(n):
    x = xkcd(n)
    if x.image_filename is None:
        return  # Comic has no image
    name = '{number}_{name}'.format(number=n, name=x.image_filename)
    with open(os.path.join('images', name), 'wb') as f:
        x.stream_image(f)


def main():
    if not os.path.exists('images'):
        os.mkdir('images')
    pool = multiprocessing.Pool(4)
    pool.map(download_image, xkcd.range())
    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
