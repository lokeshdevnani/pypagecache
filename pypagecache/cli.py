# cli.py

import argparse
from pypagecache import PyPageCache


def cli():
    parser = argparse.ArgumentParser(description='PyPageCache CLI - Manage your page cache')

    parser.add_argument('--stats', '-s', metavar='PATH',
                        help='View page cache statistics for the specified file or directory.')
    parser.add_argument('--touch', '-w', metavar='PATH',
                        help='Warm the page cache by touching all files in the specified directory.')
    parser.add_argument('--evict', '-e', metavar='PATH',
                        help='Evict file pages from the page cache for the specified directory.')

    args = parser.parse_args()

    if args.stats:
        cache_stats = PyPageCache(args.s).stats()
        print(cache_stats)
    elif args.touch:
        PyPageCache(args.w).touch()
        print(f'Cache warmed for files in {args.w}')
    elif args.evict:
        PyPageCache(args.e).evict()
        print(f'Cache evicted for files in {args.e}')
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
