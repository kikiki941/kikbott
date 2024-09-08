import os
import logging
from telebot.types import Message

from bot import bot
from message import txt_chat_to_vcf
from state import ChatToTxtState

# Pastikan direktori untuk menyimpan file ada
if not os.path.exists('files'):
    os.makedirs('files')

@bot.message_handler(commands=['chattotxt'])
async def chat_to_txt_command(message: Message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, ChatToTxtState.waiting_for_text_input, message.chat.id)
        await bot.reply_to(message, "Masukkan teks yang ingin Anda simpan ke dalam file .txt:")
    except Exception as e:
        logging.error("Error in chat_to_txt_command: ", exc_info=True)

@bot.message_handler(state=ChatToTxtState.waiting_for_text_input)
async def handle_text_input(message: Message):
    try:
        # Simpan teks yang dimasukkan oleh pengguna
        input_text = message.text
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['input_text'] = input_text
        
        await bot.send_message(message.chat.id, 'Teks ditambahkan. Ketik /done jika sudah selesai menambah teks.')
    except Exception as e:
        logging.error("Error in handle_text_input: ", exc_info=True)

@bot.message_handler(commands=['done'], state=ChatToTxtState.waiting_for_text_input)
async def handle_done_txt(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            input_text = data.get('input_text', '')

            if not input_text:
                return await bot.send_message(message.chat.id, "Tidak ada teks yang ditemukan. Silakan tambahkan teks.")

            # Nama file bisa diambil dari id pengguna atau waktu input untuk membuatnya unik
            txt_filename = f"chat_{message.from_user.id}.txt"
            file_path = save_txt(input_text, txt_filename)

            await bot.send_message(message.chat.id, f'File TXT berhasil dibuat dengan nama: {txt_filename}')

            # Kirim file TXT ke user
            with open(file_path, 'rb') as doc:
                await bot.send_document(message.chat.id, doc)

            # Hapus file lokal setelah dikirim
            os.remove(file_path)
            await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("Error in handle_done_txt: ", exc_info=True)
        await bot.send_message(message.chat.id, "Terjadi kesalahan saat membuat file TXT.")
