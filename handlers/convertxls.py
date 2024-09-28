import logging
import os
from telebot.types import Message
from bot import bot
from helpers import convert_xls_to_xlsx, extract_images_from_excel
from state import ConvertXlsImagesState

@bot.message_handler(commands='convertxls')
async def convertxls_command(message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, ConvertXlsImagesState.filename, message.chat.id)
        await bot.reply_to(message, "Silakan kirim file .xls yang akan dikonversi.")
    except Exception as e:
        logging.error("Error in convertxls_command: ", exc_info=True)

@bot.message_handler(state=ConvertXlsImagesState.filename, content_types=['document'])
async def xls_get(message: Message):
    try:
        if not message.document.file_name.endswith(".xls"):
            return await bot.send_message(message.chat.id, "Kirim file .xls")
        
        file_info = await bot.get_file(message.document.file_id)
        filename = f"files/{message.document.file_name}"
        
        logging.info(f"File .xls diterima: {filename}")
        downloaded_file = await bot.download_file(file_info.file_path)
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        await bot.set_state(message.from_user.id, ConvertXlsImagesState.name, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['filename'] = filename

        await bot.send_message(message.chat.id, 'File diterima. Silakan masukkan nama file .xlsx yang akan dihasilkan:')
    except Exception as e:
        logging.error("Error in xls_get: ", exc_info=True)

@bot.message_handler(state=ConvertXlsImagesState.name)
async def name_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if 'filename' not in data:
                await bot.send_message(message.chat.id, "Tidak ada file .xls yang diterima. Silakan coba lagi.")
                await bot.delete_state(message.from_user.id, message.chat.id)
                return

            xls_file = data['filename']
            await bot.send_message(message.chat.id, f'Nama file diatur menjadi: {message.text}. Mulai mengonversi file...')

            logging.info(f"Memulai konversi file: {xls_file}")

            # Proses konversi
            xlsx_file = convert_xls_to_xlsx(xls_file)
            if not xlsx_file:
                await bot.send_message(message.chat.id, "Konversi .xls ke .xlsx gagal.")
                logging.error("Konversi file .xls ke .xlsx gagal.")
                return

            logging.info(f"File .xlsx berhasil dibuat: {xlsx_file}")
            await bot.send_message(message.chat.id, "Konversi berhasil. Mengekstrak gambar...")

            # Proses ekstraksi gambar
            images = extract_images_from_excel(xlsx_file)
            if images:
                for img in images:
                    await bot.send_photo(message.chat.id, img)
                logging.info(f"{len(images)} gambar berhasil diekstrak.")
            else:
                await bot.send_message(message.chat.id, "Tidak ada gambar ditemukan dalam file.")
                logging.info("Tidak ada gambar ditemukan dalam file .xlsx")

            # Hapus file setelah selesai
            os.remove(xlsx_file)
            os.remove(xls_file)
        
        await bot.send_message(message.chat.id, "Proses konversi selesai.")
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("Error in name_get: ", exc_info=True)
