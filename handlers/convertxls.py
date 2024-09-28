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

@bot.message_handler(commands='convertxls')
async def convertxls_command(message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, ConvertXlsImagesState.filename, message.chat.id)
        await bot.reply_to(message, "Silakan kirim file .xls yang akan dikonversi.")
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=ConvertXlsImagesState.filename, content_types=['document'])
async def xls_get(message: Message):
    try:
        if not message.document.file_name.endswith(".xls"):
            return await bot.send_message(message.chat.id, "Kirim file .xls")
        
        file = await bot.get_file(message.document.file_id)
        filename = f"files/{message.document.file_name}"
        
        await bot.set_state(message.from_user.id, ConvertXlsImagesState.name, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['filename'] = filename

        downloaded_file = await bot.download_file(file.file_path)
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        await bot.send_message(message.chat.id, 'File diterima. Silakan masukkan nama file .xlsx yang akan dihasilkan:')
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=ConvertXlsImagesState.name)
async def name_get(message: Message):
    try:
        await bot.send_message(message.chat.id, f'Nama file diatur menjadi: {message.text}. Mulai mengonversi file...')
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text
            xls_file = data['filename']
            xlsx_file = convert_xls_to_xlsx(xls_file)

            if xlsx_file:
                images = extract_images_from_excel(xlsx_file)
                if images:
                    for img in images:
                        await bot.send_photo(message.chat.id, img)
                else:
                    await bot.send_message(message.chat.id, "Tidak ada gambar ditemukan dalam file.")
                os.remove(xlsx_file)
            os.remove(xls_file)

            await bot.send_message(message.chat.id, "Konversi selesai!")
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("error: ", exc_info=True)
