import argparse
import csv
import uuid
import cv2
import numpy as np
import pprint
import pandas as pd

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
 

def draw_frame(my_annotation=None):
    if my_annotation:
        data = my_annotation
        x = data['x']
        y = data['y']
        if np.isnan(x):
            return
        cv2.rectangle(IM_FRAME,(x - width,y + width),(x + width, y - width),(0,255,0), 2)
    elif ANNOTATION:
        data = ANNOTATION[-1]
        x = data['x']
        y = data['y']
        if np.isnan(x):
            return
        cv2.rectangle(IM_FRAME,(x - width,y + width),(x + width, y - width),(0,255,0), 2)


def interpolate(frames):
    prev_frame_number = frames[0]['frame']
    prev_frame_x = frames[0]['x']
    prev_frame_y = frames[0]['y']

    # if np.isnan(prev_frame_x)



    all_frames = []
    for index, frame in enumerate(frames[1:]):
        frame_number = frame['frame']
        dt = frame_number - prev_frame_number
        if np.isnan(frame['x'] or (index == 0 and np.isnan(prev_frame_x))):
            new_xs = [prev_frame_x] * dt
            new_ys = [prev_frame_y] * dt
        else:
            new_xs = np.linspace(prev_frame_x, frame['x'], dt)
            new_ys = np.linspace(prev_frame_y, frame['y'], dt)

        for xs, ys, new_frame in zip(new_xs, new_ys, range(prev_frame_number, prev_frame_number + dt)):
            if np.isnan(xs):
                all_frames.append(dict(x=xs,y=ys,frame=new_frame))
            else:
                all_frames.append(dict(x=int(xs),y=int(ys),frame=new_frame))


        prev_frame_number = frame_number
        prev_frame_x = frame['x']
        prev_frame_y = frame['y']

    return all_frames

def label(video, data=None):
    global FRAME, IM_FRAME
    cap = cv2.VideoCapture(video)
    cv2.namedWindow('Frame')
    # Check if camera opened successfully
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")

    cv2.setMouseCallback('Frame',draw_circle)

    if data:
        out = cv2.VideoWriter('output.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 30, (960,540))

    # Read until video is completed
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        IM_FRAME = frame
        if ret == True:
            # Display the resulting frame
            if data:
                draw_frame(data[FRAME])
            else:
                draw_frame()

            cv2.imshow('Frame',frame)
            out.write(frame)
            # Press Q on keyboard to  exit
            if data is not None:
                FRAME += 1
                continue
            res = cv2.waitKey(0)
            if res == ord('n'):
                FRAME += 1
                continue
            elif res == ord('q'):
                break
        else:
            break
    out.release()


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
    parser.add_argument('--annotate', '-a', type=str, help='Video file', default='top_left_a384f311-2c1d-4884-b8c5-0f0a536b5fb3.csv')

    args = parser.parse_args()

    NAME = args.name
    data = None
    if args.annotate:
        df = pd.read_csv(args.annotate)
        data_df = df.to_dict('records')
        data = interpolate(data_df)


    label(args.video,data )
    if data is None:
        output_data()
    

if __name__ == "__main__":
    main()

