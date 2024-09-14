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
        await bot.send_message(message.chat.id, f'Nama file diatur menjadi: {message.text}. Silakan masukkan nama kontak:')
        await bot.set_state(message.from_user.id, Convert2State.cname, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.cname)
async def cname_get(message: Message):
    try:
        await bot.send_message(message.chat.id, f'Nama kontak diatur menjadi: {message.text}. Silakan masukkan jumlah kontak per file:')
        await bot.set_state(message.from_user.id, Convert2State.totalc, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['cname'] = message.text
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.totalc, is_digit=True)
async def totalc_get(message: Message):
    try:
        await bot.send_message(message.chat.id, f'Jumlah kontak per file diatur menjadi: {message.text}. Silakan masukkan jumlah file:')
        await bot.set_state(message.from_user.id, Convert2State.totalf, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['totalc'] = int(message.text)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.totalf, is_digit=True)
async def totalf_get(message: Message):
    try:
        await bot.send_message(message.chat.id, f'Jumlah file diatur menjadi: {message.text}. Apakah setiap beberapa file nama file akan berganti? (ya/tidak)')
        await bot.set_state(message.from_user.id, Convert2State.change_name_prompt, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['totalf'] = int(message.text)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.change_name_prompt)
async def change_name_prompt_get(message: Message):
    try:
        if message.text.lower() == "ya":
            await bot.send_message(message.chat.id, f'Masukkan setiap berapa file nama akan berganti:')
            await bot.set_state(message.from_user.id, Convert2State.change_every, message.chat.id)
        else:
            await bot.send_message(message.chat.id, f'Mulai mengonversi...')
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                vcf_files = convert(data)
                await send_files(message, data, vcf_files)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.change_every, is_digit=True)
async def change_every_get(message: Message):
    try:
        await bot.send_message(message.chat.id, f'Setiap {message.text} file nama akan berganti. Masukkan batas pergantian nama (berapa kali):')
        await bot.set_state(message.from_user.id, Convert2State.change_limit, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['change_every'] = int(message.text)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.change_limit, is_digit=True)
async def change_limit_get(message: Message):
    try:
        await bot.send_message(message.chat.id, f'Batas pergantian nama diatur menjadi {message.text} kali. Silakan masukkan nama file baru:')
        await bot.set_state(message.from_user.id, Convert2State.new_name_1, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['change_limit'] = int(message.text)
            data['new_names'] = []  # Initialize new names list
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.new_name_1)
async def new_name_1_get(message: Message):
    try:
        await bot.send_message(message.chat.id, 'Masukkan nama kontak untuk file baru:')
        await bot.set_state(message.from_user.id, Convert2State.contact_names, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data.setdefault('new_names', []).append(message.text)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.new_name_2_get)
async def new_name_2_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            new_names = data.get('new_names', [])
            new_names.append(message.text)

            if len(new_names) >= data.get('change_limit', 10):
                # Batas nama file baru telah tercapai
                await bot.send_message(message.chat.id, 'Batas nama file baru telah tercapai. Memulai konversi...')
                data['new_names'] = new_names
                vcf_files = convert2(data)
                
                # Logging setelah konversi
                logging.info(f"File yang dihasilkan dari convert2: {vcf_files}")
                
                await send_files(message, data, vcf_files)
            else:
                # Meminta nama kontak berikutnya
                next_index = len(new_names) + 1
                if next_index <= 100:  # Pastikan tidak melebihi 100 nama
                    await bot.send_message(message.chat.id, f'Masukkan nama kontak berikutnya (kontak {next_index}):')
                    await bot.set_state(message.from_user.id, Convert2State.new_name_1 + next_index, message.chat.id)
                else:
                    # Jika sudah mencapai batas nama file baru
                    await bot.send_message(message.chat.id, 'Batas nama kontak telah tercapai. Memulai konversi...')
                    data['new_names'] = new_names
                    vcf_files = convert2(data)
                    
                    # Logging setelah konversi
                    logging.info(f"File yang dihasilkan dari convert2: {vcf_files}")
                    
                    await send_files(message, data, vcf_files)
    except Exception as e:
        logging.error("Error during contact names handling: ", exc_info=True)

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
