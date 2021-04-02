import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from elibrary_parser.Parsers import AuthorParser
from elibrary_parser.utils import find_common_publications

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.environ['API_TOKEN']

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
                        "Просто начните вводить id требуемых автора.")


def get_keyboard():
    buttons = [
        types.InlineKeyboardButton(text="Добавить авторов", callback_data="keyboard1_extra"),
        types.InlineKeyboardButton(text="Задать промежуток", callback_data="keyboard1_Interval"),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.authors_ids)
async def authors_ids_dict(message: types.Message, state: FSMContext):
    await Form.next()
    async with state.proxy() as data:
        data['authors_ids'] = {message.text: 'first_author'}
    await message.answer(f"Что вы хотите сделать?", reply_markup=get_keyboard())


@dp.callback_query_handler(Text(startswith='keyboard1_'))
async def callbacks(call: types.CallbackQuery, state: FSMContext):
    action = call.data.split("_")[1]
    if action == "extra":
        await call.message.edit_text(f'Хорошо, добавим еще')
        await Form.next()
    elif action == "Interval":
        await call.message.edit_text(f'Укажите промежуток от...')
        await Form.date_from.set()

    await call.answer()


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.authors_ids)
async def authors_ids_dict(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['authors_ids']['second_author'] = message.text
    await message.answer(f"Что вы хотите сделать?", reply_markup=get_keyboard())


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.date_from)
async def process_date_from(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date_from'] = message.text
    await message.reply("...И до какого года")
    await Form.date_to.set()


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.date_to)
async def process_date_to(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date_to'] = message.text
        for data['authors_ids'] in data['authors_ids']:
            parser = AuthorParser(
                author_id=data['authors_ids'],
                data_path="C://Users//SZ//PycharmProjects//Parser//data",
                date_from=int(data['date_from']),
                date_to=int(data['date_to'])
            )
            parser.find_publications()  # Загрузка HTML-файлов с публикациями
            parser.parse_publications()  # Извлечение информации из HTML-файлов
            parser.save_publications()  # Сохранение информации в CSV-файл

            path = r"C:/Users/SZ/PycharmProjects/Parser/data/processed/" + \
                (data['authors_ids']) + r'/publications.csv'

            await bot.send_document(message.chat.id, open(path, 'rb'))


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.date_from)
async def process_date_from_invalid(message: types.Message):
    return await message.reply('Пожалуйста вводите только числа')


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.date_to)
async def process_date_to_invalid(message: types.Message):
    return await message.reply('Пожалуйста вводите только числа')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
