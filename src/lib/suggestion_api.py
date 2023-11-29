import re
from . import chat_api


def is_required_moderation(prompt: str) -> bool:
    """文字列を受け取り、修正が必要かどうかを判定する

    Args:
        prompt (str): 判定対象の文字列
    Returns:
        bool: 修正が必要ならTrue、必要でなければFalse
    """
    score = chat_api.safety_scoring(prompt)
    if score.results[0].flagged:
        flag = True
    else:
        flag = False
    return flag

def get_safety_level(prompt: str) -> int:
    """
    文字列を受け取り、その安全性レベルを判定する

    Args:
        prompt (str): 判定対象の文字列
    Returns:
        int: 安全性レベル（三段階、0が一番安全）
    """
    clean_text = _delete_html_tag(prompt)
    #TODO chat_api.pyのget_safety_level()に置き換える
    score = chat_api.safety_scoring(clean_text)
    if score.results[0].flagged:
        return 1
    else:
        return 0

    

# def get_hidden_words(prompt: str):
#     """文字列を受け取り、修正対象の単語のリストを返す

#     Args:
#         prompt (str): 判定対象の文字列
#     Returns:
#         list: 修正対象の単語のリスト
#     """
#     clean_text = _delete_html_tag(prompt)
#     suggestions = morphological.ketaiso(clean_text, is_directry=False)

#     return suggestions


def _delete_html_tag(text: str):
    # FIXME HTMLじゃなくても正規表現に引っかかる可能性がある
    clean_text = re.sub(r"<[^>]+>", " ", text)
    return clean_text
