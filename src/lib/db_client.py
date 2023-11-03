import gspread
import os
import json
from dotenv import load_dotenv


class DBClient:
    # FIXME 立ち上がりに数秒かかる
    def __init__(self, SHEET_KEY: str):
        gc = gspread.service_account(filename="src/secret/sheet-secret.json")
        self.sheet = gc.open_by_key(SHEET_KEY)
        print("init: ", self.sheet.title)

    def fetch_sheet_value(self, sheet_name: str):
        """
        Args:
            sheet_name (str): シート名

        Returns:
            list: シートの全データをリストで返す
        """
        worksheet = self.sheet.worksheet(sheet_name)
        return worksheet.get_all_values()

    # TODO: 動くか不明
    def add_sheet_value(self, sheet_name: str, value: list):
        """
        Args:
            sheet_name (str): シート名
            value (list): 追加する値

        """
        worksheet = self.sheet.worksheet(sheet_name)
        worksheet.append_row(value)
        return


# import時にインスタンスを作成する
load_dotenv(verbose=True)
SHEET_KEY = os.environ.get("SHEET_KEY")
db_instance = DBClient(SHEET_KEY)
