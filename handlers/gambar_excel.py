import logging
import os
from re import findall
from asyncio import sleep
from telebot.types import Message
from telebot.apihelper import ApiTelegramException
from openpyxl import load_workbook
from io import BytesIO

from bot import bot
from message import *
from helpers import convert_xls_to_xlsx
from state import ConvertXlsState

@bot.message_handler(commands='getimages')
async def get_images_command(message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, ConvertXlsState.filename, message.chat.id)
        await bot.reply_to(message, "Silakan kirim file .xls yang akan diproses.")
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

        # Mengonversi .xls ke .xlsx
        xlsx_file = convert_xls_to_xlsx(filename)
        if not xlsx_file:
            return await bot.send_message(message.chat.id, "Gagal mengonversi file.")

        images = extract_images_from_excel(xlsx_file)
        if images:
            for img in images:
                await bot.send_document(message.chat.id, img)
        else:
            await bot.send_message(message.chat.id, "Tidak ada gambar ditemukan dalam file.")

        # Membersihkan file
        os.remove(filename)
        os.remove(xlsx_file)

        await bot.send_message(message.chat.id, "Proses selesai!")
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("error: ", exc_info=True)

def extract_images_from_excel(filename):
    """
    Mengekstrak gambar dari file Excel.
    :param filename: Jalur ke file .xlsx
    :return: Daftar aliran file gambar
    """
    from openpyxl.drawing.image import Image as OpenPyXLImage

    images = []
    
    try:
        workbook = load_workbook(filename)
        for sheet in workbook.worksheets:
            if hasattr(sheet, '_images'):
                for img in sheet._images:
                    if isinstance(img, OpenPyXLImage):
                        img_stream = BytesIO()
                        img.image.save(img_stream, format='PNG')  # Simpan sebagai PNG
                        img_stream.seek(0)
                        images.append(img_stream)

        return images
    except Exception as e:
        logging.error(f"Kesalahan saat mengekstrak gambar: {e}")
        return images

