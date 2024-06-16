from .. import loader, utils
from telethon import TelegramClient
from telethon.tl.patched import Message
from telethon.tl.types import ChatBannedRights
from telethon.tl.functions.channels import EditBannedRequest
import os

@loader.tds
class AutoLoadMod(loader.Module):
    """Автозагрузка"""
    strings = {'name': 'AutoLoad'}

    async def client_ready(self, client: TelegramClient, db):
        self.client = client
        self.db = db


    async def addusercmd(self, message: Message):
        """Добавить/исключить юзера из автозагрузки.\nИспользуй: .adduser <@ или реплай> или <list>."""
        users = self.db.get("AutoLoad", "users", [])
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        if not (args or reply):
            return await message.edit("Нет аргументов или реплая")

        if args == "list":
            if not users:
                return await message.edit("Список пуст")

            msg = ""
            for _ in users:
                try:
                    user = await self.client.get_entity(_)
                    msg += f"• <a href=\"tg://user?id={user.id}\">{user.first_name}</a>\n"
                except:
                    users.remove(_)
                    self.db.set("AutoLoad", "users", users)
                    return await message.edit("Произошла ошибка. Повтори команду")

            return await message.edit(f"Список пользователей в автозагрузке:\n\n{msg}")

        try:
            user = await self.client.get_entity(reply.sender_id if reply else args if not args.isnumeric() else int(args))
        except ValueError:
            return await message.edit("Не удалось найти пользователя")

        if user.id not in users:
            users.append(user.id)
            text = "добавлен"
        else:
            users.remove(user.id)
            text = "удален"

        self.db.set("AutoLoad", "users", users)
        await message.edit(f"{user.first_name} был {text} в список автозагрузки")


    async def addchatcmd(self, message: Message):
        """Добавить чат в список для автозагрузки.\nИспользуй: .addchat."""
        chats = self.db.get("AutoLoad", "chats", [])
        args = utils.get_args_raw(message)
        chat_id = message.chat_id

        if args == "list":
            if not chats:
                return await message.edit("Список пуст")

            msg = ""
            for _ in chats:
                try:
                    chat = await self.client.get_entity(_)
                    msg += f"• {chat.title} | {chat.id}\n"
                except:
                    chats.remove(_)
                    self.db.set("AutoLoad", "users", chats)
                    return await message.edit("Произошла ошибка. Повтори команду")

            return await message.edit(f"Список чатов для автозагрузка:\n\n{msg}")

        if message.is_private:
            return await message.edit("Это не чат!")

        if chat_id not in chats:
            chats.append(chat_id)
            text = "добавлен в"
        else:
            chats.remove(chat_id)
            text = "удален из"

        self.db.set("AutoLoad", "chats", chats)
        return await message.edit(f"Этот чат был {text} списка чатов для автозагрузки")


    async def addsaveChatcmd(self, message: Message):
        """NOT WORKED Добавить чат сохранение.\nИспользуй: .addsaveChat."""
        chat = int(self.db.get("AutoLoad", "save", 0))
        args = utils.get_args_raw(message)
        chat_id = message.chat_id
        print(message.chat_id)
        if not chat_id == chat:
            chat = chat_id
            text = "добавлен в"
        else:
            chat = 0
            text = "удален из"

        self.db.set("AutoLoad", "chats", chat)
        return await message.edit(f"Этот чат был {text} для сохранения")


    async def watcher(self, message: Message):
            users = self.db.get("AutoLoad", "users", [])
            chats = self.db.get("AutoLoad", "chats", [])
            user = message.sender if message.sender else None
            chat_id = message.chat_id

            if chat_id not in chats and chat_id not in users:
                return
            if message.media:
                try:
                    save = await self.client.get_entity(-4222209239)
                    path = await self.client.download_media(message)
                    send = await self.client.send_file(save, path, caption=f"Self-destructing photo from {user.first_name if not user == None else "None???"})
                    os.remove(path)
                except Exception as er:
                    await self.client.send_message('me', 'Error: '+str(er))
