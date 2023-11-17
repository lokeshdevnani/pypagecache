# cli.py

import argparse
from pypagecache import PyPageCache


def cli():
    parser = argparse.ArgumentParser(description='PyPageCache CLI - Manage your page cache')

    parser.add_argument('-s', '--stats', metavar='PATH',
                        help='View page cache statistics for the specified file or directory.')
    parser.add_argument('-t', '--touch', metavar='PATH',
                        help='Warm the page cache by touching all files in the specified directory.')
    parser.add_argument('-e', '--evict', metavar='PATH',
                        help='Evict file pages from the page cache for the specified directory.')

    args = parser.parse_args()

    if args.stats:
        cache_stats = PyPageCache(args.stats).stats()
        print(cache_stats)
    elif args.touch:
        PyPageCache(args.touch).touch()
        print(f'Cache warmed for files in {args.touch}')
    elif args.evict:
        PyPageCache(args.evict).evict()
        print(f'Cache evicted for files in {args.evict}')
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
