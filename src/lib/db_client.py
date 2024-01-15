import json
import gspread
import os
import logging
from .models import Sheet
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
from httpx import request

logging.basicConfig(level=logging.INFO)


# 使わない
class DBClient:
    # FIXME 立ち上がりに数秒かかる
    def __init__(self, SHEET_KEY: str):
        secret = self._get_secret_json(os.environ.get("SHEET_SECRET_NAME"))
        filename = self._save_secret_temp(secret)
        gc = gspread.service_account(filename=filename)
        self.sheet = gc.open_by_key(SHEET_KEY)
        print("init: ", self.sheet.title)

    class SheetNotFoundError(Exception):
        pass

    def fetch_sheet_value(self, sheet_name: str):
        """
        Args:
            sheet_name (str): シート名

        Returns:
            list: シートの全データをリストで返す
        """
        try:
            worksheet = self.sheet.worksheet(sheet_name)
            return worksheet.get_all_values()
        except gspread.exceptions.WorksheetNotFound:
            raise self.SheetNotFoundError(f"シート名: {sheet_name} が見つかりませんでした。")

    def add_sheet_value(self, sheet_name: str, data: Sheet):
        """
        Args:
            sheet_name (str): シート名
            data (Sheet): 追加する値

        """
        try:
            worksheet = self.sheet.worksheet(sheet_name)
            if data.ruby == "":
                data.ruby = self._get_ruby(data.word)
            row_data = list(data.model_dump().values())
            worksheet.append_row(row_data)
            return
        except gspread.exceptions.WorksheetNotFound:
            raise self.SheetNotFoundError(f"シート名: {sheet_name} が見つかりませんでした。")

    def _get_secret_json(self, param_name):
        app_env = os.environ.get("APP_ENV")

        if app_env == "ACTION":
            sheet_secret = os.environ.get("SHEET_SECRET")
            try:
                data = json.loads(sheet_secret)
                return data
            except json.JSONDecodeError as e:
                logging.error("Invalid Json format")
                raise ValueError("Invalid Json format") from e
        else:
            region_name = os.environ.get("AWS_REGION")
            ssm = boto3.client("ssm", region_name=region_name)
            try:
                response = ssm.get_parameter(Name=param_name, WithDecryption=True)
                try:
                    data = json.loads(response["Parameter"]["Value"])
                    return data
                except json.JSONDecodeError as e:
                    logging.error("Invalid Json format")
                    raise ValueError("Invalid Json format") from e
            except ClientError as e:
                logging.error(f"Secret fetching error: {e}")
                raise

    def _save_secret_temp(self, data: dict) -> str:
        filename = "/tmp/sheet-secret.json"

        if not os.path.exists(filename):
            try:
                with open(filename, "w") as f:
                    json.dump(data, f)
                logging.info(f"Secret file {filename} saved successfully.")
            except IOError as e:
                logging.error(f"Failed to write to file: {e}")
                raise
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                raise

        return filename

    def _get_ruby(self, word: str) -> str:
        url = "https://yomi-tan.jp/api/yomi.php"
        query = "?ic=UTF-8&oc=UTF-8&k=h&n=1&t="
        try:
            response = request("GET", f"{url}{query}{word}")
            return response.text
        except Exception as e:
            logging.error(f"Error fetching ruby: {e}")
            raise


# import時にインスタンスを作成する
load_dotenv(verbose=True)
SHEET_KEY = os.environ.get("SHEET_KEY")
db_instance = DBClient(SHEET_KEY)
