import openai
import logging
import json
from fastapi import HTTPException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def chat_modelate(prompt, user_id, model, response_language):
    log_data = {
        "user_id": user_id,
        "prompt": prompt,
        "model": model,
        "response_language": response_language,
    }

    logger.info(json.dumps(log_data))  # Logs the data in JSON format
    if type(prompt) != list:
        system_prompt = {
            "role": "system",
            "content": f"""
                        {response_language}で返答してください。
                        あなたはTwitterの投稿を検閲する拡張機能です。
                        ユーザーの入力テキストから誹謗中傷や暴言を検出し、それを適切な表現に修正してください。文の意味やニュアンスを保持しつつ、攻撃的な言葉や表現を和らげるような形に変換してください。
                        不適切な言葉が含まれている場合でも、文の意味が伝わるように修正してください。
                        もし不適切な表現が含まれていない場合は、変換を行わずにそのまま返答してください。
                        返答には変換結果のみを含んでください。
        """,
        }
        user_prompt = [{"role": "user", "content": prompt}]
    else:
        system_prompt = {
            "role": "system",
            "content": f"""
                    {response_language}で返答してください。
                    あなたはTwitterの投稿を検閲する拡張機能です。
                    ユーザーの入力テキストから誹謗中傷や暴言を検出し、それを適切な表現に修正してください。文の意味やニュアンスを保持しつつ、攻撃的な言葉や表現を和らげるような形に変換してください。
                    不適切な言葉が含まれている場合でも、文の意味が伝わるように修正してください。
                    もし不適切な表現が含まれていない場合は、変換を行わずにそのまま返答してください。
                    複数のプロンプトが入力された場合、最初に入力されたプロンプトを親ツイートとしたスレッドとして扱います。
                    最後に入力されたプロンプトが現在入力中のツイートです。
                    返答には入力中のツイートに対する変換結果のみを含んでください。
        """,
        }
        user_prompt = [{"role": "user", "content": p} for p in prompt]
    response = openai.ChatCompletion.create(
        model=model, messages=[system_prompt, *user_prompt]
    )
    try:
        if response.choices:
            response_content = response["choices"][0]["message"]["content"]
            response_log = {
                "user_id": user_id,
                "request_content": user_prompt[-1]["content"],
                "response_content": response_content,
            }
            logger.info(json.dumps(response_log))  # Log the response in JSON format
            return {"response": response_content}
        else:
            error_log = {"user_id": user_id, "error": "ChatGPT API request failed"}
            logger.error(json.dumps(error_log))  # Log the error in JSON format
            raise HTTPException(status_code=500, detail="ChatGPT API request failed")
    except Exception as e:
        error_log = {"user_id": user_id, "error": str(e)}
        logger.error(json.dumps(error_log))
        raise HTTPException(status_code=500, detail="Runtime error")
