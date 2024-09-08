import logging
import os
from re import findall
from asyncio import sleep
from telebot.types import Message
from telebot.apihelper import ApiTelegramException

from bot import bot
from message import txt_convert_vcf_to_txt
from helpers import convert_vcf_to_txt
from state import ConvertVcfToTxtState

@bot.message_handler(commands='convertvcf_to_txt')
async def convert_vcf_to_txt_command(message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, ConvertVcfToTxtState.filename, message.chat.id)
        await bot.reply_to(message, txt_convert_vcf_to_txt)
    except Exception as e:
        logging.error("Error in /convertvcf_to_txt command: ", exc_info=True)

@bot.message_handler(state=ConvertVcfToTxtState.filename, content_types=['document'])
async def vcf_file_get(message: Message):
    try:
        if not message.document.file_name.endswith(".vcf"):
            return await bot.send_message(message.chat.id, "Kirim file .vcf")
        
        file = await bot.get_file(message.document.file_id)
        filename = f"files/{message.document.file_name}"
        
        await bot.set_state(message.from_user.id, ConvertVcfToTxtState.name, message.chat.id)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['filename'] = filename

        downloaded_file = await bot.download_file(file.file_path)
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        await bot.send_message(message.chat.id, 'File diterima. Silakan masukkan nama file txt yang akan dihasilkan:')
    except Exception as e:
        logging.error("Error in vcf_file_get handler: ", exc_info=True)

@bot.message_handler(state=ConvertVcfToTxtState.name)
async def vcf_to_txt_name_get(message: Message):
    try:
        await bot.send_message(message.chat.id, f'Nama file diatur menjadi: {message.text}. Mulai konversi...')
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text
            txt_file = convert_vcf_to_txt(data)
            if os.path.exists(txt_file):
                await bot.send_document(message.chat.id, open(txt_file, 'rb'))
                os.remove(txt_file)
            os.remove(data['filename'])
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("Error in vcf_to_txt_name_get handler: ", exc_info=True)
