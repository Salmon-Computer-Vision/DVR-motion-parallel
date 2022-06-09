# DVR scan without parallel

First before attempting the parallel version, try `dvr-scan` not in parallel.

## Install
On windows download and install Anaconda, whereas other systems can just use
python3 `pip`.

On Windows, hit the Window key and search for "Anaconda Prompt" and open that
terminal.

Run the following to create a new environment:
```
conda create --name dvr-motion 
```

Run the following to activate the environment (You must do this everytime you close the terminal):
```
conda activate dvr-motion
```

Install pip:
```
conda install pip
```

For all systems. Simply install dvr-scan with pip:
```
pip install dvr_scan[opencv]
```

## Usage

You can check all the options with `dvr-scan -h`, but the following should be
mainly the command that would be used:

```
dvr-scan -l 10 -i <path/to/video>
```

You can tweak the threshold a little to try to filter out non-desirable detections:
```
dvr-scan -l 10 -t 0.25 -i <path/to/video>
```

0.15 is the default threshold. A higher threshold would require more movement before
a detection is triggered.

# DVR Motion Parallel

Pseudo parallel motion detection by simply running a motion detection tool
over multiple videos at the same time.

# Choose split points

Best way is to **manually** choose 4 or more clip intervals in the long video
that allows each clip to be more or less equally sized without splitting
on a target object.

Create a `times.txt` file and put the split points
in this format:
```
HH:MM:SS[.nnn]
```
Look at `times_example.txt` for an example.
