import logging
import os
from re import findall
from asyncio import sleep
from telebot.types import Message
from telebot.apihelper import ApiTelegramException

from bot import bot
from message import *
from helpers import convert
from state import ConvertState

@bot.message_handler(commands='convert')
async def convert_command(message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, ConvertState.filename, message.chat.id)
        await bot.reply_to(message, "Silakan kirim file .txt untuk memulai konversi.")
    except Exception as e:
        logging.error("Error in convert_command: ", exc_info=True)

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

        await bot.send_message(message.chat.id, 'File diterima. Silakan masukkan nama file vcf yang akan dihasilkan:')
    except Exception as e:
        logging.error("Error in txt_get: ", exc_info=True)

@bot.message_handler(state=ConvertState.filename)
async def not_txt(message: Message):
    try:
        await bot.send_message(message.chat.id, 'Kirim file .txt')
    except Exception as e:
        logging.error("Error in not_txt: ", exc_info=True)

@bot.message_handler(state=ConvertState.name)
async def name_get(message: Message):
    try:
        await bot.send_message(message.chat.id, f'Nama file diatur menjadi: {message.text}. Silakan masukkan nama kontak:')
        await bot.set_state(message.from_user.id, ConvertState.cname, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text
    except Exception as e:
        logging.error("Error in name_get: ", exc_info=True)

@bot.message_handler(state=ConvertState.cname)
async def cname_get(message: Message):
    try:
        await bot.send_message(message.chat.id, f'Nama kontak diatur menjadi: {message.text}. Silakan masukkan jumlah kontak per file:')
        await bot.set_state(message.from_user.id, ConvertState.totalc, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['cname'] = message.text
    except Exception as e:
        logging.error("Error in cname_get: ", exc_info=True)

@bot.message_handler(state=ConvertState.totalc, is_digit=True)
async def totalc_get(message: Message):
    try:
        await bot.send_message(message.chat.id, f'Jumlah kontak per file diatur menjadi: {message.text}. Silakan masukkan jumlah file:')
        await bot.set_state(message.from_user.id, ConvertState.totalf, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['totalc'] = int(message.text)
    except Exception as e:
        logging.error("Error in totalc_get: ", exc_info=True)

@bot.message_handler(state=ConvertState.totalf, is_digit=True)
async def totalf_get(message: Message):
    try:
        await bot.send_message(message.chat.id, f'Jumlah file diatur menjadi: {message.text}. Apakah penomoran akan di-reset setiap file? (ya/tidak)')
        await bot.set_state(message.from_user.id, ConvertState.reset_numbering, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['totalf'] = int(message.text)
    except Exception as e:
        logging.error("Error in totalf_get: ", exc_info=True)

@bot.message_handler(state=ConvertState.reset_numbering)
async def reset_numbering_get(message: Message):
    try:
        if message.text.lower() not in ['ya', 'tidak']:
            return await bot.send_message(message.chat.id, "Masukkan jawaban 'ya' atau 'tidak'.")
        
        await bot.send_message(message.chat.id, 'Mulai mengonversi...')
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['reset_numbering'] = message.text.lower() == 'ya'
            vcf_files = convert(data)
            os.remove(data['filename'])
            
            # Mengirim file VCF ke pengguna
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
        logging.error("Error in reset_numbering_get: ", exc_info=True)

@bot.message_handler(state=ConvertState.totalc, is_digit=False)
@bot.message_handler(state=ConvertState.totalf, is_digit=False)
async def invalid_input(message: Message):
    try:
        await bot.send_message(message.chat.id, 'Masukkan angka yang valid.')
    except Exception as e:
        logging.error("Error in invalid_input: ", exc_info=True)
