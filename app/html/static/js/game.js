function contentsCheck(requests) {
  // keyが返ってくる
  for (let req in requests) {
    // check
    console.log(req + ":" + requests[req]);
    if (requests[req] === "") {
      alert(req.toUpperCase() + "は必須です．");
      return false;
    }
  }
  return true;
}

// string format
(function () {
  if (!String.prototype.format) {
    String.prototype.format = function () {
      let args = arguments;
      return this.toString().replace(/{(\d+)}/g, function (match, number) {
        return typeof args[number] !== "undefined" ? args[number] : match;
      });
    };
  }
})();

// startが呼ばれた際の処理：要素消す
function clearElementStart() {
  $("#question_area").empty();
  $("#wiki").empty();
  $(".equation_space").empty();
}

// opが呼ばれた際の処理 -> ギリギリまで消さない
function clearElementOp() {
  // 初期化
  $("#similarity_table").empty();
  $(".equation_space").empty();
  $("#input_text").val("");
}

// startが押されたときの埋め込み (最後に一気に埋め込む)
function addElementStart(response) {
  // response:targets, wiki, eq
  // target1,target2
  let targets = response["targets"];
  // wiki_dict(content, link)
  let wiki = response["wiki"];
  // ここでは初期の式が入るはず
  let eq = "<h5>" + response["eq"] + "</h5>";

  // 問題を作る
  // target1 -> 加減算単語 -> target2
  // 10手以内に類似度ランキングでtarget2が上位5位以内に入るのを目指せ．
  let question =
    "<h2>「" +
    targets["target1"] +
    "」　→　単語を加減算　→　「" +
    targets["target2"] +
    "」</h2>" +
    "<h4>10手以内に類似度ランキングで「" +
    targets["target2"] +
    "」が上位5位以内に入るのを目指せ．</h4>";

  // wiki tableを作成する
  // 1行目
  let wikiTable = '<table border="2"><tr><th colspan="2" class="text-center">Wikipediaヒント</th></tr>';
  // 2行目以降
  for (raw in wiki) {
    // 1列目
    wikiTable += "<tr><td>" + raw + "</td><td>";
    wikiData = wiki[raw];
    // 2列目（2行以上であるのが基本）
    for (column in wikiData["content"]) {
      wikiTable += "<div>" + wikiData["content"][column] + "。</div>";
    }
    // リンク
    wikiTable += '<a href="' + wikiData["link"] + '">Wikipediaリンク（' + raw + "）</a></td></tr>";
  }
  wikiTable += "</table>";

  // 埋め込む
  $("#question_area").append(question);
  $("#wiki").append(wikiTable);
  $(".equation_space").append(eq);
}

// gameの埋め込み
function addElementGame(response) {
  clearElementOp();
  // top12, eq, target_check, word_check,finish
  let top12 = response["top12"];
  let eq = "<h5>" + response["eq"] + "</h5>";
  // target_check
  if (response["target_check"] === "NG") {
    console.log("target_check : ERROR");
    alert("スタートボタンを押してください．");
    $("#question_area").append("スタートボタンを押してください．");
  }
  // word_checkがNGなら再度入力してもらう
  else if (response["word_check"] === "NG") {
    console.log("word_check : ERROR");
    alert("辞書に含まれていない単語です．");
    $(".equation_space").append(eq + "<h3>辞書に含まれていない単語です．別の単語を入力してください．</h3>");
  } else {
    // top12Tableを作成
    // 1行目
    let top12Table = '<table border="2"><tr><th colspan="3">類似度ランキング</th></tr><tr>'; //一つ目だけ<tr>つけておく
    // 2行目以降
    let i = 0;
    for (let name in top12) {
      // 3つごとに改行 -> 4つ目でいじる
      if (i !== 0 && i % 3 === 0) {
        top12Table += "</tr><tr><td>{0}位 {1}（{2}）</td>".format(i + 1, name, top12[name]);
      } else {
        top12Table += "<td>{0}位 {1}（{2}）</td>".format(i + 1, name, top12[name]);
      }
      i++;
    }
    // 最後閉じる
    top12Table += "</tr></table>";

    // 埋め込み
    $("#similarity_table").append(top12Table);
    // クリアなどの条件 -> ボタンを出す
    if (response["finish"] === "finish") {
      // document.getElementById("start_button").value = 'もう一度チャレンジ'
      $("#start_button").text("もう一度チャレンジ");

      // スタートボタンを表示し，それ以外のボタンを非表示
      $("#start_button").css("display", "block");
      $("#input").css("display", "none");
      $("#btn-area").css("display", "none");

      // ユーザからアクセス可能なヒント画面を所定の文に置き換える
      $("#hint").text('<h1 class="m-5 text-center"> 問題が生成されていません．</h1>');

      // 改行
      $(".equation_space").append("<h3>" + response["finish_print"] + "</h3>" + eq);
    } else {
      $(".equation_space").append(eq);
    }
  }
}

function outputError(err) {
  console.log(err);
  alert("Error!");
}

function getRequests(req) {
  let requests = {
    word: $("#input_text").val(),
    op: req,
  };
  console.log(JSON.stringify(requests));
  return requests;
}

// スタートボタンを押された時の振る舞い
function postRequestStart(port) {
  // docker上のポートと別にする場合やポートフォワディング対応
  let url = "http://localhost:{0}/start".format(location.port);

  // 送るものがないので空ファイルをダミーでおくる
  let requests = { dummy: "None" };

  let response = {};

  // 入力条件check
  if (!contentsCheck(requests)) return false;

  let ret = $.ajax({
    url: url,
    type: "POST",
    data: JSON.stringify(requests),
    async: true,
    dataType: "text",
  });
  ret.then(
    (data) => {
      response = JSON.parse(data);
      console.log(response);
      addElementStart(response);
    },
    (err) => {
      outputError(err);
    }
  );

  return 0;
}

// 加減算に関する振る舞い
function postRequest(requests) {
  clearElementOp();

  // docker上のポートと別にする場合やポートフォワディング対応
  url = "http://localhost:{0}/game".format(location.port);

  let response = {};

  // 入力条件check
  if (!contentsCheck(requests)) {
    return false;
  }

  let ret = $.ajax({
    url: url,
    type: "POST",
    data: JSON.stringify(requests),
    async: true,
    dataType: "text",
  });
  ret.then(
    (data) => {
      response = JSON.parse(data);
      console.log(response);
      addElementGame(response);
    },
    (err) => {
      outputError();
    }
  );

  return 0;
}

document.addEventListener("DOMContentLoaded", function () {
  $("#plus").click(function () {
    postRequest(getRequests("plus"));
  });

  $("#minus").click(function () {
    postRequest(getRequests("minus"));
  });

  // スタートが押されると問題生成してそれを埋め込む
  $("#start_button").click(function () {
    clearElementStart();
    // opもここで消す
    clearElementOp();
    // startボタンを消して入力エリアや加減算ボタンを表示する
    $("#start_button").css("display", "none");
    $("#input").css("display", "block");
    $("#btn-area").css("display", "block");
    postRequestStart();
  });
});
