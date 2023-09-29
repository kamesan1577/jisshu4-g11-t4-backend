import openai
import logging
import json
from fastapi import HTTPException


def chat_modelate(prompt, user_id, model, response_language):
    log_data = {
        "user_id": user_id,
        "prompt": prompt,
        "model": model,
        "response_language": response_language,
    }

    logging.info(json.dumps(log_data))  # Logs the data in JSON format

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
    try:
        if response.choices:
            response_content = response["choices"][0]["message"]["content"]
            response_log = {"user_id": user_id, "response_content": response_content}
            logging.info(json.dumps(response_log))  # Log the response in JSON format
            return {"response": response_content}
        else:
            error_log = {"user_id": user_id, "error": "ChatGPT API request failed"}
            logging.error(json.dumps(error_log))  # Log the error in JSON format
            raise HTTPException(status_code=500, detail="ChatGPT API request failed")
    except Exception as e:
        error_log = {"user_id": user_id, "error": str(e)}
        logging.error(json.dumps(error_log))
        raise HTTPException(status_code=500, detail="Runtime error")
