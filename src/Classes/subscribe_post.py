import asyncio
import disnake

from src.EventManager import Event
from src.Config import *
from src.Logger import *

class SubscribePost:
    def __init__(self, bot: disnake.Client, post: disnake.Message) -> None:
        self.channel: disnake.TextChannel = post.channel
        self.post = post
        self.id = post.id
        self.bot = bot

        self.categories = {} # Categorie name: emoji from givenRoles
        self.givenRoles = {} # Emoji: [role, text]

        self.read_sub_post()


    def read_sub_post(self):
        data = json_read("subscribe_post")

        if self.post.jump_url not in data:
            self.write_sub_post()
            return

        sub_post_data = data[self.post.jump_url]
        for categorie in sub_post_data:
            self.categories[categorie] = []
            for emoji in sub_post_data[categorie]:
                self.categories[categorie].append(emoji)
                self.givenRoles[emoji] = [self.bot.get_role(sub_post_data[categorie][emoji]["role"]),
                                          sub_post_data[categorie][emoji]["text"]]


    def write_sub_post(self):
        data = {}
        for categorie in self.categories:
            if categorie not in data: data[categorie] = {}
            for emoji in self.categories[categorie]:
                data[categorie][emoji] = {
                    "text": self.givenRoles[emoji][1],
                    "role": self.givenRoles[emoji][0].id
                }

        _data = json_read("subscribe_post")
        _data[self.post.jump_url] = data
        json_write("subscribe_post", _data)


    def update(self):
        self.write_sub_post()
        loop = asyncio.get_event_loop()
        loop.create_task(self.post.edit(content="", embed=self.get_embed()))
        for emoji in self.givenRoles:
            loop.create_task(self.post.add_reaction(emoji))
        Logger.debug(f"обновлён пост выдачи ролей {self.post.jump_url}")


    def add_role(self, categorie: str, emoji: str, text: str, role: disnake.role):
        if categorie not in self.categories:
            self.categories[categorie] = []
        self.categories[categorie].append(emoji)
        self.givenRoles[emoji] = [role, text]
        self.update()


    def rem_role(self, categorie: str, emoji: str):
        if categorie not in self.categories: return
        if emoji not in self.categories[categorie]: return
        if emoji not in self.givenRoles: return
        self.categories[categorie].remove(emoji)
        if self.categories[categorie] == []: del self.categories[categorie]
        del self.givenRoles[emoji]
        loop = asyncio.get_event_loop()
        loop.create_task(self.post.clear_reaction(emoji))
        self.update()


    def get_embed(self) -> disnake.Embed:
        embed = disnake.Embed(
            title="Уведомления и роли",
            description="||Выберите эмодзи, чтобы получить соответствующую роль||",
            color=0xf1c40f,
            type="rich"
        )
        for categorie in self.categories:
            text = ""
            for emoji in self.categories[categorie]:
                text = f"{text}{str(emoji)} - {self.givenRoles[emoji][1]}\n"
            embed.add_field(name=categorie, value=text, inline=False)
        return embed

