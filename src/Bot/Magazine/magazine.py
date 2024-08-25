import disnake
from disnake.ext import commands

from src.Logger import *
from src.Classes import Member
from src.Config import *
from .page import Page


def add_magazine(bot: commands.InteractionBot):
    @bot.slash_command(
        name = "магазин",
        description = "Магазин очков."
    )
    async def magazine(inter: disnake.CommandInteraction):
        Member(inter.author).currentMagazinePage = 0
        await page(inter)


    @bot.listen("on_button_click")
    async def update_page(inter: disnake.CommandInteraction):
        if inter.component.custom_id not in ["previous", "buy", "next"]:
            return

        member = Member(inter.author)
        magazine = Magazine(current_page=member.currentMagazinePage, inter=inter)

        if inter.component.custom_id == "next":       magazine.current_page += 1
        elif inter.component.custom_id == "previous": magazine.current_page -= 1
        elif inter.component.custom_id == "buy":      await magazine.pages[magazine.current_page].buy(inter)

        if magazine.current_page > len(magazine.pages)-1: magazine.current_page = 0
        elif magazine.current_page < 0: magazine.current_page = len(magazine.pages)-1

        member.currentMagazinePage = magazine.current_page
        await page(inter, edit=True)


async def page(
        inter: disnake.CommandInteraction,
        edit=False
        ):
    embed = disnake.Embed(
        title="Магазин очков",
        description="Здесь вы можете потратить очки, заработанные работой во благо партии.",
        color=0xf1c40f,
        type="rich"
    )
    magazine = Magazine(current_page=Member(inter.author).currentMagazinePage, inter=inter)

    embed.add_field(name="Лот №{0}".format(magazine.current_page+1), value=magazine.pages[magazine.current_page].name, inline=False)
    embed.add_field(name="Описание", value=magazine.pages[magazine.current_page].description, inline=False)
    embed.add_field(name="Цена", value=f"```{magazine.pages[magazine.current_page].price}```", inline=True)
    embed.add_field(name="Страница", value="```{0}/{1}```".format(magazine.current_page+1, len(magazine.pages)), inline=True)
    embed.add_field(name="Баланс", value="```{0}```".format(Member(inter.author).score), inline=True)

    if edit:
        await inter.response.edit_message(
                embed=embed,
                components=[
                    disnake.ui.Button(emoji="◀", style=disnake.ButtonStyle.secondary, custom_id="previous"),
                    disnake.ui.Button(emoji="🛒", style=disnake.ButtonStyle.success, custom_id="buy"),
                    disnake.ui.Button(emoji="▶", style=disnake.ButtonStyle.secondary, custom_id="next"),
                ]
            )
    else:
        await inter.response.send_message(
                embed=embed,
                components=[
                    disnake.ui.Button(emoji="◀", style=disnake.ButtonStyle.secondary, custom_id="previous"),
                    disnake.ui.Button(emoji="🛒", style=disnake.ButtonStyle.success, custom_id="buy"),
                    disnake.ui.Button(emoji="▶", style=disnake.ButtonStyle.secondary, custom_id="next"),
                ],
                ephemeral=True
            )


class Magazine:
    """Класс магазина"""
    def __init__(self, current_page, inter: disnake.CommandInteraction):
        self.pages = [Page(inter, proto) for proto in yaml_read("magazine")]
        self.pages = [page for page in self.pages if page.isAccess(inter.author)]

        self.current_page = current_page
        self.inter = inter
