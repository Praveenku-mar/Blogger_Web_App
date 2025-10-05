from flask import Flask,flash,render_template,request,url_for,redirect,session
from flask_mysqldb import MySQL
from functools import wraps
from werkzeug.utils import secure_filename

import os
import random


UPLOAD_FOLDER='static/images'
FILE_EXTENSIONS = {'png', 'jpg', 'jpeg'}

UPLOAD_FOLDER1='static/profile'
FILE_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app=Flask(__name__)
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='blog'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql=MySQL(app)

@app.route("/")
@app.route("/index",methods=['POST','GET'])
def index():
    return render_template("index.html")
    
@app.route("/login",methods=['POST','GET'])
def login():
    if request.method=='POST':
        if request.form["submit"]=="Login":
            b=request.form["email"]
            c=request.form["pass"]
            cur=mysql.connection.cursor()
            cur.execute("select * from details where Email=%s and pwd=%s",(b,c))
            data=cur.fetchone()
            if data:
                session['logged_in']=True
                session['Register_Id']=data["Register_Id"]
                session['Email']=data["Email"]
                session['pwd']=data["pwd"]
                flash('Login Successfully','success')
                return redirect('loginindex')
            else:
                flash('Invalid Login.Try Again','danger')
    return render_template("login.html")
    
@app.route("/loginindex",methods=['POST','GET'])
def loginindex():
    cur=mysql.connection.cursor()
    cur.execute("select Name,bname,bimg,desp,bdate from tbl_blog,details where tbl_blog.did=details.Register_Id")
    data=cur.fetchall()
    return render_template("loginindex.html",datas=data)
    
@app.route('/logout1')
def logout1():
    session.clear()
    return redirect(url_for("login"))
    
def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('unauthorized,please Login','danger')
            return redirect(url_for('index'))
    return wrap
    
@app.route("/addblog",methods=['POST','GET'])
def addblog():
    return render_template("addblog.html")


def allowed_extensions(file_name):
    return '.' in file_name and file_name.rsplit('.',1)[1].lower() in FILE_EXTENSIONS
	
@app.route('/addblogform',methods=['POST','GET'])
def addblogform():

    if request.method=='POST': 
        bname=request.form['blogtit']      
        desp=request.form['desp']    
        file = request.files['blogimg']

        if file and allowed_extensions(file.filename):
            filename, file_extension = os.path.splitext(file.filename)
            new_filename = secure_filename(str(random.randint(10000,99999))+"."+file_extension)
            file.save(os.path.join(UPLOAD_FOLDER, new_filename))   

            cur=mysql.connection.cursor()
            cur.execute("INSERT INTO tbl_blog(bname,bimg,desp,did) VALUES  (%s,%s,%s,%s)", (bname,new_filename,desp,session['Register_Id']))
            mysql.connection.commit()
            cur.close()    
            flash('Details Added Successfully','success')
    return render_template("addblogform.html")
    
@app.route("/addblogview",methods=['POST','GET'])
def addblogview():
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_blog")
    data=cur.fetchall()
    return render_template("addblogview.html",datas=data)

@app.route('/addblogviewedit/<string:did>',methods=['POST','GET'])
def addblogviewedit(did):
    if request.method=='POST':
        a=request.form["blogtit"]
        b=request.form["desp"]
        cur=mysql.connection.cursor()
        cur.execute("UPDATE tbl_blog SET bname=%s,desp=%s where did=%s",(a,b,did))
        mysql.connection.commit()
        cur.close()
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_blog where did=%s",(did,))
    data=cur.fetchone()	
    return render_template("addblogviewedit.html",datas=data)
    
@app.route('/delete/<string:did>',methods=['POST','GET'])
def delete_blog(did):
    cur=mysql.connection.cursor()
    cur.execute("delete from tbl_blog where did=%s",(did,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("addblogview"))
    
@app.route("/updateprofile",methods=['POST','GET'])
def updateprofile():
    did = session.get('did')
    if not did:
        return redirect(url_for('login'))
    if request.method=='POST':
        a=request.form["uname"]
        b=request.form["email"]
        d=request.form["age"]
        e=request.form["phone"]
        cur=mysql.connection.cursor()
        cur.execute("UPDATE details SET Name=%s,Email=%s,Age=%s,Phone_no=%s where did=%s" ,(a,b,d,e,did))
        mysql.connection.commit()
        cur.close()
    cur=mysql.connection.cursor()
    cur.execute("select * from details where did=%s",(did,))
    data=cur.fetchone()	
    return render_template("updateprofile.html", datas=data)
    
@app.route("/changepass", methods=['POST', 'GET'])
def changepass():
    if request.method == 'POST':
        new_password = request.form['new']
        confirm_password = request.form['con']
        if new_password == confirm_password:
            cur = mysql.connection.cursor()
            cur.execute("UPDATE details SET pwd=%s WHERE did=%s", (new_password, session['did']))
            mysql.connection.commit()
            cur.close()
            flash('Password updated successfully.', 'success')
            return redirect(url_for("changepass"))
        else:
            flash('Passwords do not match. Please try again.', 'error')
    return render_template("changepass.html")

@app.route("/uploadimg",methods=['POST','GET'])
def uploadimg():
    if request.method=='POST':
        file=request.files['file']
        if file and allowed_extensions(file.filename):
            filename, file_extensions = os.path.splitext(file.filename)
            new_filename = secure_filename(str(random.randint(10000,99999)) + '.' +file_extensions)
            file.save(os.path.join(UPLOAD_FOLDER1,new_filename))
            cur = mysql.connection.cursor()
            cur.execute("Update details set image=%s where Register_Id=%s ",(new_filename,session['Register_Id']))
            mysql.connection.commit()
            cur.close()
            flash("Details add successfully",'success')
    return render_template("uploadimg.html")

@app.route("/register",methods=['POST','GET'])
def register():
    if request.method=='POST':
        a=request.form["uname"]
        b=request.form["email"]
        c=request.form["pass"]
        d=request.form["age"]
        e=request.form["phone"]
        cur=mysql.connection.cursor()
        cur.execute("Insert into details(Name,Email,pwd,Age,Phone_no) values(%s,%s,%s,%s,%s)",(a,b,c,d,e))
        mysql.connection.commit()
        cur.close()
    return render_template("register.html")
    
@app.route("/views")
def views():
    cur=mysql.connection.cursor()
    cur.execute("select * from details")
    data=cur.fetchall()
    return render_template("views.html",datas=data)
    
@app.route('/edit/<string:did>',methods=['POST','GET'])
def edit(did):
    if request.method=='POST':
        a=request.form["uname"]
        b=request.form["email"]
        c=request.form["pass"]
        d=request.form["age"]
        e=request.form["phone"]
        cur=mysql.connection.cursor()
        cur.execute("UPDATE details SET Name=%s,Email=%s,pwd=%s,Age=%s,Phone_no=%s where did=%s",(a,b,c,d,e,did))
        mysql.connection.commit()
        cur.close()
    cur=mysql.connection.cursor()
    cur.execute("select * from details where did=%s",(did,))
    data=cur.fetchone()	
    return render_template("edit.html",datas=data)
    
@app.route('/delete/<string:did>', methods=['POST','GET'])
def delete(did):
    cur=mysql.connection.cursor()
    cur.execute("delete from details where did=%s",(did,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("views"))
    
if __name__=='__main__':
    app.secret_key='secret123'
    app.run(debug=True)
    
    
    
    