# cursor()    　 ＝ データを1件ずつ抜き取るための仕組み
# execute()    　＝ SQLを実行する
# html.escape()　＝ 意味のあるものを無向にする
# render_template＝ HTMLを表示する（Flaskの機能）


from cv2 import AKAZE_DESCRIPTOR_KAZE
from flask import Flask, request, session, redirect, render_template
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

@app.route("/")
def root_page():
        return redirect("adduser")

#アカウント登録
@app.route("/adduser", methods=["GET","POST"])
def adduser_page():
        # GET＝ページ表示
        if request.method == "GET": 
                return render_template('adduser.html')
        # POST＝DB登録
        elif request.method == "POST":
                id = request.form["id"] #idを受け取る
                password = request.form["password"] #passwordを受け取る
                name = request.form["name"] #nameを受け取る
                birth = request.form["birth"] #birthを受け取る
                sex = request.form["sex"] #sexを受け取る
                money = request.form["money"]

                con = connect()
                cur = con.cursor()
                #INSERTでタイトル＆説明＆投稿時間をDBに格納
                cur.execute("""
                INSERT INTO user
                (id,password,name,birth,sex)
                VALUES(%(id)s,%(password)s,%(name)s,%(birth)s,%(sex)s)""",
                {"id":id, "password":password, "name":name, "birth":birth, "sex":sex })
                cur.execute("""
                INSERT INTO balance
                (id,date,puramai,money,m_id)
                VALUES(%(id)s,%(date)s,%(puramai)s,%(money)s,%(m_id)s)""",
                {"id":id, "date":str(datetime.datetime.today()), "puramai":0, "money":money, "m_id":id })
                con.commit()
                con.close()
                #最後にタイトルを用いてホーム画面にリダイレクトする
                
                return redirect("finish")

# 登録完了
@app.route('/finish' ,methods=["POST","GET"]) 
def finish(): 
        # GET＝ページ表示
        if request.method == "GET": 
                return render_template('finish.html')
        elif request.method == "POST":
	        return redirect("mypage")

#マイページ
@app.route('/mypage',methods=["POST","GET"])
def home():
        if request.method == "GET": 
                name="nojiri"
                money=123456
                return render_template("mypage.html",name=name, money=money)
        elif request.method == "POST":
                return redirect("record")

#入出金の記録
@app.route('/record',methods=["POST","GET"])
def record():
        if request.method == "GET": 
                return render_template("record.html")
        elif request.method == "POST":
                puramai = request.form["puramai"]
                con = connect()
                cur = con.cursor()
                
                #cur.execute("""
                #SELECT money
                #FROM balance
                #WHERE id=%(id)s""",
                #{"id":2})

                cur.execute("""
                UPDATE balance
                SET money = 1000
                WHERE id=2""")
                
                con.commit()
                con.close() 

                return redirect("completion")

#記録完了
@app.route('/completion',methods=["POST","GET"])
def completion():
        if request.method == "GET": 
                return render_template("completion.html")
        elif request.method == "POST":
                return redirect("completion")


if __name__=="__main__":
    app.run(host="0.0.0.0")