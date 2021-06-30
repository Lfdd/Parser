import logging
import os


from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from elibrary_parser.Parsers import AuthorParser
from elibrary_parser.utils import save_common_publications

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
                        "Просто начните вводить id требуемых авторов через пробел."
                        "Если что-то не так, вы всегда можете написать /restart и начать заново.")


def get_keyboard():
    buttons = [
        types.InlineKeyboardButton(text="Изменить список авторов", callback_data="keyboard1_extra"),
        types.InlineKeyboardButton(text="Задать временной промежуток", callback_data="keyboard1_interval"),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def consists_of_integers(message: types.Message):
    for i in message.text.split():
        try:
            if int(i) and int(i) > 0:
                continue
        except ValueError:
            return False


def is_date_correct(message: types.Message):
    try:
        if len(message.text) == 4 and int(message.text) and int(message.text) > 1900:
            continue
    except ValueError:
        return False


@dp.message_handler(consists_of_integers, state=Form.authors_ids)
async def authors_ids_dict(message: types.Message, state: FSMContext):
    await Form.next()
    print(message.text.split())
    
    async with state.proxy() as data:
        data['authors_ids'] = (message.text.split())
        
    await message.answer("Что вы хотите сделать?", reply_markup=get_keyboard())


@dp.callback_query_handler(Text(startswith='keyboard1_'))
async def callbacks(call: types.CallbackQuery):
    action = call.data.split("_")[1]
    
    if action == "extra":
        await call.message.edit_text('Хорошо, введите новые id авторов через пробел')
        await Form.authors_ids.set()
        
    elif action == "interval":
        await call.message.edit_text('Укажите годы (первое значение) от...')
        await Form.date_from.set()
        
    await call.answer()


@dp.message_handler(is_date, state=Form.date_from)
async def process_date_from(message: types.Message, state: FSMContext):
    
    async with state.proxy() as data:
        data['date_from'] = message.text
        
    await message.reply("...И до какого года (крайнее значение)")
    await Form.date_to.set()


@dp.message_handler(is_date, state=Form.date_to)
async def process_date_to(message: types.Message, state: FSMContext):
    
    async with state.proxy() as data:
        data['date_to'] = message.text
        
        for data['authors_ids'] in data['authors_ids']:
            print(len(data['authors_ids']))
            parser = AuthorParser(
                author_id=data['authors_ids'],
                data_path="PycharmProjects//Parser//data",
                date_from=int(data['date_from']),
                date_to=int(data['date_to'])
            )
            parser.find_publications()  # Загрузка HTML-файлов с публикациями
            parser.parse_publications()  # Извлечение информации из HTML-файлов
            parser.save_publications()  # Сохранение информации в CSV-файл

            path = r"PycharmProjects/Parser/data/processed/" + \
                (data['authors_ids']) + '/' + (data['authors_ids']) + r'_publications.csv'

            with open(path, "rb") as f:
                await bot.send_document(message.chat.id, f)

        if len((data['authors_ids']).split()) > 1:
            #await message.reply("Ухх, я запустился! А должен был?")

            path_common = r"/Parser/data/common_publications/" + \
                (data['date_from']) + '-' + (data['date_to']) + r'_publications.csv'

            data_path = "PycharmProjects//Parser//data"
            publications = [set(parser.publications)]
            save_common_publications(data_path=data_path, date_from=int(data['date_from']),
                                     date_to=int(data['date_to']), publications=publications)
            
            with open(path, "rb") as f:
                await bot.send_document(message.chat.id, f)
            
            await message.answer("Общие")
        else:
            await message.answer('Спасибо, что воспользовались нашим ботом!')



@dp.message_handler(lambda message: not consists_of_integers(message), state=Form.authors_ids)
async def process_authors_id_invalid(message: types.Message):
    return await message.reply('Пожалуйста вводите только положительные целые числа')


@dp.message_handler(lambda message: not is_date(message), state=Form.date_from)
async def process_date_from_invalid(message: types.Message):
    return await message.reply('Пожалуйста вводите только даты формата (2020)')


@dp.message_handler(lambda message: not is_date(message), state=Form.date_to)
async def process_date_to_invalid(message: types.Message):
    return await message.reply('Пожалуйста вводите только даты формата (2020)')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
