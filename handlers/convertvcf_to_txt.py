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
        logging.info(f"Command /convertvcf_to_txt diterima dari {message.from_user.id}")
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, ConvertVcfToTxtState.filename, message.chat.id)
        await bot.reply_to(message, txt_convert_vcf_to_txt)
    except Exception as e:
        logging.error("Error in /convertvcf_to_txt command: ", exc_info=True)
@bot.message_handler(state=ConvertVcfToTxtState.filename, content_types=['document'])
async def vcf_file_get(message: Message):
    try:
        logging.info(f"Menerima file dari {message.from_user.id}. Nama file: {message.document.file_name}")
        
        if not message.document.file_name.endswith(".vcf"):
            logging.warning("File yang diterima bukan VCF.")
            return await bot.send_message(message.chat.id, "Kirim file .vcf")
        
        file = await bot.get_file(message.document.file_id)
        filename = f"files/{message.document.file_name}"
        downloaded_file = await bot.download_file(file.file_path)
        
        # Simpan file VCF
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        logging.info(f"File VCF {filename} berhasil diunduh.")
        
        # Simpan nama file di state
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['filename'] = filename
        
        await bot.set_state(message.from_user.id, ConvertVcfToTxtState.name, message.chat.id)
        await bot.send_message(message.chat.id, 'File diterima. Silakan masukkan nama file txt yang akan dihasilkan:')
    except Exception as e:
        logging.error("Error in vcf_file_get handler: ", exc_info=True)
@bot.message_handler(state=ConvertVcfToTxtState.name)
async def vcf_to_txt_name_get(message: Message):
    try:
        logging.info(f"Nama file TXT akan diatur menjadi: {message.text}")
        
        await bot.send_message(message.chat.id, f'Nama file diatur menjadi: {message.text}. Mulai mengonversi file...')
        
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text
            txt_file = convert_vcf_to_txt(data)  # Proses konversi file
            
            if txt_file and os.path.exists(txt_file):
                logging.info(f"File TXT {txt_file} berhasil dibuat, mengirim ke {message.from_user.id}")
                while True:
                    try:
                        await bot.send_document(message.chat.id, open(txt_file, 'rb'))
                        os.remove(txt_file)
                        break
                    except ApiTelegramException as e:
                        if "Too Many Requests" in e.description:
                            delay = int(findall(r'\d+', e.description)[0])
                            logging.warning(f"Too many requests, menunggu selama {delay} detik.")
                            await sleep(delay)
                        else:
                            logging.error("API error saat mengirim file: ", exc_info=True)
                            break
                    except Exception as e:
                        logging.error("Error saat mengirim file: ", exc_info=True)
                        break
            else:
                logging.error(f"Gagal mengonversi file, file {txt_file} tidak ditemukan atau tidak berhasil dibuat.")
                await bot.send_message(message.chat.id, "Gagal mengonversi file.")
                
            # Hapus file VCF yang telah diunduh
            os.remove(data['filename'])
            logging.info(f"File VCF {data['filename']} dihapus setelah konversi.")
        
        await bot.send_message(message.chat.id, "Convert VCF to TXT selesai!")
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("Error in vcf_to_txt_name_get handler: ", exc_info=True)
