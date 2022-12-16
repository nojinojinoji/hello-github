from cv2 import AKAZE_DESCRIPTOR_KAZE
from flask import Flask, request, session, jsonify, make_response, redirect, render_template
from scipy.fft import idctn
from werkzeug.security import generate_password_hash as gph
from werkzeug.security import check_password_hash as cph
from datetime import timedelta
import MySQLdb
import html
import datetime
import secrets
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString 


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

#ログイン画面リダイレクト
@app.route("/")
def root():
    return redirect("login")

#API検索画面 #WebAPI出力画面
@app.route("/getapi",methods=["GET","POST"])
def root_page():
    if request.method == "GET":
        return render_template("getapi.html")
    elif request.method == "POST":
        sex = html.escape(request.form["format1"])
        form = html.escape(request.form["format2"])
        
        # 性別分岐（全員）
        if sex=="MF":
            con = connect()
            cur = con.cursor()
            cur.execute("""
            SELECT name,money,sex
            FROM balance
            ORDER BY money DESC
            """)
        
        # 性別分岐（男性）
        elif sex=="M":
            con = connect()
            cur = con.cursor()
            cur.execute("""
            SELECT name,money,sex
            FROM balance
            WHERE sex="M"
            ORDER BY money DESC
            """)

        # 性別分岐（女性）
        elif sex=="F":
            con = connect()
            cur = con.cursor()
            cur.execute("""
            SELECT name,money,sex
            FROM balance
            WHERE sex="F"
            ORDER BY money DESC
            """)
        
        # HTMLとJSONとXMLで分岐
        if form == "HTML":
            rank = 1
            res = "<title>ランキング</title>"
            res = res + "<h2>預金残高ランキング<h2>"
            res = res + "<table align=\"center\" border=\"1\">\n"
            res = res + "\t<tr><th>&nbsp;順位&nbsp;</th><th>&nbsp;ユーザ名&nbsp;</th><th>&nbsp;残高&nbsp;</th><th>&nbsp;性別&nbsp;</th>\n"
            for row in cur:
                name = row[0]
                money = row[1]
                sex = row[2]
                if sex == "F":
                    sex = "女"
                else:
                    sex = "男"
                res = res + "<tr><th>" +str(rank)+"</th><th>" +str(name)+"</th><th>"+str(money) +"</th><th>" +str(sex)+ "</th></tr>\n"
                rank += 1
            con.commit()
            con.close()
            res = res + "</table>"
            return render_template("webapi.html",res=res)
        
        if form == "JSON":
            res = {}
            tmpa = []
            rank = 1
            for row in cur:
                dic = {}
                dic["rank"] = rank
                dic["name"] = row[0]
                dic["money"] = row[1]
                dic["sex"] = row[2]
                tmpa.append(dic)
                rank += 1
            res["content"] = tmpa
            con.commit()
            con.close()
            return render_template("webapi.html",res=res)
        
        elif form == "XML":
            res = {}
            tmpa = {}
            dic = {}
            rank = 1
            for row in cur:
                dic['rank'+str(rank)] = rank
                dic["name"+str(rank)] = row[0]
                dic["money"+str(rank)] = row[1]
                dic["sex"+str(rank)] = row[2]
                rank+=1
            xml = dicttoxml(dic)
            resp = make_response(xml)
            resp.mimetype = "text/xml"
            con.commit()
            con.close()
            return resp

#WebAPI検索結果
@app.route("/result")
def result():
    
    form = request.args.get("format")
    id = request.args.get("id")
    
    con = connect()
    cur = con.cursor()
    cur.execute("""
    SELECT name, id
    FROM users
    WHERE id=%(id)s
    """,{"id":id})

    res = "<title>検索結果</title>"
    for row in cur:
        res = res + "<table border=\"1\">\n"
        res = res + "\t<tr><td><a href=\"api?id=" + html.escape(str(row[1])) + "&"
        res = res + "format=" + html.escape(form) + "\">" + html.escape(row[0]) +"</a></td></tr>\n"
        res = res + "\t<tr><td><pre>" + html.escape(row[0]) + "</pre></td></tr>"
        res = res + "</table>"
    con.close()
    return res


#アカウント登録
@app.route("/make", methods=["GET","POST"])
def make():
        if request.method == "GET":
                return render_template('make.html')
        elif request.method == "POST":
                email = html.escape(request.form["email"]) 
                passwd = html.escape(request.form["passwd"])
                id =  html.escape(request.form["id"])
                name = html.escape(request.form["name"]) 
                birth = html.escape(request.form["birth"])
                sex = html.escape(request.form["format0"])
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

                # 登録不可のnameを検出
                nlist = list(name)
                if len(nlist)>20:
                    return render_template("make.html",msg="ユーザ名は20文字以内で登録してください")
                
                # 登録不可のidを検出
                idlist = list(id)
                if len(idlist)<3:
                    return render_template("make.html",msg="IDは3文字以上で登録してください")
                elif len(idlist)>10:
                    return render_template("make.html",msg="IDは10文字以内で登録してください")

                # 登録不可のpasswdを検出
                plist = list(passwd)
                if len(plist)<5:
                    return render_template("make.html",msg="パスワードは5文字以上で登録してください")
                elif len(plist)>20:
                    return render_template("make.html",msg="パスワードは20文字以内で登録してください")

                # メアド&IDの被りがない場合に登録ができる
                con = connect()
                cur = con.cursor()
                cur.execute("""
                INSERT INTO users
                (email,passwd,name,birth,id,sex)
                VALUES(%(email)s,%(hashpass)s,%(name)s,%(birth)s,%(id)s,%(sex)s)""",
                {"email":email, "hashpass":hashpass, "name":name, "birth":birth, "id":id,"sex":sex})
                con.commit()
                con.close()

                # 預金テーブルにも登録する
                con = connect()
                cur = con.cursor()
                cur.execute("""
                INSERT INTO balance
                (id,name,updatetime,money,sex)
                VALUES(%(id)s,%(name)s,%(updatetime)s,%(money)s,%(sex)s)""",
                {"id":id, "name":name,"updatetime":str(datetime.datetime.today()), "money":0,"sex":sex})
                con.commit()
                con.close()

                if sex=="M":
                    sex_="男性"
                else:
                    sex_="女性"
                
                return render_template("info.html",email=email,passwd=passwd,name=name,birth=birth,id=id,sex=sex_)


# ログイン
@app.route("/login", methods=["GET","POST"])
def login():
        if request.method == "GET": 
            # ログイン画面ではセッションを破棄
            session.clear() 
            return render_template('login.html') 
        elif request.method == "POST":
            id = html.escape(request.form["id"])
            passwd = html.escape(request.form["passwd"])
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
                money = html.escape(request.form["money"])
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