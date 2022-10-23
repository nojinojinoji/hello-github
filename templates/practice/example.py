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
def title_page():
        # GET＝検索により該当のスレッドを表示
        if request.method == "GET":
                if request.args.get("word") is not None:
                        word = request.args.get("word") #word＝検索の文字列を格納する変数
                        con = connect()
                        cur = con.cursor()
                        cur.execute("""
                        SELECT thread_id,title,intro,create_date
                        FROM thread
                        WHERE intro like %(intro)s OR title like %(title)s
                        """,{"intro":"%"+word+"%", "title":"%"+word+"%"})
                        res = ""
                        for col in cur:
                                res = res + "<tr><td><a href=\"thread?id="+html.escape(str(col[0]))+"\">"+html.escape(col[1])+"</a></td>"
                                res = res + "<td>"+html.escape(str(col[3]))+"</td></tr>" 
                                res = res + "<tr><td colspan=\"2\"><pre>" + html.escape(col[2])+"</pre></td></tr>" 
                        con.close()
                        return render_template("title.html",page_title=html.escape(word)+"の検索結果",result=res)
                else:
                        # 空欄の場合は何も表示しない
                        return render_template("title.html",page_title="ホーム画面")
        # POST＝スレッドの作成投稿
        elif request.method == "POST":
                title = request.form["title"] #タイトルの文字列を受け取る
                intro = request.form["intro"] #説明の文字列を受け取る
                con = connect()
                cur = con.cursor()
                #INSERTでタイトル＆説明＆投稿時間をDBに格納
                cur.execute("""
                INSERT INTO thread
                (title,intro,create_date)
                VALUES(%(title)s,%(intro)s,%(create_date)s)""",
                {"title":title, "intro":intro, "create_date":str(datetime.datetime.today())})
                con.commit()
                con.close()
                #最後にタイトルを用いてホーム画面にリダイレクトする
                return redirect("home?word="+html.escape(title))

#掲示板にアクセスした場合の処理
@app.route("/thread", methods=["GET","POST"])
def thread_page():
        #GETにリクエストされた場合⇒掲示板のIDを受け取る
        if request.method == "GET":
                if request.args.get("id") is None:
                        return redirect("home")

                else:
                        thread_id=request.args.get("id")
                        con = connect()
                        cur = con.cursor()
                        #掲示板IDから掲示板のタイトルを取得
                        cur.execute("""
                        SELECT title
                        FROM thread
                        WHERE thread_id=%(thread_id)s""",
                        {"thread_id":html.escape(thread_id)})
                        
                        title = ""
                        for row in cur:
                                title = row[0]
                        con.close()
                        con = connect()
                        cur = con.cursor()
                        #掲示板IDからコメントと投稿日時を取得
                        cur.execute("""
                        SELECT comment,send_date
                        FROM comment
                        WHERE thread_id=%(thread_id)s""",
                        {"thread_id":html.escape(thread_id)})
                        
                        res = ""
                        for row in cur:
                                res = res + "<tr><td>投稿日時"+html.escape(str(row[1]))+"</td></tr>\n"
                                res = res + "<tr><td><pre>"+html.escape(str(row[0]))+"</pre></td></tr>\n" 
                        con.close()
                        return render_template("comment.html",thread_id=thread_id, result=res,title=title)

        # POST＝コメントの送信                
        elif request.method == "POST":
                cont = request.form["cont"] #cont＝コメント内容
                thread_id = request.form["id"] #id＝掲示板ID
                con = connect()
                cur = con.cursor()
                #INSERTで掲示板ID＆コメント＆投稿日時を掲示板に追加する
                cur.execute("""
                        INSERT INTO comment
                        (thread_id,comment,send_date)
                        VALUES(%(thread_id)s,%(comment)s,%(send_date)s)""",
                        {"thread_id":thread_id ,"comment":cont,"send_date":str(datetime.datetime.today())})
                con.commit()
                con.close()
                #最後にGETを用いて掲示板IDよりリダイレクトする
                return redirect("thread?id="+html.escape(str(thread_id)))


if __name__=="__main__":
    app.run(host="0.0.0.0")

