from . import mk_func_kakite

# def is_required_moderation(prompt: str):
#     """文字列を受け取り、修正が必要かどうかを判定する

#     Args:
#         prompt (str): 判定対象の文字列
#     Returns:
#         bool: 修正が必要ならTrue、必要でなければFalse
#     """

#     flag = False
#     return flag


def get_hidden_words(prompt: str):
    """文字列を受け取り、修正対象の単語のリストを返す

    Args:
        prompt (str): 判定対象の文字列
    Returns:
        list: 修正対象の単語のリスト
    """

    suggestions = mk_func_kakite.ketaiso_kaku(prompt, dir=False)
    return suggestions
