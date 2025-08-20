import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Please set BOT_TOKEN environment variable")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ====== Simple in-memory model ======
class Room:
    def __init__(self, chat_id: int, owner_id: int):
        self.chat_id = chat_id
        self.owner_id = owner_id
        self.players = set()
        self.settings = {
            "round_minutes": 7,
            "spies": 1,
            "lang": "ar",          # default Arabic
            "word_list_key": "default",
        }

rooms = {}  # key: chat_id -> Room

def get_lang(chat_id: int) -> str:
    room = rooms.get(chat_id)
    return room.settings["lang"] if room else "ar"

# ====== Handlers ======
@dp.message_handler(commands=['new'])
async def new_room(message: types.Message):
    chat_id = message.chat.id
    rooms[chat_id] = Room(chat_id=chat_id, owner_id=message.from_user.id)
    await message.answer("تم إنشاء الغرفة! استخدم /join للمشاركة.")

@dp.message_handler(commands=['join'])
async def join_room(message: types.Message):
    chat_id = message.chat.id
    room = rooms.get(chat_id)
    if not room:
        await message.answer("لا توجد غرفة في هذا القروب. استخدم /new أولاً.")
        return
    room.players.add(message.from_user.id)
    if get_lang(chat_id) == "ar":
        await message.answer("تم انضمامك إلى اللعبة! ✅")
    else:
        await message.answer("You’ve joined the game! ✅")

@dp.message_handler(commands=['startgame'])
async def start_game(message: types.Message):
    chat_id = message.chat.id
    room = rooms.get(chat_id)
    if not room:
        await message.answer("لا توجد غرفة. استخدم /new أولاً.")
        return
    if len(room.players) < 4:
        if room.settings["lang"] == "ar":
            await message.answer("عدد اللاعبين غير كافٍ لبدء اللعبة! (الحد الأدنى 4)")
        else:
            await message.answer("Not enough players to start! (min 4)")
        return
    # هنا منطق البدء الحقيقي لاحقًا (توزيع الأدوار/كلمة سرية/DM...)
    if room.settings["lang"] == "ar":
        await message.answer("بدأت اللعبة! ⏳")
    else:
        await message.answer("Game started! ⏳")

@dp.message_handler(commands=['end'])
async def end_game(message: types.Message):
    chat_id = message.chat.id
    if chat_id in rooms:
        del rooms[chat_id]
        await message.answer("انتهت اللعبة وتم حذف الغرفة.")
    else:
        await message.answer("لا توجد لعبة نشطة.")

@dp.message_handler(commands=['lang'])
async def change_language(message: types.Message):
    chat_id = message.chat.id
    room = rooms.get(chat_id)
    if not room:
        await message.answer("لا توجد غرفة. استخدم /new أولاً.")
        return
    room.settings["lang"] = "en" if room.settings["lang"] == "ar" else "ar"
    if room.settings["lang"] == "en":
        await message.answer("Language switched to English.")
    else:
        await message.answer("تم تغيير اللغة إلى العربية.")

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    lang = get_lang(message.chat.id)
    if lang == "ar":
        help_text = (
            "الأوامر المتاحة:\n"
            "/new - إنشاء غرفة جديدة\n"
            "/join - الانضمام إلى اللعبة\n"
            "/startgame - بدء اللعبة\n"
            "/end - إنهاء اللعبة\n"
            "/lang - تبديل اللغة بين العربية والإنجليزية\n"
        )
    else:
        help_text = (
            "Commands:\n"
            "/new - Create a new room\n"
            "/join - Join the current room\n"
            "/startgame - Start the game\n"
            "/end - End the current game\n"
            "/lang - Toggle language (AR/EN)\n"
        )
    await message.answer(help_text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
