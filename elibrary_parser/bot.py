import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

API_TOKEN = ''

bot = Bot(token=API_TOKEN)


storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    date_from = State()
    date_to = State()
    authors_ids = State()


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await Form.authors_ids.set()
    await message.reply("Данный бот находит общие статьи между авторами на сайте elibrary."
                        "Id автора это последние цифры вида: authorid=*******. "
                        "Просто введите id требуемых автора.")


def get_keyboard():
    buttons = [
        types.InlineKeyboardButton(text="Добавить авторов", callback_data="keyboard1_extra"),
        types.InlineKeyboardButton(text="Найти все публикации", callback_data="keyboard1_all"),
        types.InlineKeyboardButton(text="Задать промежуток", callback_data="keyboard1_Interval"),
        types.InlineKeyboardButton(text="Найти все публикации ПОСЛЕ года", callback_data="keyboard1_After"),
        types.InlineKeyboardButton(text="Найти все публикации ДО года", callback_data="keyboard1_Before")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


# @dp.message_handler(lambda message: message.text.isdigit(), state=Form.authors_ids)


@dp.message_handler(state=Form.authors_ids)
async def cmd_numbers(message: types.Message):
    await message.answer("Что вы хотите сделать?", reply_markup=get_keyboard())


@dp.callback_query_handler(Text(startswith='keyboard1_'))
async def callbacks(call: types.CallbackQuery, message: types.Message, state: FSMContext):
    action = call.data.split("_")[1]
    if action == "extra":
        await call.message.edit_text(f'Окей, добавь еще')
        async with Form.authors_ids as data:
            data['authors_ids'] = message.text
    elif action == "all":
        Form.date_from = 1900
        Form.date_to = 2021
        await call.message.edit_text(f'Ищу все публикаци с 1900 года...Это много?')
    elif action == "Interval":
        await call.message.edit_text(f'Укажите промежуток от...')
        async with Form.date_from as data:
            data['date_to'] = message.text
        await call.message.edit_text(f'...И до')
        async with Form.date_from as data:
            data['date_from'] = message.text
    elif action == "After":
        await call.message.edit_text(f'Поиск начиная от')
        async with Form.date_from as data:
            data['date_from'] = message.text
    elif action == "Before":
        await call.message.edit_text(f'Поиск до')
        async with Form.date_from as data:
            data['date_to'] = message.text

    await call.answer()


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.date_from)
async def process_date_from_invalid(message: types.Message):
    """
    If date is invalid
    """
    return await message.reply('Пожалуйста вводите только числа')


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.date_to)
async def process_date_to_invalid(message: types.Message):
    """
    If date is invalid
    """
    return await message.reply('Пожалуйста вводите только числа')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
