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
    birth_month="誕生月で絞り込み",
    private="自分だけに表示する"
)

async def character_command(
    interaction: discord.Interaction,
    private: bool = False,
    creation: app_commands.Choice[str] | None = None,
    gender: app_commands.Choice[str] | None = None,
    birth_month: app_commands.Choice[int] | None = None
):
    


    await interaction.response.defer(
        ephemeral=private
    )

    creation_value = creation.value if creation else None
    gender_value = gender.value if gender else None
    birth_month_value = birth_month.value if birth_month else None

    character = await sheets.get_random_character(
        creation=creation_value,
        gender=gender_value,
        birth_month=birth_month_value
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
        embed=embed,
        ephemeral=private
    )

@app_commands.choices(
        creation=[
        app_commands.Choice(name="なし", value="なし"),
        app_commands.Choice(name="レガード・オデッセイ", value="レガード・オデッセイ"),
        app_commands.Choice(name="エモーション", value="エモーション"),
        app_commands.Choice(name="バーベナの花束を", value="バーベナの花束を"),
        app_commands.Choice(name="Fake painT", value="Fake painT"),
        app_commands.Choice(name="【企画】ほうかご美術部！", value="【企画】ほうかご美術部！"),
        app_commands.Choice(name="パラソルガール", value="パラソルガール"),
        app_commands.Choice(name="暗影に灯るは", value="暗影に灯るは"),
        app_commands.Choice(name="探索者", value="探索者"),
        app_commands.Choice(name="【企画】ミネアカ", value="【企画】ミネアカ"),
        ],
        
        gender=[
            app_commands.Choice(name="男性", value="男性"),
            app_commands.Choice(name="女性", value="女性"),
            app_commands.Choice(name="無性", value="無性"),
            app_commands.Choice(name="概念なし", value="概念なし")
        ],

        birth_month=[
        app_commands.Choice(name="1月", value=1),
        app_commands.Choice(name="2月", value=2),
        app_commands.Choice(name="3月", value=3),
        app_commands.Choice(name="4月", value=4),
        app_commands.Choice(name="5月", value=5),
        app_commands.Choice(name="6月", value=6),
        app_commands.Choice(name="7月", value=7),
        app_commands.Choice(name="8月", value=8),
        app_commands.Choice(name="9月", value=9),
        app_commands.Choice(name="10月", value=10),
        app_commands.Choice(name="11月", value=11),
        app_commands.Choice(name="12月", value=12),
        ],
)


# ==========================
# /odai
# ==========================

@bot.tree.command(
    name="odai",
    description="お絵描きお題を表示します"
)
async def odai_command(
    interaction: discord.Interaction,
    private: bool = False
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
        embed=embed,
        ephemeral=private
    )


# ==========================
# 起動
# ==========================

Thread(
    target=run_web,
    daemon=True
).start()

bot.run(TOKEN)