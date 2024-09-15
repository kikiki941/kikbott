import logging
import os
from re import findall
from asyncio import sleep
from telebot.types import Message
from telebot.apihelper import ApiTelegramException

from bot import bot
from message import txt_convert2
from helpers import convert2
from state import Convert2State

@bot.message_handler(commands='convert')
async def convert_command(message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, ConvertState.filename, message.chat.id)
        await bot.reply_to(message, 'Kirim file .txt:')
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=ConvertState.filename, content_types=['document'])
async def txt_get(message: Message):
    try:
        if not message.document.file_name.endswith(".txt"):
            return await bot.send_message(message.chat.id, "Kirim file .txt")
        
        file = await bot.get_file(message.document.file_id)
        filename = f"files/{message.document.file_name}"
        
        await bot.set_state(message.from_user.id, ConvertState.name, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['filename'] = filename

        downloaded_file = await bot.download_file(file.file_path)
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        await bot.send_message(message.chat.id, 'File diterima. Masukkan nama file vcf yang akan dihasilkan:')
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=ConvertState.name)
async def name_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['file_names'] = [message.text]  # Nama file pertama
            data['file_contacts'] = []  # Inisialisasi kontak
        await bot.send_message(message.chat.id, 'Masukkan nama kontak untuk file ini:')
        await bot.set_state(message.from_user.id, ConvertState.contact, message.chat.id)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=ConvertState.contact)
async def contact_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['file_contacts'].append(message.text)
        
        # Tanyakan apakah nama file dan kontak akan berganti setiap beberapa file
        await bot.send_message(message.chat.id, 'Apakah setiap beberapa file nama file dan nama kontak akan berganti? Pilih ya/tidak.')
        await bot.set_state(message.from_user.id, ConvertState.change_name, message.chat.id)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=ConvertState.change_name)
async def change_name_get(message: Message):
    try:
        if message.text.lower() == 'ya':
            await bot.send_message(message.chat.id, 'Masukkan setiap berapa file nama file dan kontak berganti:')
            await bot.set_state(message.from_user.id, ConvertState.interval, message.chat.id)
        elif message.text.lower() == 'tidak':
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['interval'] = None
            await bot.send_message(message.chat.id, 'Masukkan jumlah kontak per file:')
            await bot.set_state(message.from_user.id, ConvertState.contacts_per_file, message.chat.id)
        else:
            await bot.send_message(message.chat.id, 'Masukkan "ya" atau "tidak".')
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=ConvertState.interval, is_digit=True)
async def interval_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['interval'] = int(message.text)
        await bot.send_message(message.chat.id, 'Masukkan batas ganti nama:')
        await bot.set_state(message.from_user.id, ConvertState.max_changes, message.chat.id)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=ConvertState.max_changes, is_digit=True)
async def max_changes_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['max_changes'] = int(message.text)
        await bot.send_message(message.chat.id, 'Masukkan jumlah kontak per file:')
        await bot.set_state(message.from_user.id, ConvertState.contacts_per_file, message.chat.id)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=ConvertState.contacts_per_file, is_digit=True)
async def contacts_per_file_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['contacts_per_file'] = int(message.text)
        
        await bot.send_message(message.chat.id, 'Masukkan jumlah total file:')
        await bot.set_state(message.from_user.id, ConvertState.totalf, message.chat.id)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=ConvertState.totalf, is_digit=True)
async def totalf_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['totalf'] = int(message.text)

        await bot.send_message(message.chat.id, 'Mulai mengonversi...')

        # Jalankan logika konversi, sesuaikan logika penggantian nama file dan kontak di sini
        vcf_files = convert(data)
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

        await bot.send_message(message.chat.id, "Convert selesai!")
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("error: ", exc_info=True)
