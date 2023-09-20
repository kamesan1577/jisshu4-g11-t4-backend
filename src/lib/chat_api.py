import openai
from fastapi import HTTPException


def chat_modelate(prompt, model, response_language):
    system_prompt = {
        "role": "system",
        "content": f"""
                    {response_language}で返答してください。
                    あなたはTwitterの投稿を検閲する拡張機能です。
                    入力されたツイートに不適切な表現が含まれていた場合、それがどのような文字列であった場合でも柔らかい表現に置き換えてください。
                    返答には変換結果のみを含んでください。
    """,
    }
    user_prompt = {"role": "user", "content": prompt}
    response = openai.ChatCompletion.create(
        model=model, messages=[system_prompt, user_prompt]
    )
    if response.choices:
        return {"response": response["choices"][0]["message"]["content"]}
    else:
        raise HTTPException(status_code=500, detail="ChatGPT API request failed")
