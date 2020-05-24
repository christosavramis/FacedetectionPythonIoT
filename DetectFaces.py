#import packages
import cv2
import argparse
import sys
import os.path
from os import path
from tinydb import TinyDB, Query
import imutils
import asyncio
import base64

#Save to database is asynchronous so the program won't wait for the db to insert the value
async def saveToDB(x,y,w,h,timestamp,source,db):
    db.insert({'x': int(x), 'y': int(y), 'w':int(w), 'h':int(h), "volume":int(w * h), 'timestamp':timestamp ,"source":source})

#Create command line arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True,
    help="path to video")
ap.add_argument("-j", "--json", required=True,
    help="path to json file")
ap.add_argument('-p', '--print', action='store_true', 
    help="Print database values on exit")
ap.add_argument('-b', '--bilateralFiltering', action='store_true', 
    help="Removes noise while preserving edges")
ap.add_argument('-m', '--medianFiltering', action='store_true', 
    help="Removes salt-and-pepper noise")
ap.add_argument('-g', '--guassianFiltering', action='store_true', 
    help="Removes salt-and-pepper noise")          
args = vars(ap.parse_args())

if path.exists(args['json']) == False:
    print("json file not found so one will be created")
    f = open(args['json'], "w")
    f.close()
    #sys.exit(0)

if path.exists(args['video']) == False:
    print("video file not found")
    sys.exit(0)

#Warn the user about which filter is used
if args['bilateralFiltering']:
    print("Filter: Bilateral Filtering")
elif args['medianFiltering']:
    print("Filter: Median Filtering")
elif args['gaussianFiltering']:
    print("Filter: Gaussian Filtering")
else:
    print("Filter: Default")




#Load the classifier
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

#Connect with the database
db = TinyDB(args['json'])

#Clear the database
db.truncate()

#Load the video
cap = cv2.VideoCapture(args['video'])

#For each frame apply classification
while True:
    _,frame = cap.read()

    #quit if they are no frames
    if frame is None:
        break
    
    # resize the frame
    frame = imutils.resize(frame, width=800)

    #Apply filters if specified
    if args['bilateralFiltering']:
        frame = cv2.bilateralFilter(frame,9,75,75)
    elif args['medianFiltering']:
        frame = cv2.medianBlur(frame,5)
    elif args['gaussianFiltering']:
        frame = cv2.GaussianBlur(frame,(5,5),0)


    #Convert the frame to grayscale to increase performance
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #Use the classifier in the current frame
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    #for each face draw a square and save them to db
    for (x,y,w,h) in faces:
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0),2)
        cv2.putText(frame, "Person", (x, y-20),
		cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(saveToDB(x,y,w,h,timestamp,args['video'],db))

    #Display the frame
    cv2.imshow("frame", frame)

    #Detect Escape 
    key = cv2.waitKey(1)
    if key == 27:
        break

#if script was called with -p print the data
if args['print']:
    for data in db.all():
        print(data)

#Closing stuf
cv2.destroyAllWindows()

#Release the video source
cap.release()

#Close the connection with the db
db.close()

