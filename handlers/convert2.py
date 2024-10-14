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
async def convert_command(message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, Convert2State.filename, message.chat.id)
        await bot.reply_to(message, txt2_convert)
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.filename, content_types=['document'])
async def txt_get(message: Message):
    try:
        if not message.document.file_name.endswith(".txt"):
            return await bot.send_message(message.chat.id, "Kirim file .txt")

        file = await bot.get_file(message.document.file_id)
        filename = f"files/{message.document.file_name}"

        await bot.set_state(message.from_user.id, Convert2State.file_change_count, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['filename'] = filename

        downloaded_file = await bot.download_file(file.file_path)
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        await bot.send_message(message.chat.id, 'File diterima. Berapa kali nama file akan berganti?')
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=Convert2State.file_change_count, is_digit=True)
async def file_change_count_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['file_change_count'] = int(message.text)

        await bot.send_message(message.chat.id, 'Setiap berapa file nama file akan berganti? (Masukkan angka)')
        await bot.set_state(message.from_user.id, Convert2State.file_change_frequency, message.chat.id)

    except Exception as e:
        logging.error("Error in file_change_count_get: ", exc_info=True)

@bot.message_handler(state=Convert2State.file_change_frequency, is_digit=True)
async def file_change_frequency_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['file_change_frequency'] = int(message.text)

        await bot.send_message(message.chat.id, 'Masukkan nama file pertama:')
        await bot.set_state(message.from_user.id, Convert2State.file_names, message.chat.id)

    except Exception as e:
        logging.error("Error in file_change_frequency_get: ", exc_info=True)

@bot.message_handler(state=Convert2State.file_names)
async def file_names_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if 'file_names' not in data:
                data['file_names'] = []
            data['file_names'].append(message.text)

        if len(data['file_names']) < data['file_change_count']:
            await bot.send_message(message.chat.id, f'Masukkan nama file berikutnya ({len(data["file_names"]) + 1} dari {data["file_change_count"]}):')
        else:
            await bot.send_message(message.chat.id, 'Masukkan nama kontak per file:')
            await bot.set_state(message.from_user.id, Convert2State.contact_names, message.chat.id)

    except Exception as e:
        logging.error("Error in file_names_get: ", exc_info=True)

@bot.message_handler(state=Convert2State.contact_names)
async def contact_names_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if 'contact_names' not in data:
                data['contact_names'] = []
            data['contact_names'].append(message.text)

        if len(data['contact_names']) < data['file_change_count']:
            await bot.send_message(message.chat.id, f'Masukkan nama kontak berikutnya ({len(data["contact_names"]) + 1} dari {data["file_change_count"]}):')
        else:
            await bot.send_message(message.chat.id, 'Masukkan jumlah kontak per file:')
            await bot.set_state(message.from_user.id, Convert2State.totalc, message.chat.id)

    except Exception as e:
        logging.error("Error in contact_names_get: ", exc_info=True)

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
        await bot.send_message(message.chat.id, f'Jumlah file diatur menjadi: {message.text}. Mulai mengonversi...')
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['totalf'] = int(message.text)
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

@bot.message_handler(state=Convert2State.totalc, is_digit=False)
@bot.message_handler(state=Convert2State.totalf, is_digit=False)
async def invalid_input(message: Message):
    try:
        await bot.send_message(message.chat.id, 'Masukkan angka yang valid.')
    except Exception as e:
        logging.error("error: ", exc_info=True)
