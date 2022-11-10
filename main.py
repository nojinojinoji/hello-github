from cv2 import AKAZE_DESCRIPTOR_KAZE
from flask import Flask, request, session, jsonify, redirect, render_template
from scipy.fft import idctn
from werkzeug.security import generate_password_hash as gph
from werkzeug.security import check_password_hash as cph
from datetime import timedelta
import MySQLdb
import html
import datetime
import secrets
import dicttoxml


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

@app.route("/")
def root_page():
        return redirect("make")


#WebAPI検索＆表示
@app.route("/api", methods=["GET","POST"])
def api():
    return render_template("search.html")


#アカウント登録
@app.route("/make", methods=["GET","POST"])
def make(): 
        if request.method == "GET":
                return render_template('make.html')
        elif request.method == "POST":
                email = request.form["email"] 
                passwd = request.form["passwd"]
                id =  request.form["id"]
                name = request.form["name"] 
                birth = request.form["birth"] 
                hashpass=gph(passwd)

                con = connect()
                cur = con.cursor()
                # メールアドレスの被りがあるか検索
                # execute() ＝ SQLを実行する
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
                
                # idの被りがあるか検索
                con = connect()
                cur = con.cursor()
                cur.execute("""
                SELECT * FROM users WHERE id=%(id)s""",
                {"id":id})
                data=[]
                for row in cur:
                    data.append(row)
                # idが1つ以上登録されていた場合⇒登録不可
                if len(data)!=0:
                    return render_template("make.html",msg="既に存在するIDです")
                con.commit()
                con.close()

                con = connect()
                cur = con.cursor()
                # メアド&IDの被りがない場合に登録ができる
                cur.execute("""
                INSERT INTO users
                (email,passwd,id,name,birth)
                VALUES(%(email)s,%(hashpass)s,%(id)s,%(name)s,%(birth)s)""",
                {"email":email, "hashpass":hashpass, "id":id, "name":name, "birth":birth})
                con.commit()
                con.close()

                con = connect()
                cur = con.cursor()
                # 預金テーブルにも登録する
                cur.execute("""
                INSERT INTO balance
                (id,updatetime,money)
                VALUES(%(id)s,%(updatetime)s,%(money)s)""",
                {"id":id, "updatetime":str(datetime.datetime.today()), "money":0})
                con.commit()
                con.close()
                
                return render_template("info.html",email=email,passwd=passwd,name=name,birth=birth,id=id)


# ログイン
@app.route("/login", methods=["GET","POST"])
def login():
        if request.method == "GET": 
            # ログイン画面ではセッションを破棄
            session.clear() 
            return render_template('login.html') 
        elif request.method == "POST":
            id = request.form["id"] 
            passwd = request.form["passwd"]
            con = connect()
            cur = con.cursor()
            # データベースに入力されたIDがあるか探す
            cur.execute("""
                SELECT name,birth,email,id,passwd
                FROM users
                WHERE id=%(id)s""",{"id":id})
            data=[]

            for row in cur:
                data.append([row[0],row[1],row[2],row[3],row[4]])

            if len(data)==0:
                con.close()
                return render_template("login.html",msg="IDが間違っています")
            
            if cph(data[0][4],passwd):
                # ログイン情報をセッションに記録する
                session["name"]=data[0][0]
                session["id"]=data[0][3]
                con.close()
                return redirect("home")
                
            else:
                con.close()
                return render_template("login.html",msg="パスワードが間違っています")


#マイページ
@app.route("/home")
def home():
    if "name" in session:
        # セッションに記録した情報を出力
        id=session["id"]
        con = connect()
        cur = con.cursor()
        cur.execute("""
        SELECT money
        FROM balance
        WHERE id=%(id)s""",{"id":id})
        data=[]
        for row in cur:
                data.append(row)
        money=data[0][0]
        con.close()
        return render_template("mypage.html",
        id=id,
        money=money,
        name=html.escape(session["name"])) 

    else:
        # セッションがない場合ログイン画面にリダイレクト
        return redirect("login")


# 収入支出
@app.route('/inout',methods=["GET","POST"])
def inout():
        if request.method == "GET": 
                return render_template("record.html")
        elif request.method == "POST":
                money = request.form["money"]
                money = int(money)
                if "id" in session:
                        id = session["id"]
                        con = connect()
                        cur = con.cursor()
                        cur.execute("""
                        SELECT money
                        FROM balance
                        WHERE id=%(id)s""",{"id":id})
                        data=[]
                        for row in cur:
                                data.append(row)
                        amoney=data[0][0]
                        con.close()

                        # 更新後の金額＝更新前＋差額
                        amoney += money

                        con = connect()
                        cur = con.cursor()
                        cur.execute("""
                        UPDATE balance
                        SET money=%(amoney)s
                        WHERE id=%(id)s""",{"amoney":amoney, "id":id})
                        con.commit()
                        con.close()
                        return render_template("finish.html",amoney=amoney)
                else:
                # セッションがない場合ログイン画面にリダイレクト
                        return redirect("login")


if __name__=="__main__":
    app.run(host="0.0.0.0")