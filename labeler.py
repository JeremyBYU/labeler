import argparse
import csv
import uuid
import cv2
import numpy as np


FRAME = 0
NAME = "propellor"
ANNOTATION = []
IM_FRAME = None

width = 100
height = 100
 
 # mouse callback function
def draw_circle(event,x,y,flags,param):
    global ANNOTATION
    if event == cv2.EVENT_LBUTTONDBLCLK:
        ANNOTATION.append(dict(name=NAME, x=x,y=y,frame=FRAME))
        draw_frame()
        cv2.imshow('Frame',IM_FRAME)
        print("Recording {}".format((x,y)))
    elif event == cv2.EVENT_RBUTTONDOWN:
        ANNOTATION.append(dict(name=NAME, x=np.nan,y=np.nan,frame=FRAME))
        draw_frame()
        cv2.imshow('Frame',IM_FRAME)
        print("Droping Frame {}".format((x,y)))
 

def draw_frame():
    if ANNOTATION:
        data = ANNOTATION[-1]
        x = data['x']
        y = data['y']
        if np.isnan(x):
            return
        cv2.rectangle(IM_FRAME,(x - width,y + width),(x + width, y - width),(0,255,0), 2)

def label(video):
    global FRAME, IM_FRAME
    cap = cv2.VideoCapture(video)
    cv2.namedWindow('Frame')
    # Check if camera opened successfully
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")

    cv2.setMouseCallback('Frame',draw_circle)

    # Read until video is completed
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        IM_FRAME = frame
        if ret == True:
            # Display the resulting frame
            draw_frame()
            cv2.imshow('Frame',frame)

            # Press Q on keyboard to  exit
            res = cv2.waitKey(0)
            if res == ord('n'):
                FRAME += 1
                continue
            else:
                res == ord('q')
                break


def output_data():
    with open('{}_{}.csv'.format(NAME, uuid.uuid4()), 'w') as output_file:
        keys = ANNOTATION[0].keys()
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(ANNOTATION)

def main():
    global NAME

    parser = argparse.ArgumentParser(description='Labeler')
    parser.add_argument('--video', '-v', type=str, help='Video file', default='video.mp4')
    parser.add_argument('--name', '-n', type=str, help='Video file', default='propellor')

    args = parser.parse_args()

    NAME = args.name
    label(args.video)
    output_data()
    

if __name__ == "__main__":
    main()

