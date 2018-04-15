## How to Use
 - You only need to use this .launch file if your data are saved in rosbags.

### Step. 01
 - Bag file name is assumed to be $HOMEDIR/dataset/bags/current-bag.bag
 - run `roslaunch extract-images.launch HOMEDIR:=/absolute/path/to/your/bag/file` in command line
 - Output images will be saved to $HOMEDIR/dataset/images/

### Step. 02
 - Please do rename dataset folder so that your images won't be replcaed by next run
 - Please make sure folder images exist, or images will not be saved