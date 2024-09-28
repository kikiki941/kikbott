import logging
import os
from telebot.types import Message
from telebot.apihelper import ApiTelegramException
from openpyxl import load_workbook
from io import BytesIO
from bot import bot
from message import *
from helpers import *
from state import HitungGambarState  # New state for image handling

@bot.message_handler(commands='get_images')
async def get_images_command(message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, HitungGambarState.waiting_for_file, message.chat.id)
        await bot.reply_to(message, "Silakan kirim file Excel (.xlsx) yang berisi gambar.")
    except Exception as e:
        logging.error("Error: ", exc_info=True)

@bot.message_handler(state=HitungGambarState.waiting_for_file, content_types=['document'])
async def excel_get(message: Message):
    try:
        if not message.document.file_name.endswith(".xlsx"):
            return await bot.send_message(message.chat.id, "Kirim file Excel (.xlsx) yang valid.")
        
        file = await bot.get_file(message.document.file_id)
        filename = f"files/{message.document.file_name}"
        
        downloaded_file = await bot.download_file(file.file_path)
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        images_sent = await send_images_from_excel(filename, message.chat.id)

        if images_sent == 0:
            await bot.send_message(message.chat.id, "Tidak ada gambar ditemukan dalam file Excel.")
        else:
            await bot.send_message(message.chat.id, f"{images_sent} gambar berhasil dikirim.")

        os.remove(filename)  # Remove the Excel file after processing

        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("Error: ", exc_info=True)

@bot.message_handler(state=HitungGambarState.waiting_for_file, commands=['cancel'])
async def cancel_process(message: Message):
    try:
        await bot.send_message(message.chat.id, "Proses dibatalkan.")
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("Error: ", exc_info=True)
