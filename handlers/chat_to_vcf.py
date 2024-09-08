import logging
import os
from telebot.types import Message
from telebot.apihelper import ApiTelegramException

from bot import bot
from message import txt_chat_to_vcf
from helpers import create_vcf, clean_phone_number, clean_string
from state import ChatToVcfState

# Pastikan direktori 'files' ada
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
        contact_name = clean_string(message.text)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['contact_name'] = contact_name
            data['phone_numbers'] = []  # Initialize list for phone numbers
        
        await bot.send_message(message.chat.id, 'Silakan masukkan nomor telepon kontak pertama:')
        await bot.set_state(message.from_user.id, ChatToVcfState.waiting_for_phone_number, message.chat.id)
    except Exception as e:
        logging.error("Error in handle_contact_name: ", exc_info=True)

@bot.message_handler(state=ChatToVcfState.waiting_for_phone_number)
async def handle_phone_number(message: Message):
    try:
        phone_number = clean_phone_number(message.text)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['phone_numbers'].append(phone_number)
        
        await bot.send_message(message.chat.id, 'Nomor telepon ditambahkan. Masukkan nomor lain, atau ketik /done jika sudah selesai.')
    except Exception as e:
        logging.error("Error in handle_phone_number: ", exc_info=True)

@bot.message_handler(commands='done', state=ChatToVcfState.waiting_for_phone_number)
async def handle_done(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            contact_name = data.get('contact_name')
            phone_numbers = data.get('phone_numbers', [])
        
        if not phone_numbers:
            return await bot.send_message(message.chat.id, "Anda belum menambahkan nomor telepon.")
        
        # Gabungkan semua nomor telepon ke dalam satu file VCF
        vcf_filename = clean_string(f"{contact_name}_contacts")
        file_path = create_vcf(contact_name, phone_numbers, vcf_filename)  # Modifikasi create_vcf
        
        await bot.send_message(message.chat.id, f'File VCF berhasil dibuat dengan nama: {vcf_filename}.vcf')
        
        # Kirim file VCF ke pengguna
        try:
            with open(file_path, 'rb') as doc:
                await bot.send_document(message.chat.id, doc)
        except ApiTelegramException as e:
            logging.error("API exception: ", exc_info=True)
            await bot.send_message(message.chat.id, "Terjadi kesalahan saat mengirim file.")
        
        os.remove(file_path)
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("Error in handle_done: ", exc_info=True)
