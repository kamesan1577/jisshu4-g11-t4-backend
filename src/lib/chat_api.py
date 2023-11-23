from . import models
import os
import openai
import logging
import json
from fastapi import HTTPException

logger = logging.getLogger("PocLog")
logger.setLevel(logging.INFO)

sys_prompt_single_post_path = os.path.join(
    os.path.dirname(__file__), "../prompt/modelation_single.txt"
)
sys_prompt_thread_path = os.path.join(
    os.path.dirname(__file__), "../prompt/modelation_thread.txt"
)

sys_prompt_single_post = open(sys_prompt_single_post_path, "r").read()
sys_prompt_thread = open(sys_prompt_thread_path, "r").read()


def chat_modelate(prompt, user_id, model, response_language):
    log_data = models.ModerationsRequestLog(
        prompt=prompt,
        user_id=user_id,
        model=model,
        response_language=response_language,
        post_id="hoge",
    ).model_dump()
    logger.info(json.dumps(log_data))  # Logs the data in JSON format

    # リストで渡された場合はスレッドとして扱う
    if type(prompt) is not list:
        system_prompt = {
            "role": "system",
            "content": f"""
                        {response_language}で返答してください。
                        {sys_prompt_single_post}
        """,
        }
        user_prompt = [{"role": "user", "content": prompt}]
    else:
        system_prompt = {
            "role": "system",
            "content": f"""
                    {response_language}で返答してください。
                    {sys_prompt_thread}
        """,
        }
        user_prompt = [{"role": "user", "content": p} for p in prompt]
    response = openai.ChatCompletion.create(
        model=model, messages=[system_prompt, *user_prompt]
    )
    try:
        if response.choices:
            response_content = response["choices"][0]["message"]["content"]
            response_log = models.ModerationsResponseLog(
                user_id=user_id,
                post_id="hoge",
                prompt=user_prompt[-1]["content"],
                response=response_content,
            ).model_dump()
            logger.info(json.dumps(response_log))  # Log the response in JSON format
            return response_content
        else:
            error_log = {"user_id": user_id, "error": "ChatGPT API request failed"}
            logger.error(json.dumps(error_log))  # Log the error in JSON format
            raise HTTPException(status_code=500, detail="ChatGPT API request failed")
    except Exception as e:
        error_log = {"user_id": user_id, "error": str(e)}
        logger.error(json.dumps(error_log))
        raise HTTPException(status_code=500, detail="Runtime error")


def safety_scoring(prompt):
    response = openai.Moderation.create(
        input=prompt,
    )
    return response
