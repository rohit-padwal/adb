from flask import Flask, render_template, request, redirect, url_for
import os
import pyodbc
from azure.storage.blob import BlobServiceClient


app = Flask(__name__)
app.config["DEBUG"] = True
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Container Connection String
connect_str = 'DefaultEndpointsProtocol=https;AccountName=rohitadb;AccountKey=LZQIDLMv4x/eAJw7vFSkjKpvsOLkB21WDUmnvwi9cm6CI/qmmHQ98YQCCxVaEfVMFlVM/YLaRalw+AStYO20fw==;EndpointSuffix=core.windows.net'

#Container data - get container client
container_name = "assignment1container"
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
try:
    container_client = blob_service_client.get_container_client(container_name)
    container_client.get_container_properties()
except Exception as e:
    print(e)
    print("Creating container...")
    container_client = blob_service_client.create_container(container_name)

#Get image url of uploaded photos
def getImageUrl(imageName):
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    try:
        container_client = blob_service_client.get_container_client(container_name)
        container_client.get_container_properties()
    except Exception as e:
        print(e)
        print("Creating container...")
        container_client = blob_service_client.create_container(container_name)
    blob_client = container_client.get_blob_client(imageName)
    return blob_client.url

#Link to home page
@app.route('/')
def index():
    return render_template('index.html')

#Upload files to static folder
@app.route("/", methods=['POST'])
def uploadFiles():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
    return redirect(url_for('index'))


#Search people by criteria
@app.route("/search", methods=['POST','GET'])
def searchByName():
    if request.method == 'POST':
        name = request.form.get("username")
        salary = request.form.get("salary")
        if request.form.get("Delete"):
            #Code for delete entry
            if name != '' and salary == '':
                deletePerson(name)
                return redirect(f'/allPeople')

        elif request.form.get("Update"):
            print("Inside update")
            if name != '' and salary != '':
                updateSalary(name, salary)
                return redirect(f'/userName/{name}')

        elif request.form.get("Submit"):
            if name != '':
                return redirect(f'/userName/{name}')
            elif salary != '':
                return redirect(f'/userSalary/{salary}')

        else:
            return redirect(f'/allPeople')


#Form for search criteria
@app.route("/form")
def form():
    return render_template('form.html')


#Object created to store Person data with default empty fields
class Person:
  def __init__(self, Name, State = '', Salary = '', Grade = '', Room = '', Telnum = '', Picture = '', Keywords = '', ImageURL = ''):
    self.Name = Name
    self.State = State
    self.Salary = Salary
    self.Grade = Grade
    self.Room = Room
    self.Telnum = Telnum
    self.Picture = Picture
    self.Keywords = Keywords
    self.ImageURL = ImageURL


#Display all people in data
@app.route("/allPeople")
def allPeople():
    conn = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:adb-rohit.database.windows.net,1433;Database=adb;Uid=rohit;Pwd=Adbsetup@2022;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM people;""")
    data = []
    users = cursor.fetchall()
    conn.commit()
    conn.close()
    for user in users:
        imageUrl = "_"
        if user.Picture != None:
            imageUrl = getImageUrl(user.Picture)
        data.append(Person(user.Name, user.State, user.Salary, user.Grade, user.Room, user.Telnum, user.Picture, user.Keywords, imageUrl))
    return render_template('user.html', data = data)



#Update person salary
def updateSalary(name, salary):
    print("Inside update function")
    conn = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:adb-rohit.database.windows.net,1433;Database=adb;Uid=rohit;Pwd=Adbsetup@2022;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    cursor = conn.cursor()
    cursor.execute("""UPDATE people set Salary=? where Name=?;""", salary, name)
    conn.commit()
    conn.close()


#Delete person
def deletePerson(name):
    conn = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:adb-rohit.database.windows.net,1433;Database=adb;Uid=rohit;Pwd=Adbsetup@2022;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    cursor = conn.cursor()
    cursor.execute("""DELETE FROM people where Name=?;""", name)
    conn.commit()
    conn.close()


#Search people by Salary
@app.route("/userSalary/<salary>")
def userSalary(salary):
    conn = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:adb-rohit.database.windows.net,1433;Database=adb;Uid=rohit;Pwd=Adbsetup@2022;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM people WHERE salary <= ?""", salary)
    users = cursor.fetchall()
    conn.commit()
    conn.close()
    data = []
    for user in users:
        imageUrl = "_"
        if user.Picture != None:
            imageUrl = getImageUrl(user.Picture)
        data.append(Person(user.Name, user.State, user.Salary, user.Grade, user.Room, user.Telnum, user.Picture, user.Keywords, imageUrl))
    return render_template('user.html', data = data)


#Search people by Name
@app.route("/userName/<name>")
def userName(name):
    conn = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:adb-rohit.database.windows.net,1433;Database=adb;Uid=rohit;Pwd=Adbsetup@2022;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM people WHERE name = ?""", name)
    user = cursor.fetchone()
    conn.commit()
    conn.close()
    data = []
    blob_client = container_client.get_blob_client(user.Picture)
    imageUrl = "_"
    if user.Picture != None:
        imageUrl = getImageUrl(user.Picture)
    data.append(Person(user.Name, user.State, user.Salary, user.Grade, user.Room, user.Telnum, user.Picture, user.Keywords, imageUrl))
    return render_template('user.html', data = data)


#View Photos uploaded to azure container
@app.route("/upload-photos")
def view_photos():
    blob_items = container_client.list_blobs()
    img_html = "<div style='display: flex; justify-content: space-between; flex-wrap: wrap;'>"
    for blob in blob_items:
        blob_client = container_client.get_blob_client(blob.name)
        print(blob.name)
        img_html += "<img src='{}' width='auto' height='200' style='margin: 0.5em 0;'/>".format(
            blob_client.url)
    img_html += "</div>"
    return """
    <head>
    <!-- CSS only -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    </head>
    <body>
        <div class="container">
            <div class="card" style="margin: 1em 0; padding: 1em 0 0 0; align-items: center;">
                <h3>Upload new photos</h3>
                <div class="form-group">
                    <form method="post" action="/upload-photos" 
                        enctype="multipart/form-data">
                        <div style="display: flex;">
                            <input type="file" accept=".png, .jpeg, .jpg, .gif" name="photos" multiple class="form-control" style="margin-right: 1em;">
                            <input type="submit" class="btn btn-primary">
                        </div>
                    </form>
                </div> 
            </div>
    """ + img_html + "</div></body>"


#Upload photos to azure container
@app.route("/upload-photos", methods=["POST"])
def upload_photos():
    filenames = ""
    for file in request.files.getlist("photos"):
        try:
            container_client.upload_blob(file.filename,file)
            filenames += file.filename + "<br /> "
        except Exception as e:
            print(e)
            print("Ignoring duplicate filenames")  # ignore duplicate filenames
    return redirect('/upload-photos')


if (__name__ == "__app__"):
    app.run(port = 5000)
