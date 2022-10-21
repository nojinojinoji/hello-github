from flask import Flask, request, redirect, render_template
import MySQLdb
import html
import datetime

# cursor()    　 ＝ データを1件ずつ抜き取るための仕組み
# execute()    　＝ SQLを実行する
# html.escape()　＝ 意味のあるものを無向にする
# render_template＝ HTMLを表示する（Flaskの機能）

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

#ユーザ登録
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
                
                con = connect()
                cur = con.cursor()
                #INSERTでタイトル＆説明＆投稿時間をDBに格納
                cur.execute("""
                INSERT INTO user
                (id,password,name,birth,sex)
                VALUES(%(id)s,%(password)s,%(name)s,%(birth)s,%(sex)s)""",
                {"id":id, "password":password, "name":name, "birth":birth, "sex":sex })
                con.commit()
                con.close()
                #最後にタイトルを用いてホーム画面にリダイレクトする
                
                return redirect("finish")

@app.route('/finish' ,methods=["POST","GET"]) 
def finish(): 
        # GET＝ページ表示
        if request.method == "GET": 
                return render_template('finish.html')
        elif request.method == "POST":
	        return redirect("home")

@app.route('/home',methods=["POST","GET"])
def home():
        if request.method == "GET": 
                return render_template('home.html')
        elif request.method == "POST":
                return redirect("home")

if __name__=="__main__":
    app.run(host="0.0.0.0")