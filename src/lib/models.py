from pydantic import BaseModel, validator, field_validator
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
    original_text_num: int = 0
    hidden_texts: list[str]
    hidden_texts_num: int = 0

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


class Moderations(BaseModel):
    response: str


class IsNotSafe(BaseModel):
    is_required_moderation: bool


class SafetyLevel(BaseModel):
    post: str
    level: int


class TimeLineSafety(BaseModel):
    response: list[SafetyLevel]
    index: list[int] = []

    @validator("index", pre=True, always=True)
    def set_index(cls, v, values):
        if "response" in values:
            return list(range(len(values["response"])))
        return v


# 修正のリクエスト
class ModerationsRequest(BaseModel):
    prompt: Union[str, list[str]]
    user_id: str
    model: str = "gpt-3.5-turbo-1106"
    response_language: str = "日本語"


# 修正提案のリクエスト
class SuggestionsRequest(BaseModel):
    prompt: str
    user_id: str


# 提案受け入れ記録のリクエスト
class IsAcceptedSuggestionRequest(HiddenChars):
    is_accepted: bool
    is_edited_by_user: bool = False


# タイムラインの投稿修正リクエスト
class TimeLineRequest(BaseModel):
    prompts: list[str]
    index: list[int] = []

    @validator("index", pre=True, always=True)
    def set_index(cls, v, values):
        if "prompts" in values:
            return list(range(len(values["prompts"])))
        return v


# ログのテンプレート
class BaseLog(BaseModel):
    user_id: str
    post_id: str
    log_type: str


# 投稿修正リクエストのログ
class ModerationsRequestLog(BaseLog, ModerationsRequest):
    log_type: str = "moderation_request"


# 投稿修正レスポンスのログ
class ModerationsResponseLog(
    BaseLog,
):
    log_type: str = "moderation_response"
    prompt: str
    response: str


# 提案修正のログ
class SuggestionsLog(BaseLog, HiddenChars):
    log_type: str = "suggestion"
    hidden_texts_str: str = ""

    @field_validator("hidden_texts_str", mode="before")
    def validate_hidden_texts_str(cls, v, values):
        if "hidden_texts" in values:
            return ",".join(values["hidden_texts"])
        return v


# 安全性判定のログ
class SafetyJudgementLog(BaseLog, SuggestionsRequest):
    log_type: str = "safety"


# 提案受け入れ記録のログ
class IsAcceptedSuggestionLog(BaseLog, IsAcceptedSuggestionRequest):
    log_type: str = "is_accepted_suggestion"


# スプレッドシートのデータモデル
class Sheet(BaseModel):
    word: str
    ruby: str
    alternative: str = ""
    note: str = ""
