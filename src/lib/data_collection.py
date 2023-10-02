# TODO validatorからfield_validatorに移行する
from pydantic import BaseModel, validator


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