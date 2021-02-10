#imports
"""
from flask import Flask
from flask import render_template
"""

import os
from flask import Flask, request, jsonify, render_template
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app

#make the app
app = Flask(__name__)

#Initialize the firestore db
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
posts_ref = db.collection('posts')


#routes
@app.route("/")
def mainPage():
    return render_template("index.html")

@app.route("/upload")
def uploadPage():
    return render_template("upload.html")

@app.route("/viewall")
def viewAllPage():
    return render_template("viewAll.html")

@app.route("/create")
def createPage():
    return render_template("create.html")

@app.route("/create/new", methods = ["POST"])
def createNew():
    try:
        #get the request data from the form
        aName = request.form.get("aname")
        title = request.form.get("title")
        date = request.form.get("date")
        post = request.form.get("post")
        #needs to be put into json form
        json_request_form = {
            "name": aName,
            "title": title,
            "date": date,
            "post": post
        }

        print("got to where to post")
        #add the new post (document) to firebase
        posts_ref.document(title).set(json_request_form)

        #return a success message
        return "add succedeed"
    except Exception as e:
        return "failed to add"

@app.route("/read")
def readPage():
    return render_template("read.html")

@app.route("/update")
def updatePage():
    return render_template("update.html")

@app.route("/delete")
def deletePage():
    return render_template("delete.html")



#run the app
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')