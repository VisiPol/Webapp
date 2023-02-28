from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory,jsonify
from werkzeug.utils import secure_filename
import os
import pymysql, json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
import time
import datetime
from pathlib import Path
from static.prediction import detect 
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/home/visipol/mysite/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}
app.secret_key = 'mysecretkey'

URI = "mysql://visipol:Summer_2023@visipol.mysql.pythonanywhere-services.com/visipol$default".format(username='visipol',password='Summer_2023',hostname='visipol.mysql.pythonanywhere-services.com:3306',databasename='visipol$default')
app.config['SQLALCHEMY_DATABASE_URI']= URI
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280

db = SQLAlchemy(app)

class Images(db.Model, SerializerMixin):
    __tablename__='images'
    id=db.Column(db.Integer, primary_key=True)
    filename=db.Column(db.Text)
    lat=db.Column(db.Text)
    lng=db.Column(db.Text)
    created_at=db.Column(db.DateTime)
    conf=db.Column(db.Text)
    severity=db.Column(db.Text)
    predictfname=db.Column(db.Text)

db.create_all()
db.session.commit()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            location = request.form.get('location').split(',')
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

            #insert_this = Images(filename=filename, lat=location[0], lng=location[1],created_at=timestamp)

            #db.session.add(insert_this)
            #db.session.commit()
            #flash('File uploaded successfully')

            # Classify the image
            # image = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # predicted_class, probabilities = classify_image(image)
            # print(predicted_class, probabilities)
            # # Render the result page with the predicted class and probability distribution
            # classes = ['class1', 'class2', 'class3', 'class4', 'class5']
            # redicted_class_name = classes[predicted_class]
            image = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            predictVal=predict(filename)
            print(predictVal) 
            insert_this = Images(filename=filename, lat=location[0], lng=location[1],created_at=timestamp,conf=predictVal[0],severity=predictVal[1],predictfname=predictVal[2])
            db.session.add(insert_this)
            db.session.commit()
            flash('File uploaded successfully')

            #return render_template('upload.html')
            return render_template('predictions.html',predictions=predictVal)
        else:
            flash('Invalid file type. Only JPG, JPEG, PNG, and GIF files are allowed.')
            return redirect(request.url)
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Route to display image locations in a Leaflet map
@app.route('/map')
def map():
    rows = Images.query.all()
    # Render the map HTML file and pass the location data as a list of rows
    return render_template('maps.html', rows=rows)


# Route to display image locations in a Leaflet map
@app.route('/getLocations')
def getLocations():
    rows = Images.query.all() 
    images=[]
    for x in rows:
        images.append('{"lat":"'+x.lat+'","lng":"'+x.lng+'","filename":"'+x.filename+'"}')
    return jsonify(images)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    rows = Images.query.all()
    return render_template('dashboard.html',rows=rows)

# Route to display image locations in a Leaflet map
@app.route('/getLatestLocations')
def getLatestLocations():
    rows=db.session.query(Images).values('lat', 'lng','filename')
    return jsonify(rows)

#@app.route('/predict')
def predict(image):
    sum_last_item = 0
    count = 0
    BASE_DIR = Path(__file__).resolve().parent
    STATIC_DIR = os.path.join(BASE_DIR,"static")

    wt_name = "/home/visipol/mysite/static/prediction/visipol.pt"
    imgsrc = "/home/visipol/mysite/uploads/"+image

    resp = detect.run(weights=wt_name,source=imgsrc,save_txt=True,save_conf=True)
    x = re.findall("exp(.*)", str(resp))
    lableFolder = x[0]
    imgx = image.split('.')
    fname = str(imgx[0])
    with open(STATIC_DIR+"/prediction/runs/detect/exp"+lableFolder+"/labels/"+fname+".txt") as f:
        for line in f:
            items = line.strip().split()
            last_item = float(items[-1])
            sum_last_item += last_item
            count += 1
    average_last_item = sum_last_item / count
    resp=average_last_item
    cropped_img_path="static/prediction/runs/detect/exp"+lableFolder+"/"+image
    if resp > 0.7:
        severity='Severe'
    elif resp > 0.5 and resp <0.7:
        severity='Major'
    else:
        severity='Minor'

    #insert_pred = Prediction(conf=resp,severity=severity,fname=cropped_img_path)
    #db.session.add(insert_pred)
    #db.session.commit()

    return [resp,severity,cropped_img_path] 
    #return render_template('predictions.html',predictions=cropped_img_path)

if __name__ == '__main__':
    app.run(debug=True)
