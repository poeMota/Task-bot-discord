import disnake
from disnake.ext import commands

from src.Logger import *
from src.Classes import Member
from src.Config import *
from src.HelpManager import HelpManager
from src.Localization import LocalizationManager
from .page import Page


loc = LocalizationManager()

def add_shop_commands(bot: commands.InteractionBot):
    helper = HelpManager()

    disabled_commands = from_toml("config", "Commands")
    if not disabled_commands: disabled_commands = {}

    if "shop" not in disabled_commands or disabled_commands["shop"]:
        @bot.slash_command(
            name=loc.GetString("shop-command-name"),
            description=loc.GetString("shop-command-description")
        )
        async def shop(inter: disnake.CommandInteraction):
            Member(inter.author).currentMagazinePage = 0
            await page(inter)
        helper.AddCommand(shop)


        @bot.listen("on_button_click")
        async def update_page(inter: disnake.CommandInteraction):
            if inter.component.custom_id not in ["previous", "buy", "next"]:
                return

            member = Member(inter.author)
            magazine = Magazine(current_page=member.currentMagazinePage, inter=inter)

            if inter.component.custom_id == "next":
                magazine.current_page += 1
            elif inter.component.custom_id == "previous":
                magazine.current_page -= 1
            elif inter.component.custom_id == "buy":
                await magazine.pages[magazine.current_page].buy(inter)

            if magazine.current_page > len(magazine.pages) - 1:
                magazine.current_page = 0
            elif magazine.current_page < 0:
                magazine.current_page = len(magazine.pages) - 1

            member.currentMagazinePage = magazine.current_page
            await page(inter, edit=True)


async def page(
        inter: disnake.CommandInteraction,
        edit=False
    ):
    embed = disnake.Embed(
        title=loc.GetString("shop-embed-title"),
        description=loc.GetString("shop-embed-description"),
        color=0xf1c40f,
        type="rich"
    )
    magazine = Magazine(current_page=Member(inter.author).currentMagazinePage, inter=inter)

    if not magazine.pages:
        await inter.response.send_message(loc.GetString("shop-no-pages-response"))
        return

    embed.add_field(name=loc.GetString("shop-embed-item", num=magazine.current_page + 1), value=magazine.pages[magazine.current_page].name, inline=False)
    embed.add_field(name=loc.GetString("shop-embed-description-field"), value=magazine.pages[magazine.current_page].description, inline=False)
    embed.add_field(name=loc.GetString("shop-embed-price"), value=f"```{magazine.pages[magazine.current_page].price}```", inline=True)
    embed.add_field(name=loc.GetString("shop-embed-page"), value="```{0}/{1}```".format(magazine.current_page + 1, len(magazine.pages)), inline=True)
    embed.add_field(name=loc.GetString("shop-embed-balance"), value="```{0}```".format(Member(inter.author).score), inline=True)

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
    def __init__(self, current_page, inter: disnake.CommandInteraction):
        replacements = yaml_read("magazine_replacements")
        data = yaml_read("magazine")

        if data:
            self.pages = [Page(inter, proto, replacements) for proto in data]
            self.pages = [page for page in self.pages if page.isAccess(inter.author)]
        else:
            self.pages = []

        self.current_page = current_page
        self.inter = inter

