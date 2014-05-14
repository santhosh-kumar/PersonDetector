#!/usr/bin/python
import numpy as np
import cv2
import cv2.cv as cv

import ConfigParser
import io
import os
import logging

# default name for the config file
CONFIG_FILE_NAME                = "config.cfg"
DEFAULT_HUMAN_DETECTOR_MODEL    = 'DefaultPeopleDetector'
HUMAN_DETECTOR_MODEL_48x96      = 'PeopleDetector48x96'
HUMAN_DETECTTOR_MODEL_64x128    = 'PeopleDetector64x128'

class HumanDetector:
    """Hog based human detector class"""
    def __init__(self, videoFilePath, videoFileName, cameraId, humanDetectorModel, outputDirectoryPath, shouldDisplayResults, shouldSaveResults):
        self.videoFilePath          = videoFilePath
        self.videoFileName          = videoFileName
        self.cameraId               = cameraId
        self.outputDirectoryPath    = outputDirectoryPath
        self.shouldDisplayResults   = shouldDisplayResults
        self.shouldSaveResults      = shouldSaveResults
        self.hog                    = cv2.HOGDescriptor()
        
        # set the capture file
        self.capture                = cv2.VideoCapture(os.path.join(videoFilePath, videoFileName))
        
        if shouldSaveResults:
            self.outputFile         = open( os.path.join(outputDirectoryPath, videoFileName) + '.gt', 'w', 0 )
        else:
            self.outputFile         = []
            
        if self.shouldDisplayResults:
            cv2.namedWindow('Results')
        
        # set the svm model
        if humanDetectorModel == HUMAN_DETECTOR_MODEL_48x96:
            self.hog.setSVMDetector( cv2.HOGDescriptor_getPeopleDetector48x96() )
        elif humanDetectorModel == HUMAN_DETECTTOR_MODEL_64x128:
            self.hog.setSVMDetector( cv2.HOGDescriptor_getPeopleDetector64x128() )
        else:
            self.hog.setSVMDetector( cv2.HOGDescriptor_getDefaultPeopleDetector() )

            
    def __del__(self):
    	if self.capture is not None:
    		self.capture.release
         
		if shouldSaveResults:
			if self.outputFile is not None:
				self.outputFile.close()
         
    @staticmethod
    def inside(r, q):
        rx, ry, rw, rh = r
        qx, qy, qw, qh = q
        return rx > qx and ry > qy and rx + rw < qx + qw and ry + rh < qy + qh

    @staticmethod
    def draw_detections(img, rects, thickness = 1):
        for x, y, w, h in rects:
            # the HOG detector returns slightly larger rectangles than the real objects.
            # so we slightly shrink the rectangles to get a nicer output.
            pad_w, pad_h = int(0.15*w), int(0.05*h)
            cv2.rectangle(img, (x+pad_w, y+pad_h), (x+w-pad_w, y+h-pad_h), (0, 255, 0), thickness)
    
    def process(self, startFrameIndex, numberFrames):
        assert( self.capture.isOpened() )
        logging.info( 'Processing video' )
        
        # calculate the endframe index
        if numberFrames < 0:
            endFrameIndex = self.capture.get( cv.CV_CAP_PROP_FRAME_COUNT ) + startFrameIndex
        else:
            endFrameIndex = startFrameIndex + numberFrames
        
        # Process one frame after another
        for frameIndex in range( startFrameIndex, int(endFrameIndex)):
            success, origFrameImg = self.capture.read()
            if success:
                # perform multiscale hog detection
                found, w = self.hog.detectMultiScale(origFrameImg, winStride=(8,8), padding=(32,32), scale=1.05)
                found_filtered = []
                for ri, r in enumerate(found):
                    for qi, q in enumerate(found):
                        if ri != qi and HumanDetector.inside(r, q):
                            break
                    else:
                        found_filtered.append(r)
                        if shouldSaveResults:
                            outputLine = str(frameIndex) + ' ' + ' '.join(map(str, r)) + '\n'
                            self.outputFile.write(outputLine)
                HumanDetector.draw_detections(origFrameImg, found)
                HumanDetector.draw_detections(origFrameImg, found_filtered, 3)
                if self.shouldDisplayResults:
                    cv2.imshow('Results', origFrameImg)
            else:
                break

            key = cv2.waitKey(20)
            if key in [27, ord('Q'), ord('q')]: # exit on ESC
                break

        
if __name__ == "__main__":
    # read the configuration file
    with open (CONFIG_FILE_NAME, "r") as configFile:
        configData = configFile.read()
        
    # print the config data
    print configData
    
    # parse the config
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(configData))
    
    # set the variables from config
    videoDirectoryPath  = config.get("input_output_settings", "Input_Video_Directory")
    cameraIdList        = config.get("input_output_settings", "Input_Camera_ID_List").split(",")
    videoList           = config.get("input_output_settings", "Input_Video_Name_List").split(",")
    startFrameIndex     = int( config.get("input_output_settings", "Start_Frame_Index") )
    numberFrames        = int( config.get("input_output_settings", "Number_Of_Frames") )
    outputDirectoryPath = config.get("input_output_settings", "OutPut_Video_Directory")
    logFileName         = config.get("input_output_settings", "Log_File_Name")
    shouldDisplayResults= int( config.get("input_output_settings", "Display_Intermediate_Result") )
    shouldSaveResults   = int( config.get("input_output_settings", "Save_Intermediate_Result") )
    humanDetectorModel  = config.get("model_settings", "human_detector_model") 
    
    print humanDetectorModel
    
    # configure log file
    logging.basicConfig(filename=logFileName,level=logging.DEBUG)
    
    assert( len(cameraIdList) == len(videoList) )
    
    # create a list of human detector
    humanDetectorList = []
    
    print len(cameraIdList)
    
    for i in range(0,len(cameraIdList)):
        humanDetector = HumanDetector(videoDirectoryPath, videoList[i], cameraIdList[i], humanDetectorModel, outputDirectoryPath, shouldDisplayResults, shouldSaveResults)
        humanDetectorList.append(humanDetector)
        humanDetector.process(startFrameIndex, numberFrames)
        
    logging.info( '############### done ##################' )
