# DVR Motion Parallel

Python >= 3.5

Parallel motion detection by simply running a motion detection tool
over multiple videos at the same time.

The script will by default parallelize up to your machine's CPU cores and
output separate compilation videos of all the motion detected
events per video recursively in the supplied folder.

## Install

### Windows

Download and install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/).

Miniconda is a more lite version without the extra GUI applications.

Hit the Windows key and search for "Anaconda Prompt" and open it. A terminal prompt will appear.

Enter the following to create a new environment:
```
conda create --name dvr-motion 
```

Enter the following to activate the environment (You must do this everytime you close the terminal):
```
conda activate dvr-motion
```

Install pip:
```
conda install pip
```

Install dvr-scan:
```
pip install dvr_scan[opencv]
```

### Other systems

For all systems. Simply install dvr-scan with pip:
```
pip install dvr_scan[opencv]
```

## Usage

Check the help for the options:

```
python dvr_motion_parallel.py --help
```

Run with all defaults:

```
python dvr_motion_parallel.py path/to/videos/folder
```

You may want to specify a different output folder:

```
python dvr_motion_parallel.py path/to/videos/folder -o path/to/output/folder
```

Change the configs inside the `dvr-scan.cfg` file.

# DVR-Scan Normal Usage

You can check all the options with `dvr-scan -h`, but the following should be
mainly the command that would be used:

```
dvr-scan -l 10 -i <path/to/video>
```

Also, try the following as supposedly this background subtractor may be faster:
```
dvr-scan -l 10 -b CNT -i <path/to/video>
```

You can tweak the threshold a little to try to filter out non-desirable detections:
```
dvr-scan -l 10 -b CNT -t 0.25 -i <path/to/video>
```

0.15 is the default threshold. A higher threshold would require more movement before
a detection is triggered.

This will output several motion detected `.avi` clips in the current folder.

# Deprecated

## Choose split points

Best way is to **manually** choose 4 or more clip intervals in the long video
that allows each clip to be more or less equally sized without splitting
on a target object.

Create a `times.txt` file and put the split points
in this format:
```
HH:MM:SS[.nnn]
```
Look at `times_example.txt` for an example.
