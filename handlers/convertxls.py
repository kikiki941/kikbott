import logging
import os
from re import findall
from asyncio import sleep
from telebot.types import Message
from telebot.apihelper import ApiTelegramException

from bot import bot
from message import *
from helpers import convert_xls_to_xlsx
from state import ConvertXlsState

@bot.message_handler(commands='convertxls')
async def convertxls_command(message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, ConvertXlsState.filename, message.chat.id)
        await bot.reply_to(message, "Silakan kirim file .xls yang akan dikonversi.")
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=ConvertXlsState.filename, content_types=['document'])
async def xls_get(message: Message):
    try:
        if not message.document.file_name.endswith(".xls"):
            return await bot.send_message(message.chat.id, "Kirim file .xls")
        
        file = await bot.get_file(message.document.file_id)
        filename = f"files/{message.document.file_name}"
        
        await bot.set_state(message.from_user.id, ConvertXlsState.name, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['filename'] = filename

        downloaded_file = await bot.download_file(file.file_path)
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        await bot.send_message(message.chat.id, 'File diterima. Silakan masukan nama file .xlsx yang akan dihasilkan:')
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=ConvertXlsState.filename)
async def not_xls(message: Message):
    try:
        await bot.send_message(message.chat.id, 'Kirim file .xls')
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=ConvertXlsState.name)
async def name_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text
            xls_file = data['filename']
            output_name = data['name']

            await bot.send_message(message.chat.id, f'Nama file diatur menjadi: {data["name"]}. Mulai mengonversi file...')
            
            xlsx_file, images = convert_xls_to_xlsx_and_extract_images(xls_file, output_name)

            if xlsx_file:
                await bot.send_document(message.chat.id, open(xlsx_file, 'rb'))
                os.remove(xlsx_file)
                
                # Mengirim gambar
                for img_path in images:
                    await bot.send_photo(message.chat.id, open(img_path, 'rb'))
                    os.remove(img_path)

            os.remove(xls_file)
            await bot.send_message(message.chat.id, "Konversi selesai!")
        
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("error: ", exc_info=True)
