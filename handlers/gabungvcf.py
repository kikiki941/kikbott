import logging
import os
from re import findall
from asyncio import sleep
from telebot.types import Message
from telebot.apihelper import ApiTelegramException

from bot import bot
from message import txt_gabung_vcf
from helpers import gabung_vcf
from state import GabungVcfState

# Ensure the 'files' directory exists
if not os.path.exists('files'):
    os.makedirs('files')

@bot.message_handler(commands='gabungvcf')
async def gabung_vcf_command(message: Message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, GabungVcfState.waiting_for_files, message.chat.id)
        await bot.reply_to(message, txt_gabung_vcf)
    except Exception as e:
        logging.error("Error in gabung_vcf_command: ", exc_info=True)

@bot.message_handler(state=GabungVcfState.waiting_for_files, content_types=['document'])
async def handle_vcf_file(message: Message):
    try:
        if not message.document.file_name.endswith(".vcf"):
            return await bot.send_message(message.chat.id, "Kirim file .vcf")
        
        file = await bot.get_file(message.document.file_id)
        filename = f"files/{message.document.file_name}"
        
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if 'files' not in data:
                data['files'] = []
            data['files'].append(filename)

        downloaded_file = await bot.download_file(file.file_path)
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        await bot.send_message(message.chat.id, 'File diterima. Kirim file VCF lain jika ada. Jika sudah selesai, kirim /done.')
    except Exception as e:
        logging.error("Error in handle_vcf_file: ", exc_info=True)

@bot.message_handler(commands='done', state=GabungVcfState.waiting_for_files)
async def done_command(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if 'files' not in data or not data['files']:
                return await bot.send_message(message.chat.id, "Belum ada file VCF yang diterima.")

            await bot.send_message(message.chat.id, 'Masukkan nama file TXT yang akan dihasilkan:')
            await bot.set_state(message.from_user.id, GabungVcfState.name, message.chat.id)
    except Exception as e:
        logging.error("Error in done_command: ", exc_info=True)

@bot.message_handler(state=GabungVcfState.name)
async def handle_txt_name(message: Message):
    try:
        await bot.send_message(message.chat.id, f'Nama file diatur menjadi: {message.text}. Mulai menggabungkan file...')
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text
            files = data.get('files', [])
            output_file = gabung_vcf(files, data['name'])
            for file in files:
                os.remove(file)

            if not os.path.exists(output_file):
                return await bot.send_message(message.chat.id, "File hasil gabungan tidak ditemukan. Coba lagi.")
            
            while True:
                try:
                    with open(output_file, 'rb') as doc:
                        await bot.send_document(message.chat.id, doc)
                    os.remove(output_file)
                    break
                except ApiTelegramException as e:
                    if "Too Many Requests" in str(e):
                        delay = int(findall(r'\d+', str(e))[0])
                        await sleep(delay)
                    else:
                        logging.error("API exception: ", exc_info=True)
                        continue
                except Exception as e:
                    logging.error("Error sending document: ", exc_info=True)
                    continue

            await bot.send_message(message.chat.id, "Gabungkan VCF selesai!")
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("Error in handle_txt_name: ", exc_info=True)
