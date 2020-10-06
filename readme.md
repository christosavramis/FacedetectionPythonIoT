DecectFaces

example usage python .\DetectFaces.py --video "people2.mp4" --json 'faces1.json' -b
![GitHub Logo](/images/Capture.png)
Arguments

    General:

    --video : which is the path of the video file

    --json : which is the path of the json file

    -p : will print the database data in the console

    Filters:

    -b: applies Bilateral Filtering,removes noise while preserving edges

    -m: applies Median Filtering,removes salt and pepper noise

    -g: applies Gaussian Filtering, removes gaussian noise

    Note: only one filter can be active at a time, if more than one filters are
    active this order will be used -b > -m > -g
