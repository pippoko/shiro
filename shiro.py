from flask import Flask
from threading import Thread
import os
print("===== SHIRO V2 起動 =====")
from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.ext import commands

from sheets import SheetsManager
from odai import get_random_odai
from birthday import BirthdayManager
from discord.ext import tasks


# ==========================
# 環境変数
# ==========================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CSV_URL = os.getenv("SHEET_CSV_URL")
BIRTHDAY_CHANNEL_ID = int(
    os.getenv("BIRTHDAY_CHANNEL_ID")
)

# ==========================
# Bot設定
# ==========================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

sheets = SheetsManager(CSV_URL)

birthday_manager = BirthdayManager(
    sheets,
    BIRTHDAY_CHANNEL_ID
)

@tasks.loop(minutes=10)
async def check_birthdays():
    await birthday_manager.check_birthdays(bot)

# ==========================
# Flaskサーバー
# ==========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Shiro is running!"


def run_web():
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )


# ==========================
# 起動処理
# ==========================

@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync()

        print(
            f"スラッシュコマンド同期完了 "
            f"({len(synced)}件)"
        )

    except Exception as e:
        print(f"同期失敗: {e}")
        

    print(f"{bot.user} でログインしました")


# ==========================
# /character
# ==========================

@bot.tree.command(
    name="character",
    description="キャラクターをランダム表示します"
)
@app_commands.describe(
    creation="創作名で絞り込み",
    gender="性別で絞り込み",
    birth_month="誕生月で絞り込み"
)
async def character_command(
    interaction: discord.Interaction,
    creation: str | None = None,
    gender: str | None = None,
    birth_month: int | None = None
):

    await interaction.response.defer()

    character = await sheets.get_random_character(
        creation=creation,
        gender=gender,
        birth_month=birth_month
    )

    if not character:

        await interaction.followup.send(
            "条件に一致するキャラクターが見つかりませんでした。"
        )
        return

    name = character.get("名前", "不明")
    emoji = character.get("絵文字", "")
    intro = character.get(
        "簡単キャラ紹介",
        ""
    ).strip()

    if not intro:
        intro = "まだ紹介文が登録されていません。"

    creation_name = character.get("創作", "不明")
    gender_name = character.get("性別", "不明")

    birthday = character.get("誕生日", "")

    image_quote = character.get(
        "イメージセリフ",
        ""
    ).strip()

    page_url = character.get(
        "個別ページ",
        ""
    ).strip()

    embed = discord.Embed(
        title=f"{emoji} {name}",
        description=intro,
        color=discord.Color.blue()
    )

    embed.add_field(
        name="創作",
        value=creation_name or "未設定",
        inline=True
    )

    embed.add_field(
        name="性別",
        value=gender_name or "未設定",
        inline=True
    )

    embed.add_field(
        name="誕生日",
        value=birthday or "未設定",
        inline=True
    )

    if image_quote:
        embed.add_field(
            name="イメージセリフ",
            value=image_quote,
            inline=False
        )

    if page_url:
        embed.add_field(
            name="個別ページ",
            value=page_url,
            inline=False
        )

    embed.set_footer(
        text="Shiro Character Database"
    )

    await interaction.followup.send(
        embed=embed
    )


# ==========================
# /odai
# ==========================

@bot.tree.command(
    name="odai",
    description="お絵描きお題を表示します"
)
async def odai_command(
    interaction: discord.Interaction
):

    odai = get_random_odai()

    embed = discord.Embed(
        title="🎨 今日のお題",
        description=f"**{odai}**",
        color=discord.Color.green()
    )

    embed.set_footer(
        text="Shiro Drawing Prompt"
    )

    await interaction.response.send_message(
        embed=embed
    )


# ==========================
# 起動
# ==========================

Thread(
    target=run_web,
    daemon=True
).start()

bot.run(TOKEN)