import logging
import os
from re import findall
from asyncio import sleep
from telebot.types import Message
from telebot.apihelper import ApiTelegramException

from bot import bot
from message import *
from helpers import convert_xls_to_xlsx, extract_images_from_excel
from state import ConvertXlsImagesState

from bot import bot
from helpers import convert_xls_to_xlsx, extract_images_from_xlsx
import os

@bot.message_handler(commands='extract_images')
async def extract_images_command(message):
    try:
        await bot.send_message(message.chat.id, "Silakan kirim file .xls yang berisi gambar.")
        await bot.set_state(message.from_user.id, ConvertXlsState.filename, message.chat.id)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=ConvertXlsState.filename, content_types=['document'])
async def xls_get(message: Message):
    try:
        if not message.document.file_name.endswith(".xls"):
            return await bot.send_message(message.chat.id, "Kirim file .xls")

        file = await bot.get_file(message.document.file_id)
        filename = f"files/{message.document.file_name}"

        downloaded_file = await bot.download_file(file.file_path)
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        xlsx_file = convert_xls_to_xlsx(filename)
        if xlsx_file:
            images = extract_images_from_xlsx(xlsx_file)
            if images:
                for img in images:
                    await bot.send_photo(message.chat.id, img)
            else:
                await bot.send_message(message.chat.id, "Tidak ada gambar yang ditemukan.")
        else:
            await bot.send_message(message.chat.id, "Konversi file gagal.")

        os.remove(filename)
        if xlsx_file:
            os.remove(xlsx_file)
    except Exception as e:
        logging.error("error: ", exc_info=True)
