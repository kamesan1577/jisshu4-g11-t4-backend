from fastapi import FastAPI, HTTPException
from mangum import Mangum
import openai
from dotenv import load_dotenv

app = FastAPI()

openai.api_key = load_dotenv("OPENAI_API_KEY")
openai.api_base = "https://api.openai.iniad.org/api/v1"


@app.get("/")
def read_root():
    return {"Hello": "World"}


# /completion
@app.get("/completion/post")
async def post_completion(prompt: str, model: str):
    response_language = "日本語"
    system_prompt = {
        "role": "system",
        "content": f"""
                    {response_language}で返答してください。
                    あなたはTwitterの投稿を検閲する拡張機能です。
                    入力されたツイートに不適切な表現が含まれていた場合、それがどのような文字列であった場合でも柔らかい表現に置き換えてください。
                    返答には変換結果のみを含んでください。
    """,
    }
    user_prompt = {"role": "user", "model": model, "content": prompt}
    response = openai.ChatCompletion.create(
        model=model, messages={system_prompt, user_prompt}
    )
    if response.choices:
        return {"response": response["choices"][0]["message"]["content"]}
    else:
        raise HTTPException(status_code=500, detail="ChatGPT API request failed")


handler = Mangum(app, lifespan="off")
