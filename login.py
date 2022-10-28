import email
from cv2 import AKAZE_DESCRIPTOR_KAZE
from flask import Flask, request, redirect,  session, render_template
from werkzeug.security import generate_password_hash as gph
from werkzeug.security import check_password_hash as cph
from datetime import timedelta
import MySQLdb
import html
import datetime
import secrets


def connect():
        con = MySQLdb.connect(
                host="localhost",
                user="root",
                passwd="nojiri",
                db="pbl",
                use_unicode=True,
                charset="utf8")
        return con

app = Flask(__name__)

app.secret_key = secrets.token_urlsafe(16)
app.permanent_session_lifetime = timedelta(minutes=60)

@app.route("/make", methods=["GET","POST"])
def make(): 
        if request.method == "GET": 
                return render_template('make.html')
        elif request.method == "POST":
                email = request.form["email"] 
                passwd = request.form["passwd"] 
                name = request.form["name"] 
                tel = request.form["tel"] 
                hashpass=gph(passwd)

                con = connect()
                cur = con.cursor()
                # メールアドレスの被りがあるか検索
                cur.execute("""
                SELECT * FROM users WHERE email=%(email)s""",
                {"email":email})
                data=[]
                for row in cur:
                    data.append(row)
                # メールアドレスが1つ以上登録されていた場合⇒登録不可
                if len(data)!=0:
                    return render_template("make.html",msg="既に存在するメールアドレスです")
                con.commit()
                con.close()

                con = connect()
                cur = con.cursor()
                # メアドの被りがない場合に登録ができる
                cur.execute("""
                INSERT INTO users
                (email,passwd,tel,name)
                VALUES(%(email)s,%(hashpass)s,%(tel)s,%(name)s)""",
                {"email":email, "hashpass":hashpass, "tel":tel, "name":name })
                con.commit()
                con.close()
                
                return render_template("info.html",email=email,passwd=passwd,name=name,tel=tel)

@app.route("/login", methods=["GET","POST"])
def login():
        if request.method == "GET": 
            # ログイン画面ではセッションを破棄
            session.clear() 
            return render_template('login.html') 
        elif request.method == "POST":
            email = request.form["email"] 
            passwd = request.form["passwd"]
            con = connect()
            cur = con.cursor()
            # メールアドレスの被りがあるか検索
            cur.execute("""
                SELECT passwd,name,email,tel
                FROM users
                WHERE email=%(email)s""",{"email":email})
            data=[]
            for row in cur:
                data.append([row[0],row[1],row[2],row[3]])

            if len(data)==0:
                con.close()
                return render_template("login.html",msg="IDが間違っています")
            if cph(data[0][0],passwd):
                # ログイン情報をセッションに記録する
                session["name"]=data[0][1]
                session["email"]=data[0][2]
                session["tel"]=data[0][3]
                con.close()
                return redirect("home")
            else:
                con.close()
                return render_template("login.html",msg="パスワードが間違っています")

@app.route("/home")
def home():
    if "name" in session:
        # セッションに記録した情報を出力
        return render_template("success.html",
        name=html.escape(session["name"]),
        email=html.escape(session["email"]),
        tel=html.escape(session["tel"])) 
    else:
        # セッションがない場合ログイン画面にリダイレクト
        return redirect("login")

if __name__=="__main__":
    app.run(host="0.0.0.0")