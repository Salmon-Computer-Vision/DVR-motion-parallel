#!/usr/bin/env python3
import argparse
import cv2
import subprocess
import os
import shutil
import traceback
import glob
import re

import multiprocessing as mp
from multiprocessing import Pool

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

fps_rg = re.compile(r'[0-9]+.[0-9]+ frames/s')

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


class Scan:
    base_cmd = 'dvr-scan'
    cmd = []

    def __init__(self, path, output_path, args):
        self.path = path
        self.output_path = output_path

        self.min_event_length = args.min_event_length
        self.thresh = args.thresh
        self.mog = args.mog
        self.time_post = args.time_post_event
        self.time_before = args.time_before_event
        self.time_code = args.time_code

    def build_cmd(self):
        self.cmd = [self.base_cmd]
        self.cmd += ['-i', self.path]
        self.cmd += ['-o', self.output_path]
        self.cmd += ['-l', str(self.min_event_length)]
        self.cmd += ['-t', str(self.thresh)]
        self.cmd += ['-tb', self.time_before]
        self.cmd += ['-tp', self.time_post]

        if not self.mog:
            self.cmd += ['-b', 'MOG2_CUDA']

        if self.time_code:
            self.cmd += ['-tc']

    def run(self):
        p = subprocess.Popen(self.cmd, 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True)
        out, err = p.communicate()
        return (out, err)

def scan_run_job(scan):
    print("Start:", scan.path)
    out, err = scan.run()
    print(out)
    try:
        print(fps_rg.findall(err)[-1]) # Print out the last fps
    except:
        print("Error trying to print out FPS")
    print("Finish:", scan.path)

def run_parallel_scan(args):
    job_pool = Pool(int(args.jobs))

    scan_instances = []
    for vid in glob.glob(os.path.join(args.src_folder, '**', '*.mp4'), recursive=True):
        input_dir = os.path.dirname(vid)
        output_dir = os.path.join(args.output, os.path.relpath(input_dir, args.src_folder))
        if os.listdir(output_dir):
            continue

        os.makedirs(output_dir, exist_ok=True)
        name = os.path.splitext(os.path.basename(vid))[0]
        output_path = os.path.join(output_dir, f"{name}.avi")

        scan = Scan(path=vid, output_path=output_path, args=args)
        scan.build_cmd()
        scan_instances.append(scan)

    job_pool.map(scan_run_job, scan_instances)

    job_pool.close()
    job_pool.join()

    return


def subcommands(parser):
    subp = parser.add_subparsers()

    all_parser = subp.add_parser('all', help='Run all processing and output motion clips. Will require at most 3 times as much disk space.')
    all_parser.set_defaults(func=run_all)
    all_parser.add_argument('src_video', help='Source video to preprocess.')
    all_parser.add_argument('-j', '--jobs', default=4, help='Number of parallel jobs at once. Ideally no more than your vCPU cores.')
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
    scan_parser.add_argument('-l', '--min_event_length', default=3, help='Min required number of frames to trigger. See more in `dvr-scan -h`. Default is 3.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Split and parallelize the clipping of motion detection preprocessing on a video.')

    parser.set_defaults(func=run_parallel_scan)

    parser.add_argument('src_folder', help='Source folder to recursively find videos on.')
    parser.add_argument('-j', '--jobs', default=mp.cpu_count(), help='Number of parallel jobs at once. Default is your number of CPU cores.')
    parser.add_argument('-o', '--output', default='motion_detected_clips', help='Output folder for the motion detected video clips. Will recreate the source folder hierarchy.')
    parser.add_argument('-t', '--thresh', default=0.3, help='Motion threshold value. See more in `dvr-scan -h`. Default is 0.3')
    parser.add_argument('-l', '--min-event-length', default=3, help='Min required number of frames to trigger. See more in `dvr-scan -h`. Default is 3.')
    parser.add_argument('-m', '--mog', action='store_true', help='Use slower MOG background subtraction. See more in `dvr-scan -h`.')
    parser.add_argument('-tp', '--time-post-event', default='3s', help='Num of frames to include after motion (Can use seconds, too). See more in `dvr-scan -h`. 3 sec')
    parser.add_argument('-tb', '--time-before-event', default='3s', help='Num of frames to include before motion (Can use seconds, too). See more in `dvr-scan -h`. Default 3 sec')
    parser.add_argument('-tc', '--time-code', action='store_true', help='Draw time code of each frame in top left corner. See more in `dvr-scan -h`.')

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        traceback.print_exc()
        parser.print_usage()
