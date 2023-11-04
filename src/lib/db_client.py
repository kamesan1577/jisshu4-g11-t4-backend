import gspread
import os
from .models import Sheet
from dotenv import load_dotenv


class DBClient:
    # FIXME 立ち上がりに数秒かかる
    def __init__(self, SHEET_KEY: str):
        gc = gspread.service_account(filename="src/secret/sheet-secret.json")
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
            row_data = list(data.model_dump().values())
            worksheet.append_row(row_data)
            return
        except gspread.exceptions.WorksheetNotFound:
            raise self.SheetNotFoundError(f"シート名: {sheet_name} が見つかりませんでした。")


# import時にインスタンスを作成する
load_dotenv(verbose=True)
SHEET_KEY = os.environ.get("SHEET_KEY")
db_instance = DBClient(SHEET_KEY)
