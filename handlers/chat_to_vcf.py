import logging
import os
from telebot.types import Message
from telebot.apihelper import ApiTelegramException

from bot import bot
from message import txt_chat_to_vcf
from helpers import create_vcf

from state import ChatToVcfState

# Pastikan direktori 'files' ada
if not os.path.exists('files'):
    os.makedirs('files')

@bot.message_handler(commands='chattovcf')
async def chat_to_vcf_command(message: Message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, ChatToVcfState.waiting_for_contact_name, message.chat.id)
        await bot.reply_to(message, "Silakan masukkan nama kontak:")
    except Exception as e:
        logging.error("Error in chat_to_vcf_command: ", exc_info=True)

@bot.message_handler(state=ChatToVcfState.waiting_for_contact_name)
async def handle_contact_name(message: Message):
    try:
        contact_name = message.text.strip()
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if 'contacts' not in data:
                data['contacts'] = {}
            if 'contact_count' not in data:
                data['contact_count'] = 1
            
            # Generate a unique name for the contact
            unique_name = f"Nama {data['contact_count']}"
            data['contacts'][unique_name] = []
            data['contact_count'] += 1
        
        await bot.send_message(message.chat.id, 'Silakan masukkan nomor telepon kontak. Jika ingin menambah lagi, masukkan nomor lain, atau ketik /done jika sudah selesai:')
        await bot.set_state(message.from_user.id, ChatToVcfState.waiting_for_phone_number, message.chat.id)
    except Exception as e:
        logging.error("Error in handle_contact_name: ", exc_info=True)

@bot.message_handler(commands=['done'])
async def handle_done(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            contact_name = data.get('contact_name')
            phone_numbers = data.get('phone_numbers', [])

            if not contact_name or not phone_numbers:
                return await bot.send_message(message.chat.id, "Kontak atau nomor telepon tidak ditemukan.")

            vcf_content = ''
            # Loop through phone numbers to create multiple contacts
            for idx, phone_number in enumerate(phone_numbers):
                vcf_content += create_vcf(f"Nama {idx + 1}", phone_number)

            # Save VCF file
            vcf_filename = f"{contact_name}_multiple_contacts"
            file_path = save_vcf(vcf_content, vcf_filename)

            await bot.send_message(message.chat.id, f'File VCF berhasil dibuat dengan nama: {vcf_filename}.vcf')

            # Send VCF file to user
            with open(file_path, 'rb') as doc:
                await bot.send_document(message.chat.id, doc)

            os.remove(file_path)
            await bot.delete_state(message.from_user.id, message.chat.id)

    except Exception as e:
        logging.error("Error in handle_done: ", exc_info=True)
