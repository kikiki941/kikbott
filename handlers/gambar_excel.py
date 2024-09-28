import logging
import os
from telebot.types import Message
from telebot.apihelper import ApiTelegramException
from bot import bot
from state import HitungGambarState
from helpers import extract_images_from_excel

@bot.message_handler(commands='get_images')
async def get_images_command(message: Message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, HitungGambarState.waiting_for_file, message.chat.id)
        await bot.reply_to(message, "Silakan kirim file Excel (.xls, .xlsx, .xlsm) yang berisi gambar.")
    except Exception as e:
        logging.error("Error in get_images_command: ", exc_info=True)

@bot.message_handler(state=HitungGambarState.waiting_for_file, content_types=['document'])
async def excel_get(message: Message):
    try:
        # Cek apakah file yang diterima adalah file Excel
        if not (message.document.file_name.endswith(".xls") or
                message.document.file_name.endswith(".xlsx") or
                message.document.file_name.endswith(".xlsm")):
            return await bot.send_message(message.chat.id, "Kirim file Excel (.xls, .xlsx, .xlsm) yang valid.")

        file = await bot.get_file(message.document.file_id)
        filename = f"files/{message.document.file_name}"

        # Download the Excel file
        downloaded_file = await bot.download_file(file.file_path)
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Send images extracted from the Excel file
        images_sent = await send_images_from_excel(filename, message.chat.id)

        if images_sent == 0:
            await bot.send_message(message.chat.id, "Tidak ada gambar ditemukan dalam file Excel.")
        else:
            await bot.send_message(message.chat.id, f"{images_sent} gambar berhasil dikirim.")

        os.remove(filename)  # Hapus file Excel setelah diproses
        await bot.delete_state(message.from_user.id, message.chat.id)
    except ApiTelegramException as e:
        logging.error("Telegram API error: ", exc_info=True)
        await bot.send_message(message.chat.id, "Terjadi kesalahan saat mengakses Telegram API.")
    except Exception as e:
        logging.error("Error in excel_get: ", exc_info=True)
        await bot.send_message(message.chat.id, "Terjadi kesalahan saat memproses file.")

async def send_images_from_excel(filename, chat_id):
    """
    Extracts images from the Excel file and sends them to the user.

    Parameters:
    filename (str): The path to the Excel file.
    chat_id (int): The ID of the chat to send images to.

    Returns:
    int: The number of images sent.
    """
    images_sent = 0
    try:
        images = extract_images_from_excel(filename)  # Gunakan fungsi helper untuk mengekstrak gambar

        for img_stream in images:
            await bot.send_photo(chat_id, img_stream)
            images_sent += 1
    except Exception as e:
        logging.error("Error sending images: ", exc_info=True)

    return images_sent

@bot.message_handler(state=HitungGambarState.waiting_for_file, commands=['cancel'])
async def cancel_process(message: Message):
    try:
        await bot.send_message(message.chat.id, "Proses dibatalkan.")
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("Error in cancel_process: ", exc_info=True)
