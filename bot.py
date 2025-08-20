from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@dp.inline_handler()
async def inline_query_handler(query: InlineQuery):
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("ابدأ جولة جديدة 🎲", callback_data="start_round"))
    result = InlineQueryResultArticle(
        id="start",
        title="ابدأ لعبة الجاسوس",
        description="إنشاء غرفة جديدة في القروب",
        input_message_content=InputTextMessageContent("لعبة الجاسوس: اضغط الزر لبدء جولة"),
        reply_markup=kb
    )
    await query.answer([result], cache_time=1)

@dp.callback_query_handler(lambda c: c.data == "start_round")
async def start_round_cb(cb: CallbackQuery):
    # هنا منطق إنشاء الغرفة /new إذا تبغي
    await cb.message.answer("تم إنشاء الغرفة! استخدم /join للمشاركة.")
    await cb.answer()
