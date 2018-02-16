PersonDetector
==============

OpenCv based person detector written using Python. This is a convenient script generating detections on a given video. 

### Config Params ###

config.cfg has all the configurations for running the detecttor.

### Output ###

Detections will be stored in the specified output folder ("OutPut_Video_Directory").

      * input_file_name.extension.txt stores the detection results in the following format:
      [ frameNumber, xCentroid, yCentroid, width, height, objectId, timestamp(seconds) ]


### Contact ###
[1] Santhoshkumar Sunderrajan( santhosh@ece.ucsb.edu)
Website: http://santhoshsunderrajan.com/

### Bibtex ###
If you use the code in any of your research works, please cite the following papers:
~~~
@INPROCEEDINGS{sunderrajan2013, 
author={Santhoshkumar, S. and Karthikeyan, S. and Manjunath, B.S.}, 
booktitle={Image Processing (ICIP), 2013 20th IEEE International Conference on}, 
title={Robust multiple object tracking by detection with interacting Markov chain Monte Carlo}, 
year={2013}, 
month={Sept}, 
pages={2953-2957}, 
doi={10.1109/ICIP.2013.6738608},}
