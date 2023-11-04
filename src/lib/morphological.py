# from janome.tokenizer import Tokenizer
import re
import json
import os
from .db_client import db_instance
from httpx import request

# csv_in = "src/csv/kinshi.csv"
# with open(csv_in, "r", encoding="utf-8") as f:
#     reader = csv.reader(f)
#     moral_foundation_dic = [row for row in reader]
# print(moral_foundation_dic)
# load_dotenv(verbose=True)

# google spreadsheetから読み込む
WORKSHEET_NAME = "シート1"
moral_foundation_dic = db_instance.fetch_sheet_value(WORKSHEET_NAME)
# print(moral_foundation_dic)

CLIENT_ID = os.environ.get("YAHOO_CLIENT_ID")
BASE_URL = "https://jlp.yahooapis.jp/MAService/V2/parse"


def ketaiso(text: str, dir: bool = True):
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


if __name__ == "__main__":
    print(ketaiso("src/sample_text/tweet.txt"))
    # 　呼び出し
