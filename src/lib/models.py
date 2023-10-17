from pydantic import BaseModel, validator
from typing import Union


# TODO validatorからfield_validatorに移行する
class HiddenChars(BaseModel):
    """隠された文字列の情報を格納するモデル

    Attributes:
        user_id: ユーザーID
        original_text: 修正前のテキスト
        original_text_num: 修正前のテキストの文字数
        hidden_texts: 隠された文字列のリスト
        hidden_texts_num: 隠された文字列の合計文字数
    """

    user_id: str
    original_text: str
    original_text_num: int = None
    hidden_texts: list[str]
    hidden_texts_num: int = None

    @validator("hidden_texts_num", pre=True, always=True)
    def set_hidden_texts_num(cls, v, values):
        if "hidden_texts" in values:
            return sum([len(c) for c in values["hidden_texts"]])
        return v

    @validator("original_text_num", pre=True, always=True)
    def set_original_text_num(cls, v, values):
        if "original_text" in values:
            return len(values["original_text"])
        return v


# 修正のリクエスト
class ModerationsRequest(BaseModel):
    prompt: Union[str, list[str]]
    user_id: str
    model: str = "gpt-3.5-turbo"
    response_language: str = "日本語"


# 修正提案のリクエスト
class SuggestionsRequest(BaseModel):
    prompt: str
    user_id: str


# 提案受け入れ記録のリクエスト
class IsAcceptedSuggestionRequest(HiddenChars):
    is_accepted: bool


# ログのテンプレート
class BaseLog(BaseModel):
    user_id: str
    post_id: str
    log_type: str


# 投稿修正のログ
class ModerationsLog(BaseLog, ModerationsRequest):
    log_type: str = "moderation"


# 提案修正のログ
class SuggestionsLog(BaseLog, HiddenChars):
    log_type: str = "suggestion"


# 提案受け入れ記録のログ
class IsAcceptedSuggestionLog(BaseLog, IsAcceptedSuggestionRequest):
    log_type: str = "is_accepted_suggestion"
