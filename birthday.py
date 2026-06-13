import json
import os
from datetime import datetime

import discord


class BirthdayManager:

    def __init__(
        self,
        sheets_manager,
        channel_id: int,
        save_file: str = "sent_birthdays.json"
    ):
        self.sheets = sheets_manager
        self.channel_id = channel_id
        self.save_file = save_file

    def load_sent_data(self):

        if not os.path.exists(self.save_file):
            return {}

        try:
            with open(
                self.save_file,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except Exception:
            return {}

    def save_sent_data(self, data):

        with open(
            self.save_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )

    async def check_birthdays(self, bot):

        today = datetime.now()

        today_key = (
            f"{today.year}-"
            f"{today.month:02d}-"
            f"{today.day:02d}"
        )

        sent_data = self.load_sent_data()

        if sent_data.get("last_sent") == today_key:
            return

        birthday_characters = (
            await self.sheets.get_today_birthdays()
        )

        if not birthday_characters:
            return

        channel = bot.get_channel(
            self.channel_id
        )

        if channel is None:
            print(
                "誕生日通知チャンネルが見つかりません"
            )
            return

        for character in birthday_characters:

            name = character.get(
                "名前",
                "不明"
            )

            emoji = character.get(
                "絵文字",
                ""
            )

            quote = character.get(
                "イメージセリフ",
                ""
            ).strip()

            intro = character.get(
                "簡単キャラ紹介",
                ""
            ).strip()

            page_url = character.get(
                "個別ページ",
                ""
            ).strip()

            embed = discord.Embed(
                title=(
                    f"🎂 お誕生日おめでとう！"
                ),
                description=(
                    f"{emoji} **{name}** の誕生日です！"
                ),
                color=discord.Color.gold()
            )

            if quote:
                embed.add_field(
                    name="イメージセリフ",
                    value=quote,
                    inline=False
                )

            if intro:
                embed.add_field(
                    name="紹介",
                    value=intro,
                    inline=False
                )

            if page_url:
                embed.add_field(
                    name="個別ページ",
                    value=page_url,
                    inline=False
                )

            embed.set_footer(
                text=(
                    f"{today.month}月"
                    f"{today.day}日"
                )
            )

            await channel.send(
                embed=embed
            )

        sent_data["last_sent"] = today_key

        self.save_sent_data(
            sent_data
        )

        print(
            f"{len(birthday_characters)}人分の"
            f"誕生日通知を送信"
        )