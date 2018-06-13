from flask import Flask,render_template

application = Flask(__name__)

@application.route("/")

def index():
	return render_template('child.txt',text='Child')

if __name__ == "__main__":
    application.run(host = '0.0.0.0',port = '8888')
