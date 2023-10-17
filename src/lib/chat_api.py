from . import models
import openai
import logging
import json
from fastapi import HTTPException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
                        あなたはTwitterの投稿を検閲する拡張機能です。
                        ユーザーの入力テキストを形態素ごとに分割し、誹謗中傷や暴言を検出し、それを以下に示す出力例に倣い適切な表現に修正してください。文の意味やニュアンスを保持しつつ、攻撃的な言葉や表現を和らげるような形に変換してください。
                        不適切な言葉が含まれている場合でも、文の意味が伝わるように修正してください。
                        もし不適切な表現が含まれていない場合は、変換を行わずにそのまま返答してください。
                        返答には変換結果のみを含んでください。

                        変換を行う例:
                            入力:
                                [人名]普通に[動詞]してるの頭悪いよね
                            出力:
                                [人名]普通に[動詞]してるの独創的だよね

                            入力:
                                殺すぞ
                            出力:
                                やめてよ

                            入力:
                                あなたを殺害します
                            出力:
                                やめてくれませんか

                            入力:
                                お前が死んだら世界は平和になるよ
                            出力:
                                お前のおかげで世界はいつも面白いよ

                            入力:
                                死ね死ね死ね死ね死ね死ね
                            出力:
                                ちょっと落ち着くのに時間をくれ

                            入力:
                                [人名]ブスすぎて草
                                そんなんだから彼氏できないんだよ
                            出力:
                                [人名]を見てると、自分も頑張らないとって思うよね

                        変換を行わない例:
                            入力:
                                おはようございます
                            出力:
                                おはようございます

                            入力:
                                バカおもろいんだけどｗｗｗｗ
                            出力:
                                バカおもろいんだけどｗｗｗｗ

                            入力:
                                マジ尊い…死ぬ…
                            出力:
                                マジ尊い…死ぬ…
        """,
        }
        user_prompt = [{"role": "user", "content": prompt}]
    else:
        system_prompt = {
            "role": "system",
            "content": f"""
                    {response_language}で返答してください。
                    あなたはTwitterの投稿を検閲する拡張機能です。
                    ユーザーの入力テキストを形態素ごとに分割し、誹謗中傷や暴言を検出し、それを以下に示す出力例に倣い適切な表現に修正してください。文の意味やニュアンスを保持しつつ、攻撃的な言葉や表現を和らげるような形に変換してください。
                    不適切な言葉が含まれている場合でも、文の意味が伝わるように修正してください。
                    もし不適切な表現が含まれていない場合は、変換を行わずにそのまま返答してください。
                    複数のプロンプトが入力された場合、最初に入力されたプロンプトを親ツイートとしたスレッドとして扱います。
                    最後に入力されたプロンプトが現在入力中のツイートです。
                    返答には入力中のツイートに対する変換結果のみを含んでください。

                    変換を行う例:
                        入力:
                            [人名]普通に[動詞]してるの頭悪いよね
                        出力:
                            [人名]普通に[動詞]してるの独創的だよね

                        入力:
                            殺すぞ
                        出力:
                            やめてよ

                        入力:
                            あなたを殺害します
                        出力:
                            やめてくれませんか

                        入力:
                            お前が死んだら世界は平和になるよ
                        出力:
                            お前のおかげで世界はいつも面白いよ

                        入力:
                            死ね死ね死ね死ね死ね死ね
                        出力:
                            ちょっと落ち着くのに時間をくれ

                        入力:
                            [人名]ブスすぎて草
                            そんなんだから彼氏できないんだよ
                        出力:
                            [人名]を見てると、自分も頑張らないとって思うよね

                        入力:
                            ツイート1:
                                今日は[人名]と[場所]で[動詞]してきたよ！
                            返信1:
                                [人名]は[形容詞]だから関わらないほうがいいよ
                        出力:
                            [人名]と[場所]で[動詞]してきたんだね！

                        入力:
                            ツイート1:
                                死ねよお前マジで殺すぞ
                            返信1:
                                てめぇが死ねよクソガキ
                        出力:
                            あなたも落ちついてください

                    変換を行わない例:
                        入力:
                            おはようございます
                        出力:
                            おはようございます

                        入力:
                            バカおもろいんだけどｗｗｗｗ
                        出力:
                            バカおもろいんだけどｗｗｗｗ

                        入力:
                            マジ尊い…死ぬ…
                        出力:
                            マジ尊い…死ぬ…

                        入力:
                            ツイート1:
                                今日は[人名]と[場所]で[動詞]してきたよ！
                            返信1:
                                いいね！
                        出力:
                            いいね！

                        入力:
                            ツイート1:
                                死ねよお前マジで殺すぞ
                            返信1:
                                落ち着いてください
                        出力:
                            落ち着いてください
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
