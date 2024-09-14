import logging
import os
from re import findall
from asyncio import sleep
from telebot.types import Message
from telebot.apihelper import ApiTelegramException

from bot import bot
from message import *
from helpers import convert2
from state import Convert2State

@bot.message_handler(commands='convert2')
async def convert2_command(message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, Convert2State.filename, message.chat.id)
        await bot.reply_to(message, txt_convert2)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.filename, content_types=['document'])
async def txt_get(message: Message):
    try:
        if not message.document.file_name.endswith(".txt"):
            return await bot.send_message(message.chat.id, "Kirim file .txt")
        
        file = await bot.get_file(message.document.file_id)
        filename = f"files/{message.document.file_name}"
        
        await bot.set_state(message.from_user.id, Convert2State.name, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['filename'] = filename

        downloaded_file = await bot.download_file(file.file_path)
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        await bot.send_message(message.chat.id, 'File diterima. Silakan masukkan nama file vcf yang akan dihasilkan:')
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.name)
async def name_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text
            await bot.send_message(message.chat.id, f'Nama file diatur menjadi: {message.text}. Silakan masukkan nama kontak untuk file pertama:')
            await bot.set_state(message.from_user.id, Convert2State.cname, message.chat.id)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.cname)
async def cname_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['cname'] = message.text
            await bot.send_message(message.chat.id, f'Nama kontak diatur menjadi: {message.text}. Silakan masukkan jumlah kontak per file:')
            await bot.set_state(message.from_user.id, Convert2State.totalc, message.chat.id)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.totalc, is_digit=True)
async def totalc_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['totalc'] = int(message.text)
            await bot.send_message(message.chat.id, f'Jumlah kontak per file diatur menjadi: {message.text}. Silakan masukkan jumlah file:')
            await bot.set_state(message.from_user.id, Convert2State.totalf, message.chat.id)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.totalf, is_digit=True)
async def totalf_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['totalf'] = int(message.text)
            await bot.send_message(message.chat.id, f'Jumlah file diatur menjadi: {message.text}. Apakah setiap beberapa file nama file akan berganti? (ya/tidak)')
            await bot.set_state(message.from_user.id, Convert2State.change_name_prompt, message.chat.id)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.change_name_prompt)
async def change_name_prompt_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if message.text.lower() == "ya":
                await bot.send_message(message.chat.id, f'Masukkan setiap berapa file nama akan berganti:')
                await bot.set_state(message.from_user.id, Convert2State.change_every, message.chat.id)
            else:
                await bot.send_message(message.chat.id, f'Mulai mengonversi...')
                vcf_files = convert2(data)
                await send_files(message, data, vcf_files)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.change_every, is_digit=True)
async def change_every_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['change_every'] = int(message.text)
            await bot.send_message(message.chat.id, f'Setiap {message.text} file nama akan berganti. Masukkan batas pergantian nama (berapa kali):')
            await bot.set_state(message.from_user.id, Convert2State.change_limit, message.chat.id)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.change_limit, is_digit=True)
async def change_limit_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['change_limit'] = int(message.text)
            await bot.send_message(message.chat.id, f'Batas pergantian nama diatur menjadi {message.text} kali. Silakan masukkan nama file pertama dan nama kontaknya:')
            await bot.set_state(message.from_user.id, Convert2State.new_name_1, message.chat.id)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.new_name_1)
async def new_name_1_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            new_names = data.get('new_names', [])
            new_names.append(message.text)
            await bot.send_message(message.chat.id, f'Nama file baru diatur menjadi: {message.text}. Silakan masukkan nama kontak untuk file ini:')
            await bot.set_state(message.from_user.id, Convert2State.contact_names, message.chat.id)
            data['new_names'] = new_names
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.contact_names)
async def contact_names_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            new_names = data.get('new_names', [])
            current_name = new_names[-1]  # Nama file terbaru yang sedang diinput kontaknya

            # Inisialisasi dictionary untuk menyimpan kontak per file jika belum ada
            if 'contacts' not in data:
                data['contacts'] = {}

            if current_name not in data['contacts']:
                data['contacts'][current_name] = []

            # Tambahkan nama kontak ke file saat ini hanya jika belum mencapai batas
            if len(data['contacts'][current_name]) < data['totalc']:
                data['contacts'][current_name].append(message.text)
                await bot.send_message(message.chat.id, f"Kontak '{message.text}' telah ditambahkan untuk file '{current_name}'.")

            # Cek apakah jumlah kontak untuk file saat ini sudah mencapai batas (misalnya totalc = jumlah kontak per file)
            if len(data['contacts'][current_name]) >= data['totalc']:
                # Cek apakah semua file sudah diinput
                if len(data['contacts']) >= data['totalf']:  
                    await bot.send_message(message.chat.id, 'Semua nama file dan kontak telah diinput. Memulai konversi...')
                    vcf_files = convert2(data)  # Mulai proses konversi
                    await send_files(message, data, vcf_files)  # Kirim file hasil konversi
                else:
                    # Minta nama file dan kontak berikutnya jika belum mencapai batas file
                    await bot.send_message(message.chat.id, 'Nama kontak untuk file ini telah selesai. Silakan masukkan nama file berikutnya dan nama kontaknya:')
                    await bot.set_state(message.from_user.id, Convert2State.new_name_1, message.chat.id)
            else:
                # Jika belum mencapai jumlah kontak per file, minta input kontak berikutnya
                await bot.send_message(message.chat.id, f'Masukkan nama kontak berikutnya untuk file {current_name}:')
    except Exception as e:
        logging.error("Error while adding contact: ", exc_info=True)
        await bot.send_message(message.chat.id, "Terjadi kesalahan. Silakan coba lagi.")


async def send_files(message, data, vcf_files):
    try:
        os.remove(data['filename'])
        for file in vcf_files:
            try:
                await bot.send_document(message.chat.id, open(file, 'rb'))
                os.remove(file)
            except ApiTelegramException as e:
                if "Too Many Requests" in e.description:
                    delay = int(findall('\d+', e.description)[0])
                    await sleep(delay)
                else:
                    logging.error("Telegram API error: ", exc_info=True)
            except Exception as e:
                logging.error("Error sending document: ", exc_info=True)
        await bot.send_message(message.chat.id, "Konversi selesai!")
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("Error during file sending: ", exc_info=True)
