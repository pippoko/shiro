import aiohttp
import csv
import io
import random
from datetime import datetime


class SheetsManager:
    def __init__(self, csv_url: str):
        self.csv_url = csv_url

    async def fetch_characters(self) -> list[dict]:
        """
        Google Sheets(CSV)から全キャラ取得
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(self.csv_url) as response:

                if response.status != 200:
                    raise Exception(
                        f"CSV取得失敗: HTTP {response.status}"
                    )

                text = await response.text()

        reader = csv.DictReader(io.StringIO(text))

        characters = []

        for row in reader:

            # 名前が空なら除外
            if not row.get("名前", "").strip():
                continue

            characters.append(row)

        return characters

    async def get_random_character(
        self,
        creation: str | None = None,
        gender: str | None = None,
        birth_month: int | None = None
    ) -> dict | None:

        characters = await self.fetch_characters()

        filtered = characters

        # 創作フィルター
        if creation:
            filtered = [
                c for c in filtered
                if c.get("創作", "").strip() == creation
            ]

        # 性別フィルター
        if gender:
            filtered = [
                c for c in filtered
                if c.get("性別", "").strip() == gender
            ]

        # 誕生月フィルター
        if birth_month:

            month_filtered = []

            for char in filtered:

                birthday = char.get("誕生日", "").strip()

                if not birthday:
                    continue

                try:
                    month = int(birthday.split("/")[0])

                    if month == birth_month:
                        month_filtered.append(char)

                except (ValueError, IndexError):
                    continue

            filtered = month_filtered

        if not filtered:
            return None

        return random.choice(filtered)

    async def get_today_birthdays(self) -> list[dict]:

        characters = await self.fetch_characters()

        today = datetime.now()

        birthday_characters = []

        for char in characters:

            birthday = char.get("誕生日", "").strip()

            if not birthday:
                continue

            try:

                parts = birthday.split("/")

                if len(parts) == 3:
                    _, month, day = parts

                elif len(parts) == 2:
                    month, day = parts

                else:
                    continue

                month = int(month)
                day = int(day)

                if (
                    month == today.month
                    and day == today.day
                ):
                    birthday_characters.append(char)

            except ValueError:
                continue

        return birthday_characters