import re
import regex
import random
import json
import numpy as np
import gensim
from gensim.models import word2vec
from module.wiki_search import wikipediaSearch


class word2vec_game():

    ''' 初期化 '''

    def __init__(self):

        self.model = word2vec.Word2Vec.load(
            "./data/wiki_neologd.model")  # load word2vec model
        self.topn = 12  # 上位何位までの類似度を計算するか（現在12で固定する前提で実装，後に拡張予定）

        self.target_num = 1000  # 問題数（サーバ起動時に事前に1000問生成する）
        self.pre_target()  # ターゲットを決定

        self.target_check_words = []  # どんな単語を使ったか => 現在は格納のみで生成時に確認処理をしているわけではない（後に実装予定）

        self.pos = []  # word2vecモデルへ入力するポシティブ単語リスト（リロードなどで必ず初期化する）
        self.neg = []  # word2vecモデルへ入力するネガティブ単語リスト（リロードなどで必ず初期化する）

        self.question_num = 0  # 質問制限は現段階ではもうけてないため問題生成のたびに加算（現状 => 生成した問題数に達した段階でエラーがでる，後に改善予定）

        self.did_target_out = False  # ターゲット生成の前にplusとかがされていないか

    ''' reload時の再初期化用 '''

    def reload(self):
        self.current_str = ''
        self.did_target_out = False

        self.question_num = 0  # 再度生成をするわけではないので，問題を使い切った段階でエラーがでる（後に改善予定）

    ''' 結果の出力（もしクリアしていればクリアフラグをTrueにしてフロントへ返す） '''

    def out_result(self):

        self.count += 1  # countは「次の」試行回数とするため +1 加算する

        # eq : 計算式（EQ : フランス　ー　パリ + 日本 (= 東京 類似度高い )）
        # target_check : OP (+ or -) が押されたときの戻り値でターゲットが生成されているかを表す
        # word_check:単語があるか．
        # => ここにきてる段階でどちらもOK
        res = {'top12': dict(), 'target_check': 'OK', 'word_check': 'OK'}

        # 類似度ランキングを計算
        top12 = self.model.most_similar(
            positive=self.pos, negative=self.neg, topn=self.topn
        )

        clear_flag = False  # クリア確認前の初期化
        for i, data in enumerate(top12):
            # 正解フェーズ（5位以内にターゲット単語がある場合）
            # -> クライアント側で表も出したいのでここではflagを立てる
            if ((i < 5) and (data[0] == self.target_check_words[-1])):
                clear_flag = True

            # data[0]:単語，
            # data[1]:それに対応した類似度(stringに結局変わるのでここでformatで書き換える)
            res['top12'][data[0]] = '%.3f' % data[1]

        out = 'EQ(%d回): ' % (self.count) + self.current_str

        # クリアしている場合
        if clear_flag:
            # 名前は妥当じゃないかもしれないがいいのが思い浮かばないので，eqで揃える
            res['eq'] = out  # 改行はフロント側で判定
            res['finish_print'] = 'クリア条件に達しました．'

            res['finish'] = 'finish'  # スタートボタンを出すフラグ

            self.did_target_out = False  # ターゲットフラグをFalseへ戻す

        # 10手に達した場合 => 失敗
        elif self.count >= 10:
            res['eq'] = out
            res['finish_print'] = '10手に達したため失敗です．'
            # スタートボタンを出すフラグ
            res['finish'] = 'finish'
            # ターゲットフラグを戻す
            self.did_target_out = False

        # それ以外は継続
        else:
            res['eq'] = out

        # json：{top12, eq, finish, target_check[OK], word_check[OK]}
        return json.dumps(res, ensure_ascii=False)

    ''' 出題問題選定(target_num数単語が確保される)'''

    def pre_target(self):
        # 前処理
        words = self.model.wv.index2word
        p = re.compile('[\u30A1-\u30FF]+')
        p2 = regex.compile(r'\p{Script=Han}+')

        # (隠れ制約)3文字以上5文字以下
        num_min = 3
        num_max = 5
        words_cut = [word for word in words if (p.fullmatch(word) or p2.fullmatch(
            word)) if (len(word) >= num_min and len(word) <= num_max)]

        self.target_words = words_cut  # ターゲット単語リスト => ランダムに選択

        # min, max (後半特にわからないのがあるので5で割った数), size
        self.target_index = np.random.randint(
            0, len(words_cut) // 5, self.target_num).tolist()
        return 'dummy'

    ''' 問題生成 '''

    def target_out(self):
        # 各初期化
        self.pos = []
        self.neg = []
        self.count = 0
        self.question_num += 1
        self.did_target_out = True

        # start_word
        # => wikipediaに記事があることが前提なので，ここで無限loop
        # => 基本的にあるので一回で終わるはず，なければ次のターゲットへ
        while True:
            # ターゲット1 (開始単語) を取得
            target1 = self.target_words[self.target_index.pop(0)]
            target1_wiki = wikipediaSearch(target1)  # 開始単語に関するWikipedia情報を取得する

            # 結果的に一番最後に追加されたものが「-2番目」に対応
            self.target_check_words.append(target1)
            if not (target1_wiki == None):
                break

        # goal_word（top15以内から選定する）
        # 類似度が6位から15位の間の単語を選択する
        while True:
            topn = 15  # ここのtopnは問題生成のときのみ使われるものでフィールド変数とは異なる

            # 一単語選定（6位から15位の間でランダム）=> target2 = （単語, スコア）
            target2 = self.model.most_similar(positive=[target1], topn=topn)[
                random.randint(5, topn) - 1]
            target2 = target2[0]  # 単語のみ抽出
            target2_wiki = wikipediaSearch(target2)  # 終了単語に関するWikipedia情報を取得する
            if not (target2_wiki == None):
                self.target_check_words.append(target2)
                break

        # 始まり単語と終了単語をまとめる
        targets = {'target1': target1, 'target2': target2}

        # wiki_dict(content, link)をまとめる
        # ターゲット名にすることでjs側で名前を簡単に特定できるようにする
        wiki_dict = {target1: target1_wiki, target2: target2_wiki}

        # ひとまず現在のdict生成
        res = {'targets': targets, 'wiki': wiki_dict}

        self.pos.append(target1)  # positiveへ初期値を追加

        self.current_str = target1  # current_strの宣言と初期化
        # 0回目のEQを追加
        res['eq'] = 'EQ(%d回): ' % (self.count) + target1

        # json : {targets, wiki, eq}
        return json.dumps(res, ensure_ascii=False)

    # op（+ or -）が押された時に呼ばれるメイン処理

    def main(self, requests):

        # ターゲット生成されているか
        if not self.did_target_out:
            res = {'target_check': 'NG'}
            return json.dumps(res, ensure_ascii=False)

        # リクエスト処理（'text':入力単語，'op':plus or minus)
        res = json.loads(requests)
        word = res['word']
        op = res['op']

        # word check -> なければ無いことをjsonで伝える
        # 'word_check':'NG'
        try:
            self.model[word]
        except:
            res = {
                'word_check': 'NG',
                'target_check': 'OK',
                'eq': 'EQ(%d回): ' % (self.count) + self.current_str
            }
            return json.dumps(res, ensure_ascii=False)

        # フィールド追加処理 => 結果を返す
        if op == 'plus':
            self.pos.append(word)
            self.current_str += ' + ' + word
        elif op == 'minus':
            self.neg.append(word)
            self.current_str += ' - ' + word
        else:
            return "{ \"Server Error\": Operation Error.}"

        return self.out_result()
