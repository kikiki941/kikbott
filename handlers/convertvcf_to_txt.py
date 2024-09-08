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
async def convert_vcf_to_txt_command(message: Message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, ConvertVcfToTxtState.filename, message.chat.id)
        await bot.reply_to(message, "Kirim file .vcf yang ingin dikonversi ke .txt")
    except Exception as e:
        logging.error("Error: ", exc_info=True)

@bot.message_handler(state=ConvertVcfToTxtState.filename, content_types=['document'])
async def handle_vcf_file(message: Message):
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

        await bot.send_message(message.chat.id, 'File diterima. Silakan masukan nama file txt yang akan dihasilkan:')
    except Exception as e:
        logging.error("Error: ", exc_info=True)

@bot.message_handler(state=ConvertVcfToTxtState.name)
async def handle_txt_name(message: Message):
    try:
        await bot.send_message(message.chat.id, f'Nama file diatur menjadi: {message.text}. Mulai mengonversi file...')
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text
            file = convert_vcf_to_txt(data)
            os.remove(data['filename'])

            while True:
                try:
                    await bot.send_document(message.chat.id, open(file, 'rb'))
                    os.remove(file)
                    break
                except Throttled as e:
                    if "Too Many Requests" in str(e):
                        delay = int(findall(r'\d+', str(e))[0])
                        await sleep(delay)
                    else:
                        continue
                except Exception as e:
                    logging.error("Error sending document: ", exc_info=True)
                    continue

            await bot.send_message(message.chat.id, "Convert VCF to TXT selesai!")
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("Error: ", exc_info=True)
