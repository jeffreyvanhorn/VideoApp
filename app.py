#imports
"""
from flask import Flask
from flask import render_template
"""

import os
from flask import Flask, request, jsonify, render_template
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from google.cloud import storage
import pyrebase

config = {
    "apiKey": "AIzaSyD40fENGn9XwqfCFxJvqGYP2B4t7dOIr34",
    "authDomain": "video-practice-8d962.firebaseapp.com",
    "projectId": "video-practice-8d962",
    "storageBucket": "video-practice-8d962.appspot.com",
    "databaseURL": "video-practice-8d962-default-rtdb.firebaseio.com",
    "messagingSenderId": "355762864667",
    "appId": "1:355762864667:web:58fcc73ae4a4fdec6eaebe"
}

firebase = pyrebase.initialize_app(config)

#make the app
app = Flask(__name__)

#SETUP THE FIRESTORE DB CONNECTION
#use the private key we generated to connect to the database
cred = credentials.Certificate('key.json')
#initialize the app with the credentials
#default_app = initialize_app(cred, {'storageBucket': 'video-practice-8d962.appspot.com'})

default_app = initialize_app(cred)

#create a database connection to the client
db = firestore.client()
#get the collection of post documents
posts_ref = db.collection('posts')



#FUNCTIONS THAT SUPPORT THE ROUTES
def getAllPosts():
    return [doc.to_dict() for doc in posts_ref.stream()]

def getSinglePost(postID):
    posts_ref = db.collection('posts').document(postID)
    post = posts_ref.get()
    return post

def createNewOrUpdateEntire():
    #get the request data from the form
    aName = request.form.get("aname")
    title = request.form.get("title")
    date = request.form.get("date")
    post = request.form.get("post")
    #generate the id by stripping whitespaces from name and title and concatenating
    strippedName = aName.replace(" ", "")
    strippedTitle = title.replace(" ", "")
    postID = strippedName + strippedTitle

    #needs to be put into json form
    json_request_form = {
        "name": aName,
        "id": postID,
        "title": title,
        "date": date,
        "post": post
    }

    #add the new post (document) to firebase
    posts_ref.document(postID).set(json_request_form)



#ROUTES

@app.route("/")
def mainPage():
    return render_template("index.html")

@app.route("/upload")
def uploadPage():
    return render_template("upload.html")

@app.route("/upload/new", methods = ["GET", "POST"])
def uploadNew():
    try:
        #get the request data sent by the upload form
        name = request.form.get("name")
        title = request.form.get("title")
        date = request.form.get("date")
        img = request.form.get("imgupload")
        post = request.form.get("desc")

        strippedName = name.replace(" ", "")
        strippedTitle = title.replace(" ", "")
        postID = strippedName + strippedTitle

        print("img")
        #print(img)

        #access firebase storage
        storage = firebase.storage()

        file_name = postID + "IMG"

        path_on_cloud = "images/" + file_name
        path_local = file_name
        print(file_name)
        print("trying local file")
        print(request.files)
        local_file = request.files["imgupload"]
        print("passed local file")
        #path_local = "disney-plus-main.jpg"
        #storage.child(path_on_cloud).put(path_local)
        storage.child(path_on_cloud).put(local_file)

        return "works"
    except Exception as e:
        return "failed"

@app.route("/viewall")
def viewAllPage():
    return render_template("viewAll.html")

#route to handle going to the page to enter info for new post
@app.route("/create")
def createPage():
    return render_template("create.html")

@app.route("/create/new", methods = ["POST"])
def createNew():
    #set the message passed to the user to be success by default
    result_of_add_message = "succedeed"
    try:
        
        #get the request data from the form
        aName = request.form.get("aname")
        title = request.form.get("title")
        date = request.form.get("date")
        post = request.form.get("post")
        #generate the id by stripping whitespaces from name and title and concatenating
        strippedName = aName.replace(" ", "")
        strippedTitle = title.replace(" ", "")
        postID = strippedName + strippedTitle

        #needs to be put into json form
        json_request_form = {
            "name": aName,
            "id": postID,
            "title": title,
            "date": date,
            "post": post
        }

        #add the new post (document) to firebase
        posts_ref.document(postID).set(json_request_form)
        
        createNewOrUpdateEntire()

    except Exception as e:
        #if something goes wrong change the message
        result_of_add_message = "failed to add"

    #return the created template
    #pass the message to the template which it will render
    return render_template("created.html", message=result_of_add_message)


#read all posts
@app.route("/read", methods = ["GET"])
def readPage():
    try:
        #all_posts = [doc.to_dict() for doc in posts_ref.stream()]
        return render_template("read.html", posts=getAllPosts())
    except Exception as e:
        return f"An Error Occured: {e}"


#read individual post
@app.route("/read/<string:postID>")
def readSinglePost(postID):
    try:
        #connect to the collection by specifying the collection and postID
        posts_ref = db.collection('posts').document(postID)
        post = posts_ref.get()
        
        #check if the post exists
        if post.exists:
            print("true")
        else:
            print("false")

        #render the template for a single post 
        #and pass the post in dictionary form to the template
        return render_template("readOne.html", post=post.to_dict())
    except Exception as e:
        return f"An Error Occured: {e}"

#route to handle when a user wants to update a post
@app.route("/update")
def updatePage():
    #get all of the posts so one to edit can be chosen
    return render_template("update.html", posts = getAllPosts())

@app.route("/update/<string:postID>")
def updatePost(postID):
    try:
        return render_template("updateOne.html", post = getSinglePost(postID).to_dict())
    except Exception as e:
        return f"An Error Occured: {e}"


@app.route("/update/<string:postID>/update", methods = ["POST"])
def processUpdate(postID):
    #set the message passed to the user to be success by default
    result_of_add_message = "succedeed"
    try:
        #get the request data from the form
        aName = request.form.get("aname")
        title = request.form.get("title")
        date = request.form.get("date")
        post = request.form.get("post")
        #generate the id by stripping whitespaces from name and title and concatenating
        strippedName = aName.replace(" ", "")
        strippedTitle = title.replace(" ", "")
        postID = strippedName + strippedTitle

        #needs to be put into json form
        json_request_form = {
            "name": aName,
            "id": postID,
            "title": title,
            "date": date,
            "post": post
        }

        #add the new post (document) to firebase
        posts_ref.document(postID).set(json_request_form)

    except Exception as e:
        #if something goes wrong change the message
        result_of_add_message = "failed to add"

    #return the created template
    #pass the message to the template which it will render
    return render_template("created.html", message=result_of_add_message)

@app.route("/delete")
def deletePage():
    return render_template("delete.html", posts = getAllPosts())

@app.route("/delete/<string:postID>")
def delete(postID):
    try:
        db.collection('posts').document(postID).delete()
        #return render_template("updateOne.html", post = getSinglePost(postID).to_dict())
        return render_template("delete.html")
    except Exception as e:
        return f"An Error Occured: {e}"

#run the app
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')