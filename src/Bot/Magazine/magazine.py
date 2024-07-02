import disnake
from disnake.ext import commands
from disnake import utils

from src.Logger import *
from datetime import timedelta, datetime
from src.Classes import Member


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
        self.pages = [
            Page(
                name= "Стажер+",
                description= "Получить роль стажера+, что даёт доступ стажерам ко всем основным командам для маппинга (загрузка/сохранение карт).",
                price= 7,
                on_buy= [give_role, send],
                access= ["стажер-маппер"],
                not_access= ["+"],
                add_roles= ["+"],
                channel= 1181543849580052490, # Secret channel
                text= f"<@&1181535312304951296>, нужно выдать Стажера+ на песке <@{inter.author.id}>."
            ),
            Page(
                name= "Повышение",
                description= "Устали быть стажером? Хотите получить доступ к мастерской? Тогда вам к нам! Всего за 18 очков вы можете получить своё долгожданное повышение.",
                price= 18,
                on_buy= [give_role, rem_role, send],
                access= ["+"],
                not_access= ["маппер"],
                add_roles= ["маппер"],
                rem_roles= ["стажер-маппер", "+"],
                channel= 1181543849580052490, # Secret channel
                text= f"<@&1181535312304951296>, нужно выдать Маппера на песке <@{inter.author.id}>."
            ),
            Page(
                name= "Мут агоичи",
                description= "Вы можете замутить агоичи на 5 минут всего за 2 очка!",
                price= 2,
                on_buy= [mute, send],
                id= 823598558690934824,
                until= timedelta(minutes=5),
                reason= f"С днём мута, скажи спасибо {inter.author.name}!",
                text= f"С днём мута <@823598558690934824>, скажи спасибо <@{inter.author.id}>!"
            ),
            Page(
                name="Пригласить друга на песок!",
                description="Вы можете пригласить своего друга на песок ||никакого блата||! Человек, которого вы хотите пригласить получит доступ на песок с базовыми правами (агост и спавн).",
                price=20,
                on_buy=[send],
                channel= 1181543849580052490, # Secret channel
                text= f"<@&1181535312304951296>, <@{inter.author.id}> хочет пригласить пупика на песок."
            ),
            Page(
                name="Ревью работы",
                description="Заставить ведущего маппера сделать полный ревью одной вашей работы.\n" + 
                "Ревью будет включать в себя проверку на соблюдение всех стандартов маппинга, указание на все недочёты и советы по улучшению.",
                price=10,
                on_buy= [send],
                channel= 1181543849580052490, # Secret channel
                text= f"<@&1181535312304951296>, работать, <@{inter.author.id}> заказал ревью!"
            ),
            Page(
                name= 'Подписка "Маг"',
                description= "**ВРЕМЕННАЯ АКЦИЯ! Действует пока у моты не закончатся деньги.** \n" +
                             "За свою работу вы можете получить вознаграждение в виде месячной подписки Мага! \n"+
                             "Подписка данного уровня даёт следующие преимущества: \n" +
                             "- 💬 Уникальная роль в Discord \n" +
                             "- 👤 Ещё +5 слотов персонажей \n" +
                             "- 🪮 Доступ к 10 новым причёскам \n" +
                             "- 🤖 Доступ к киберпротезами во внешних чертах персонажа \n" +
                             "- 🔵 Синий цвет ника в OOC \n" +
                             "- 🌈 Уникальная тема призрака \n" +
                             "- 🔑 Вход на заполненый сервер без очереди",
                price= 30,
                on_buy= [send],
                channel= 1181543849580052490, # Log channel
                text= f"<@1046425922200420505> надо раскошелиться на 700 рублей для <@{inter.author.id}>!"
            ),
            Page(
                name= 'Подписка "Синдикат"',
                description= "**ВРЕМЕННАЯ АКЦИЯ! Действует пока у моты не закончатся деньги.** \n" +
                             "За свою работу вы можете получить вознаграждение в виде месячной подписки Синдиката! \n"+
                             "Подписка данного уровня даёт следующие преимущества: \n" +
                             "- 💬 Уникальная роль в Discord \n" +
                             "- 👤 Ещё +5 слотов персонажей \n" +
                             "- 🪮 Доступ к 10 новым причёскам \n" +
                             "- 🤖 Доступ к киберпротезами во внешних чертах персонажа \n" +
                             "- 🔴 Красный цвет ника в OOC \n" +
                             "- 🌸 Уникальная тема призрака \n" +
                             "- 🔑 Вход на заполненый сервер без очереди \n" +
                             "- 😼 Доступ к кошачьим ушкам и хвосту во внешних чертах персонажа \n" +
                             "- 🐺Доступ к расе лис - Вульпканин",
                price= 50,
                on_buy= [send],
                channel= 1181543849580052490, # Log channel
                text= f"<@1046425922200420505> надо раскошелиться на 1000 рублей для <@{inter.author.id}>!"
            )
        ]
        self.current_page = current_page
        self.inter = inter
        self.access_pages()


    def access_pages(self):
        not_access = []
        for page in self.pages:
            access = False
            if "everyone" in page.access: access = True
            for role in self.inter.author.roles:
                if role.name.lower().replace(" ", "") in page.access:
                    access = True
                if role.name.lower().replace(" ", "") in page.not_access: 
                    access = False
                    break
            if access is False: not_access.append(page)

        for page in not_access:
            self.pages.remove(page)


class Page:
    """класс страниц с предложениями в магазине"""
    def __init__(self, name, description: str, price: int, on_buy, access=["@everyone"], not_access=[], **kwargs):
        self.name = name
        self.description = description
        self.price = price
        self.on_buy = on_buy
        self.access = access
        self.not_access = not_access
        self.kwargs = kwargs

    async def buy(self, inter: disnake.CommandInteraction):
        self.inter = inter
        member = Member(inter.author)
        if member.score >= self.price:
            member.change_score(-self.price, False)
            for func in self.on_buy:
                await func(inter= self.inter, kwargs= self.kwargs)
            Logger.medium(inter, f"{inter.author.display_name} совершил покупку **{self.name}**")


async def give_role(inter: disnake.AppCommandInteraction, kwargs):
    for i in kwargs["add_roles"]:
        for role in inter.guild.roles:
            if role.name == i: await inter.author.add_roles(role)


async def rem_role(inter: disnake.AppCommandInteraction, kwargs):
    for i in kwargs["rem_roles"]:
        for role in inter.guild.roles:
            if role.name == i and role in inter.author.roles:
                await inter.author.remove_roles(role)


async def mute(inter: disnake.AppCommandInteraction, kwargs):
    member = utils.get(inter.guild.members, id=kwargs["id"])
    await member.timeout(until=(datetime.now() + kwargs["until"]).astimezone(), reason=kwargs["reason"])


async def send(inter: disnake.AppCommandInteraction, kwargs):
    if "channel" in kwargs:
        channel: disnake.TextChannel = utils.get(inter.guild.channels, id=int(kwargs["channel"]))
        if channel is not None:
            await channel.send(kwargs["text"])
    else: await inter.channel.send(kwargs["text"])