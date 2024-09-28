import logging
import os
from telebot.types import Message
from telebot.apihelper import ApiTelegramException
from bot import bot
from state import HitungGambarState  # New state for image handling
from helpers import extract_images_from_excel  # Import helper function

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

        # Download the Excel file
        downloaded_file = await bot.download_file(file.file_path)
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Extract images from the Excel file
        images = extract_images_from_excel(filename)
        if not images:
            await bot.send_message(message.chat.id, "Tidak ada gambar ditemukan dalam file Excel.")
            return

        # Send images to the user
        images_sent = 0
        for img_stream in images:
            await bot.send_photo(message.chat.id, img_stream)
            images_sent += 1

        await bot.send_message(message.chat.id, f"{images_sent} gambar berhasil dikirim.")
        os.remove(filename)  # Remove the Excel file after processing
        await bot.delete_state(message.from_user.id, message.chat.id)
    except ApiTelegramException as e:
        logging.error("Telegram API error: ", exc_info=True)
        await bot.send_message(message.chat.id, "Terjadi kesalahan saat mengakses Telegram API.")
    except Exception as e:
        logging.error("Error: ", exc_info=True)
        await bot.send_message(message.chat.id, "Terjadi kesalahan saat memproses file.")
