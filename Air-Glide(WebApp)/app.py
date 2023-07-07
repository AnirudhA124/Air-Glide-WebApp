from flask import Flask,render_template,Response,redirect,url_for
import cv2
import os

app = Flask(__name__)
cap=cv2.VideoCapture(0)

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


@app.route('/')
def home():
    return render_template("main.html")

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/main')
def main():
    pass

@app.route('/video')
def video():
    pass
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture')
def capture():
    while True:
        frame=camera()
        path='E:\Air-Glide(WebApp) not gitHub\Images'
        cv2.imwrite(os.path.join(path,"Anirudh.png"), frame)
        break
    return redirect(url_for('home'))
    
    
    
    

if __name__=="__main__":
    app.run(debug=True)