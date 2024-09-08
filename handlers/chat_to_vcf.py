import logging
import os
from telebot.types import Message
from telebot.apihelper import ApiTelegramException

from bot import bot
from message import txt_chat_to_vcf
from helpers import create_vcf
from state import ChatToVcfState

# Ensure the 'files' directory exists
if not os.path.exists('files'):
    os.makedirs('files')

@bot.message_handler(commands='chattovcf')
async def chat_to_vcf_command(message: Message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, ChatToVcfState.waiting_for_contact_name, message.chat.id)
        await bot.reply_to(message, txt_chat_to_vcf)
    except Exception as e:
        logging.error("Error in chat_to_vcf_command: ", exc_info=True)

@bot.message_handler(state=ChatToVcfState.waiting_for_contact_name)
async def handle_contact_name(message: Message):
    try:
        contact_name = message.text
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['contact_name'] = contact_name
        
        await bot.send_message(message.chat.id, 'Silakan masukkan nama file VCF yang akan dihasilkan:')
        await bot.set_state(message.from_user.id, ChatToVcfState.waiting_for_filename, message.chat.id)
    except Exception as e:
        logging.error("Error in handle_contact_name: ", exc_info=True)

@bot.message_handler(state=ChatToVcfState.waiting_for_filename)
async def handle_vcf_filename(message: Message):
    try:
        vcf_filename = message.text
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            contact_name = data.get('contact_name')
        
        if not contact_name:
            return await bot.send_message(message.chat.id, "Nama kontak tidak ditemukan.")
        
        # Use the helper function to create the VCF file
        file_path = create_vcf(contact_name, vcf_filename)
        
        await bot.send_message(message.chat.id, f'File VCF berhasil dibuat dengan nama: {vcf_filename}.vcf')
        
        # Send VCF file to user
        try:
            with open(file_path, 'rb') as doc:
                await bot.send_document(message.chat.id, doc)
        except ApiTelegramException as e:
            logging.error("API exception: ", exc_info=True)
            await bot.send_message(message.chat.id, "Terjadi kesalahan saat mengirim file.")
        
        os.remove(file_path)
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("Error in handle_vcf_filename: ", exc_info=True)
