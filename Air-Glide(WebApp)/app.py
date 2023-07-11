from flask import Flask,render_template,Response,redirect,url_for,flash
import cv2
import os
import numpy as np
import face_recognition
import time
import pyautogui
import HANDDETECTION as hdt
from flask_mysqldb import MySQL

app = Flask(__name__)
cap=cv2.VideoCapture(0)
app.secret_key='dont tell'

def camera():
    success,frame=cap.read()
    return frame
        
def generate_frames():
    while True:
        frame=camera()
        ret,buffer=cv2.imencode('.jpg',frame)
        frame=buffer.tobytes()
        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
def generate_frame_login():
    global face_reco
    #Taking the images from the given path and passing in myList
    path='Images'
    images=[]
    ClassNames=[]
    myList=os.listdir(path)
    print(myList)

    # passing images in image list and spliting names and appending them in ClassName
    for cl in myList:
        frame=cv2.imread(f'{path}/{cl}')
        images.append(frame)
        ClassNames.append(os.path.splitext(cl)[0])
    print(ClassNames)

    #Function to append encodings of the images
    def findEncodings(images):
        encodeList=[]
        for img in images:
            img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            encode=face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    encodeListKnown=findEncodings(images)
    while True:
        frame=camera()
        #imgS=cv2.resize(img,(0,0),None,0.25,0.25)
        imgS=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        #Finding Locations of frame and encoding each frame
        faceCurFrame= face_recognition.face_locations(imgS)
        encodeCurFrame=face_recognition.face_encodings(imgS,faceCurFrame)

        #Matching the encodings and getting min distance to get best match
        for encodeFace,faceLoc in zip(encodeCurFrame,faceCurFrame):
            matches=face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis=face_recognition.face_distance(encodeListKnown,encodeFace)
            #print(faceDis)
            matchIndex=np.argmin(faceDis)


            #Matching with DataBase
            if matches[matchIndex]:
                name=ClassNames[matchIndex].upper()
                #color= 'green'
                y1, x2, y2, x1 = faceLoc
                cv2.rectangle(imgS, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(imgS, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(imgS, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1)
                print(name)
                time.sleep(3)
                pyautogui.hotkey('alt','l')
                return 
                    

            else:
                #color= 'red'
                y1, x2, y2, x1 = faceLoc
                cv2.rectangle(imgS, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.rectangle(imgS, (x1, y2-35), (x2, y2), (255, 0, 0), cv2.FILLED)
                print("NAHI HAI")
                pyautogui.hotkey('alt','w')
                return 
                


        #Showing The original Image again.
        imgS = cv2.cvtColor(imgS, cv2.COLOR_RGB2BGR)
        ret,buffer=cv2.imencode('.jpg',imgS)
        frame=buffer.tobytes()
        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def generate_frames_virtual_mouse():
    hweb = 480
    wweb = 640
    cap.set(3,wweb)
    cap.set(4,hweb)
    pTime = 0
    wscr , hscr = pyautogui.size()
    tym = 0
    pixels = 100
    
    detector = hdt.HandDetector()
    while True:
        frame=camera()
        frame = cv2.flip(frame,1)
        frame = detector.findHands(frame)
        lmlist = detector.findPosition(frame)

        #tip of all the fingers

        if len(lmlist) != 0:
            x0,y0 = lmlist[4][1:]
            x1, y1 = lmlist[8][1:]
            x2, y2 = lmlist[12][1:]
            x3, y3 = lmlist[16][1:]
            x4, y4 = lmlist[20][1:]

            fingers = detector.fingersup()


            cv2.rectangle(frame,(pixels,pixels),(wweb - pixels, hweb - pixels),(255,255,0),2)


            #only index finger moving mode:
            if fingers == [0,1,0,0,0]:
                xc = np.interp(x1,(pixels,wweb - pixels),(0,wscr))
                yc = np.interp(y1, (pixels, hweb - pixels), (0, hscr))

                pyautogui.moveTo(xc,yc)
                cv2.circle(frame,(x1,y1),15,(140,140,0),cv2.FILLED)

            #for clicking: middle and index fing
            if fingers == [0,1,1,0,0]:

                lenght, frame  = detector.distance(8,12,frame)
                if lenght <40:
                    tym+=1
                    if tym>30:
                        cv2.circle(frame,(x1,y1),15,(0,255,0),cv2.FILLED)
                        pyautogui.click()
                        tym = 0

            #thumb up for win r
            if fingers == [1,0,0,0,0]:
                tym+=1
                if tym > 40:
                    cv2.circle(frame, (x0, y0), 15, (0, 255, 0), cv2.FILLED)
                    pyautogui.hotkey("win","r")
                    tym = 0


            #for closing opencv
            if fingers == [0,0,0,0,1]:
                tym+=1
                if tym > 40:
                    cv2.circle(frame, (x4, y4), 15, (0, 255, 0), cv2.FILLED)
                    pyautogui.hotkey("q")
                    tym = 0

        #frame rate
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 0), 3)
        ret,buffer=cv2.imencode('.jpg',frame)
        frame=buffer.tobytes()
        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    


@app.route('/')
def home():
    return render_template("home.html")

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/login_message')
def login_message():
    return render_template("login_message.html")

@app.route('/main')
def main():
    return render_template("main.html")

@app.route('/video_signup')
def video_signup():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_login')
def video_login():
    return Response(generate_frame_login(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_virtual_mouse')
def video_virtual_mouse():
    return Response(generate_frames_virtual_mouse(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture')
def capture():
    while True:
        frame=camera()
        path='E:\Air-Glide(WebApp) not gitHub\Images'
        cv2.imwrite(os.path.join(path,"Anirudh.png"), frame)
        break
    return redirect(url_for("login"))
    
    
    
if __name__=="__main__":
    app.run(debug=True)