from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello Cloud! This is New version:)'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

