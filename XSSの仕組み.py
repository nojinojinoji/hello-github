from flask import Flask, request
import html

app = Flask(__name__)

@app.route("/")
def home():
    res = ""
    res = res + "<form method=\"POST\" action=\"test\">\n"
    # 入力ボックス
    res = res + "\t<input type=\"text\" name=\"XSS\">"
    # 送信ボタン
    res = res + "\t<input type=\"submit\" value=\"submit\">"
    return res

@app.route("/test", methods=["POST"])
def xss():
    # localhost/testにアクセスされた場合にXSSの内容を表示
    # html.escapeを使わない→Javaスクリプトが埋め込まれてしまう
    # return request.form["XSS"]
    return html.escape(request.form["XSS"])

if __name__=="__main__":
    app.run(host="0.0.0.0")