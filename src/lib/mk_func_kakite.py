from janome.tokenizer import Tokenizer
import re
import pandas as pd

t = Tokenizer()
csv_in = "src/csv/kinshi.csv"
df = pd.read_csv(csv_in, sep=",", skiprows=0, header=0)


def ketaiso_kaku(text: str, dir: bool = True):
    # 道徳基盤辞書
    result = []
    if dir:
        text_dir = text
        text_kakite = open(text_dir, encoding="utf8").read()
    else:
        text_kakite = text
    n = -1
    for tokens in t.tokenize(text_kakite):
        if "命令" in tokens.infl_form:
            result.append(tokens.surface)
    for item in df["見出し"]:
        n += 1
        if re.search(df.iloc[n, 0], text_kakite):
            result.append(str(df.iloc[n, 0]))
    return result


if __name__ == "__main__":
    print(ketaiso_kaku("src/sample_text/tweet.txt"))
    # 　呼び出し
