from flask import Flask,render_template

app = Flask(__name__)

@app.route('/')
def home():
    return "This is home page."

@app.route('/signup')
def signup():
    pass

@app.route('/signin')
def signin():
    pass

@app.route('/main')
def main():
    pass

if __name__=="__main__":
    app.run(debug=True)