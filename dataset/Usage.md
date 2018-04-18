## How to Use
 - You only need to use these files if your data are saved in rosbags.

### Step. 01
 - the .py files are written in python2
 - please read the python files, you need to set the working directory yourself
 - run `python shrink-data.py` in command line, it will call extraction-assignment.py automatically
 - extract-images.py will callback extract-images.launch to recursively extract images from bag files in the working directory and its subfolders.

### Step. 02
 - check images folder to see if the work is done