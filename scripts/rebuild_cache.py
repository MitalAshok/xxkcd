import sys
import os
import multiprocessing
import argparse

import xxkcd


def get_raw_json(n):
    return dict(xxkcd.xkcd(n)._raw_json)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    current_directory = os.path.dirname(os.path.realpath(__file__))
    default_output_file = os.path.join(current_directory, os.pardir, 'xxkcd', '_cache.py')

    parser = argparse.ArgumentParser(prog='rebuild_cache', description='Regenerates xxkcd._cache')
    parser.add_argument('file', nargs='?', default=default_output_file, help='Where to write the file to')
    parser.add_argument('-p', '--procs', default=4, type=int, help='If positive, how many processes to use. Else single threaded.')

    args = parser.parse_args(argv)

    range = xxkcd.xkcd.range()
    if args.procs > 0:
        pool = multiprocessing.Pool(args.procs)
        raw_json_list = pool.map(get_raw_json, map(xxkcd.xkcd, range))
        pool.close()
        pool.join()
    else:
        raw_json_list = map(get_raw_json, range)

    raw_json_dict = dict(zip(range, raw_json_list))

    with open(args.file, 'w') as f:
        f.write('cache = ')
        f.write(repr(raw_json_dict))
    return 0


if __name__ == '__main__':
    main()
