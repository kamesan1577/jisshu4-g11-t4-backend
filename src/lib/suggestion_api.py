from . import mk_func_kakite, chat_api


def is_required_moderation(prompt: str):
    """文字列を受け取り、修正が必要かどうかを判定する

    Args:
        prompt (str): 判定対象の文字列
    Returns:
        bool: 修正が必要ならTrue、必要でなければFalse
    """
    score = chat_api.safety_scoring(prompt)
    if score["results"][0]["flagged"]:
        flag = True
    else:
        flag = False
    return flag


def get_hidden_words(prompt: str):
    """文字列を受け取り、修正対象の単語のリストを返す

    Args:
        prompt (str): 判定対象の文字列
    Returns:
        list: 修正対象の単語のリスト
    """

    suggestions = mk_func_kakite.ketaiso_kaku(prompt, dir=False)
    return suggestions
