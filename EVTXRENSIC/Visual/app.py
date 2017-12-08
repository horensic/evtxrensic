"""
This file is part of the flask+d3 Hello World project.
"""
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    
    return render_template("index.html")

if __name__ == "__main__":
    
    # Set up the development server on port 8000.
    app.run(host="127.0.0.1", port=5000, threaded=True)
