import asyncio
from sheets import SheetsManager

CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1I_W7tfPT5tHWQ-KTjatpXZ_V1bVfqeidptcRtn66SuQ/"
    "export?format=csv&gid=17302043"
)

async def main():

    sheets = SheetsManager(CSV_URL)

    characters = await sheets.fetch_characters()

    for char in characters[:20]:
        print(
            char["名前"],
            "|",
            repr(char.get("誕生日"))
        )
    
    birthdays = await sheets.get_today_birthdays()

    for c in birthdays:
        print(c["名前"])

asyncio.run(main())