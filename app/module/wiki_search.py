import re
import wikipediaapi

'''
入力単語に基づいてWikipediaの記事を取得する
'''


def wikipediaSearch(search_text):
    res = {}
    wiki_wiki = wikipediaapi.Wikipedia('ja')
    try:
        wiki_page = wiki_wiki.page(search_text)
    except:
        return None

    wiki_content = wiki_page.text
    if len(wiki_content) == 0:
        return None

    try:
        search = [m for _, m in zip(range(2), re.finditer(
            r'\u002E|\u3002|．', wiki_content))][1]
        index = search.span()[0]
        which = search[0]

    # indexout
    except:
        # 終端が一つ
        try:
            search = re.search(r'\u002E|\u3002|．', wiki_content)
            index = search.start()
            which = search.gropu()
        # そもそも終端無し
        except:
            index = -1
            which = ' '

    # index -> 終端記号のindex，which -> 終端記号の種類「．　。　.」
    # 終端なしを考慮して最後の終端記号はwhichでつけ加える，あと2文以上の場合は<div>で分けるので終端でsplitかけてリストにする
    content = (wiki_content[:index] + which).split(which)
    # 終端が無い場合以外はsplitしたら''が-1番目に現れるので分岐
    if content[-1] == '':
        # 最後を出す（削除）ー破壊的
        content.pop()

    res['content'] = content  # 配列(最大2）
    res['link'] = wiki_page.fullurl
    # dictが返る -> エラーもしくは何も文字が無い場合はNoneが上記で返る
    return res
