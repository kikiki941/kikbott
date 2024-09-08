import logging
import os
from telebot.types import Message
from telebot.apihelper import ApiTelegramException
from bot import bot
from message import txt_chat_to_vcf
from helpers import create_vcf, clean_phone_number, clean_string
from state import ChatToVcfState

# Ensure the 'files' directory exists
if not os.path.exists('files'):
    os.makedirs('files')

# Command to start VCF creation
@bot.message_handler(commands='chattovcf')
async def chat_to_vcf_command(message: Message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, ChatToVcfState.waiting_for_contact_name, message.chat.id)
        await bot.reply_to(message, txt_chat_to_vcf)
    except Exception as e:
        logging.error("Error in chat_to_vcf_command: ", exc_info=True)

# Handle the contact name input
@bot.message_handler(state=ChatToVcfState.waiting_for_contact_name)
async def handle_contact_name(message: Message):
    try:
        contact_name = clean_string(message.text)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['contact_name'] = contact_name
            data['phone_numbers'] = []  # Initialize an empty list for phone numbers
        
        await bot.send_message(message.chat.id, 'Silakan masukkan nomor telepon kontak (ketik /done jika selesai):')
        await bot.set_state(message.from_user.id, ChatToVcfState.waiting_for_phone_number, message.chat.id)
    except Exception as e:
        logging.error("Error in handle_contact_name: ", exc_info=True)

# Handle phone number input
@bot.message_handler(state=ChatToVcfState.waiting_for_phone_number)
async def handle_phone_number(message: Message):
    try:
        if message.text == "/done":
            logging.info("Command /done received")
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                contact_name = data.get('contact_name')
                phone_numbers = data.get('phone_numbers', [])
            
            if not contact_name or not phone_numbers:
                return await bot.send_message(message.chat.id, "Nama kontak atau nomor telepon tidak ditemukan.")
            
            # Create VCF file with all phone numbers
            vcf_filename = clean_string(f"{contact_name}")
            file_path = create_vcf(contact_name, phone_numbers, vcf_filename)
            
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
        else:
            phone_number = clean_phone_number(message.text)
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['phone_numbers'].append(phone_number)  # Add phone number to list
            
            await bot.send_message(message.chat.id, 'Nomor telepon ditambahkan. Jika ingin menambah lagi, masukkan nomor lain, atau ketik /done jika sudah selesai.')
    except Exception as e:
        logging.error("Error in handle_phone_number: ", exc_info=True)
