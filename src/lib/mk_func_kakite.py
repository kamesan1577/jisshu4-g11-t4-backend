# from janome.tokenizer import Tokenizer
import re
import json
import csv
import os
from dotenv import load_dotenv
from httpx import request

# import pandas as pd

# t = Tokenizer()
csv_in = "src/csv/kinshi.csv"
with open(csv_in, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    moral_foundation_dic = [row for row in reader]
load_dotenv(verbose=True)
CLIENT_ID = os.environ.get("YAHOO_CLIENT_ID")
BASE_URL = "https://jlp.yahooapis.jp/MAService/V2/parse"
# df = pd.read_csv(csv_in, sep=",", skiprows=0, header=0)


def ketaiso_kaku(text: str, dir: bool = True):
    if dir:
        text_dir = text
        text_kakite = open(text_dir, encoding="utf8").read()
    else:
        text_kakite = text

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Yahoo AppID: {}".format(CLIENT_ID),
    }

    param_dic = {
        "id": "1234-1",
        "jsonrpc": "2.0",
        "method": "jlp.maservice.parse",
        "params": {"q": text_kakite},
    }
    params = json.dumps(param_dic).encode("utf-8")
    response = request("POST", BASE_URL, headers=headers, data=params).json()
    response_dic = response["result"]["tokens"]

    result = []

    for token in response_dic:
        if "命令形" in token:
            result.append(token[0])
    for item in moral_foundation_dic:
        if re.search(item[0], text_kakite) and item[0] not in result:
            result.append(str(item[0]))
    return result


# def ketaiso_kaku(text: str, dir: bool = True):
#     # 道徳基盤辞書
#     result = []
#     if dir:
#         text_dir = text
#         text_kakite = open(text_dir, encoding="utf8").read()
#     else:
#         text_kakite = text
#     n = -1
#     for tokens in t.tokenize(text_kakite):
#         if "命令" in tokens.infl_form:
#             result.append(tokens.surface)
#     for item in df["見出し"]:
#         n += 1
#         if re.search(df.iloc[n, 0], text_kakite):
#             result.append(str(df.iloc[n, 0]))
#     return result


if __name__ == "__main__":
    print(ketaiso_kaku("src/sample_text/tweet.txt"))
    # 　呼び出し
