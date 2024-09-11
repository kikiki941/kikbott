import logging
import os
from telebot.types import Message

from bot import bot
from helpers import gabungkan_kolom  # Impor fungsi gabungkan kolom yang telah diperbarui
from state import GabungKolomState  # Import state untuk gabung kolom

# Pastikan direktori 'files' ada
if not os.path.exists('files'):
    os.makedirs('files')

@bot.message_handler(commands=['gabungkolom'])
async def gabung_kolom_command(message: Message):
    try:
        # Setel ulang state pengguna dan setel state baru untuk menunggu file
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, GabungKolomState.waiting_for_files, message.chat.id)
        await bot.reply_to(message, "Kirim file TXT yang kolom-kolomnya ingin digabungkan.")
    except Exception as e:
        logging.error("Error in gabung_kolom_command: ", exc_info=True)

@bot.message_handler(state=GabungKolomState.waiting_for_files, content_types=['document'])
async def handle_txt_files(message: Message):
    try:
        # Pastikan file yang diunggah berformat .txt
        if not message.document.file_name.endswith(".txt"):
            return await bot.send_message(message.chat.id, "Kirim file dengan format .txt")
        
        # Dapatkan file dari server Telegram
        file_info = await bot.get_file(message.document.file_id)
        filename = f"files/{message.document.file_name}"
        
        # Simpan file dalam data session pengguna
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['filename'] = filename
        
        # Unduh file dari Telegram dan simpan di folder 'files'
        downloaded_file = await bot.download_file(file_info.file_path)
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        await bot.send_message(message.chat.id, 'File diterima. Proses penggabungan kolom sedang berlangsung.')
        await bot.set_state(message.from_user.id, GabungKolomState.processing, message.chat.id)
    except Exception as e:
        logging.error("Error in handle_txt_files: ", exc_info=True)

@bot.message_handler(state=GabungKolomState.processing)
async def process_file(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            input_file = data['filename']
            output_file = f"files/hasil_gabung_kolom.txt"
            
            # Panggil fungsi gabungkan_kolom untuk memproses file
            gabungkan_kolom(input_file, output_file)

        # Kirim file yang telah digabungkan kolomnya ke pengguna
        with open(output_file, 'rb') as doc:
            await bot.send_document(message.chat.id, doc)

        # Hapus file asli dan file hasil setelah dikirim
        os.remove(input_file)
        os.remove(output_file)

        await bot.send_message(message.chat.id, "Kolom-kolom telah digabungkan dari atas ke kiri, lalu ke bawah.")
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("Error in process_file: ", exc_info=True)
