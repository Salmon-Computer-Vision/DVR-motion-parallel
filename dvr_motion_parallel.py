#!/usr/bin/env python3
import argparse


def run_all(args):
    return


def run_split(args):
    return


def run_parallel_scan(args):
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Split and parallelize the clipping of motion detection preprocessing on videos.')

    subp = parser.add_subparsers(help='Different processing')

    all_parser = subp.add_parser('all', help='Run all processing and output motion clips. Will require at most 3 times as much disk space.')
    all_parser.set_defaults(func=run_all)
    all_parser.add_argument('src_video', help='Source video to preprocess.')

    split_parser = subp.add_parser('split', help='Only split the video into equally sized clips.')
    split_parser.set_defaults(func=run_split)
    split_parser.add_argument('src_video', help='Source video to preprocess.')
    split_parser.add_argument('-n', '--number', default=8, help='Number of splits of the video desired.')
    split_parser.add_argument('-o', '--output', default='split_clips', help='Output folder of the split video clips.')

    scan_parser = subp.add_parser('scan', help='Scans and creates motion detected clips in parallel of all videos in a folder')
    scan_parser.set_defaults(func=run_parallel_scan)
    scan_parser.add_argument('src_video', help='Source video to preprocess.')
    scan_parser.add_argument('-j', '--jobs', default=8, help='Number of parallel jobs at once. Ideally no more than double your CPU cores.')
    scan_parser.add_argument('-o', '--output', default='motion_detected_clips', help='Output folder of the motion detected video clips.')

    args = parser.parse_args()
    args.func(args)
