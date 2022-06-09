#!/usr/bin/env python3
import argparse
import cv2
import subprocess
import os
import shutil
import traceback
import glob
from multiprocessing import Pool

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


def run_all(args):
    args.number = args.jobs
    motion_output = args.output
    temp_folder = 'temp_split_vids'
    args.output = temp_folder
    run_split(args)

    args.src_folder = temp_folder
    args.output = motion_output
    run_parallel_scan(args)
    shutil.rmtree(temp_folder)
    return


def run_split(args):
    name = os.path.splitext(os.path.basename(args.src_video))[0]
    dest_path = os.path.join(args.output, name)

    os.makedirs(dest_path, exist_ok=True)
    video = cv2.VideoCapture(args.src_video)

    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = video.get(cv2.CAP_PROP_FPS)
    duration = frame_count / fps
    print('Dur:', duration, 'Frames:', frame_count, 'FPS:', fps)
    interval = duration / args.number

    dest_filename = os.path.join(dest_path, name)
    for i in range(args.number):
        ffmpeg_extract_subclip(args.src_video, interval * i, interval * (i+1), 
                targetname=dest_filename + f"_{str(i)}" + '.mp4')
    return


class ScanParams:
    path = ''
    start = '00:00:00'
    end = '00:00:00'

    def __init__(self, path, start, end):
        self.path = path
        self.start = start
        self.end = end


def run_parallel_scan(args):
    def run_dvr_scan(params):
        subprocess.run(['dvr-scan', '-l', 10, '-st', params.start, '-et', params.end,
            '-t', args.threshold, params.path])

    os.makedirs(args.output)

    job_pool = Pool(args.jobs)

    all_params = []
    for vid in glob.glob(f"{args.src_folder}/*"):
        all_params.append(ScanParams(path=vid, 

    job_pool.map(run_dvr_scan, all_params))

    job_pool.close()
    job_pool.join()

    for vid in glob.glob('*.avi'):
        print(vid)
        shutil.copy(vid, args.output)

    return


def subcommands(parser):
    subp = parser.add_subparsers()

    all_parser = subp.add_parser('all', help='Run all processing and output motion clips. Will require at most 3 times as much disk space.')
    all_parser.set_defaults(func=run_all)
    all_parser.add_argument('src_video', help='Source video to preprocess.')
    all_parser.add_argument('-j', '--jobs', default=8, help='Number of parallel jobs at once. Ideally no more than double your CPU cores.')
    all_parser.add_argument('-o', '--output', default='motion_detected_clips', help='Output folder of the motion detected video clips.')

    split_parser = subp.add_parser('split', help='Only split the video into equally sized clips. Don\'t split too much otherwise the desired detected object may also be split.')
    split_parser.set_defaults(func=run_split)
    split_parser.add_argument('src_video', help='Source video to preprocess.')
    split_parser.add_argument('-n', '--number', default=4, help='Number of splits of the video desired.')
    split_parser.add_argument('-o', '--output', default='split_clips', help='Output folder of the split video clips.')

    scan_parser = subp.add_parser('scan', help='Scans and creates motion detected clips in parallel of all videos in a folder.')
    scan_parser.set_defaults(func=run_parallel_scan)
    scan_parser.add_argument('src_folder', help='Source folder of video clips to preprocess.')
    scan_parser.add_argument('-j', '--jobs', default=4, help='Number of parallel jobs at once. Ideally no more than double your CPU cores.')
    scan_parser.add_argument('-o', '--output', default='motion_detected_clips', help='Output folder of the motion detected video clips.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Split and parallelize the clipping of motion detection preprocessing on a video.')

    parser.set_defaults(func=run_parallel_scan)

    parser.add_argument('src_video', help='Source video to run motion detection on.')
    parser.add_argument('-j', '--jobs', default=4, help='Number of parallel jobs at once. Ideally no more than double your CPU cores.')
    parser.add_argument('-o', '--output', default='motion_detected_clips', help='Output folder of the motion detected video clips.')
    parser.add_argument('-t', '--threshold', default=0.15, help='Motion threshold value. See more in `dvr-scan -h`')
    parser.add_argument('-j', '--jobs', default=4, help='Number of parallel jobs at once. Ideally no more than double your CPU cores.')

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        traceback.print_exc()
        parser.print_usage()
