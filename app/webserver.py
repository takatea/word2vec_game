# -*- coding:utf-8 -*-
from flask import Flask, render_template, request, redirect
from module.w2v_game import word2vec_game

# 初期起動で10sくらいかかる
w2v = word2vec_game()  # reload処理をつける

app = Flask(__name__, static_folder='html/static/',
            template_folder='html/templates')

# jsonで日本語が文字化けするのを回避
app.config['JSON_AS_ASCII'] = False


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        title = "TOP"
        return render_template("index.html", title=title)
    else:
        return "{ \"message\": \"POST Requests no messages\"}"


@app.route("/game_used_word2vec", methods=["GET", "POST"])
def game_used_word2vec():
    if request.method == "GET":
        title = "Game_used_word2vec"
        # reload
        print('========== reloading of w2v is success! ========')
        w2v.reload()  # 初回もこのreloadが呼ばれるが現状問題ない
        return render_template("game.html", title=title)
    else:
        return "{ \"message\": \"POST Requests no messages\"}"


@app.route("/start", methods=["GET", "POST"])
def start():
    if request.method == "POST":
        # 実行(引数無し)
        return w2v.target_out()
    else:
        return "{ \"message\": \"GET Requests no messages\"}"


@app.route("/game", methods=["GET", "POST"])
def game():
    if request.method == "POST":
        # game送信
        return w2v.main(request.get_data())
    else:
        return "{ \"message\": \"GET Requests no messages\"}"


if __name__ == "__main__":
    # app.debug = True
    app.run(host='0.0.0.0', port=8888)
