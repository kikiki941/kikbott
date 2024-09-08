import logging
import os
from telebot.types import Message
from telebot.apihelper import ApiTelegramException

from bot import bot
from message import txt_chat_to_vcf
from helpers import create_vcf, clean_phone_number

from state import ChatToVcfState

# Ensure the 'files' directory exists
if not os.path.exists('files'):
    os.makedirs('files')

# Start command for creating a VCF
@bot.message_handler(commands='chattovcf')
async def chat_to_vcf_command(message: Message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, ChatToVcfState.waiting_for_contact_name, message.chat.id)
        await bot.reply_to(message, "Silakan masukkan nama kontak:")
    except Exception as e:
        logging.error("Error in chat_to_vcf_command: ", exc_info=True)

# Handle the contact name input
@bot.message_handler(state=ChatToVcfState.waiting_for_contact_name)
async def handle_contact_name(message: Message):
    try:
        contact_name = message.text.strip()
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['contact_name'] = contact_name
            data['phone_numbers'] = []
        
        await bot.send_message(message.chat.id, 'Silakan masukkan nomor telepon kontak. Jika ingin menambah lagi, masukkan nomor lain, atau ketik /done jika sudah selesai:')
        await bot.set_state(message.from_user.id, ChatToVcfState.waiting_for_phone_number, message.chat.id)
    except Exception as e:
        logging.error("Error in handle_contact_name: ", exc_info=True)

# Handle phone numbers input
@bot.message_handler(state=ChatToVcfState.waiting_for_phone_number)
async def handle_phone_number(message: Message):
    try:
        phone_number = message.text.strip()

        if phone_number == "/done":
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                contact_name = data.get('contact_name')
                phone_numbers = data.get('phone_numbers', [])

            if not phone_numbers:
                await bot.send_message(message.chat.id, "Anda belum memasukkan nomor telepon apa pun. Silakan tambahkan nomor.")
                return
            
            # Create VCF file with multiple numbers
            vcf_filename = f"{contact_name}.vcf"
            file_path = create_vcf(contact_name, phone_numbers)
            
            await bot.send_message(message.chat.id, f'File VCF berhasil dibuat dengan nama: {vcf_filename}')
            
            # Send the VCF file
            try:
                with open(file_path, 'rb') as doc:
                    await bot.send_document(message.chat.id, doc)
            except ApiTelegramException as e:
                logging.error("API exception: ", exc_info=True)
                await bot.send_message(message.chat.id, "Terjadi kesalahan saat mengirim file.")
            
            os.remove(file_path)
            await bot.delete_state(message.from_user.id, message.chat.id)
        else:
            # Clean the phone number and add to the list
            clean_phone = clean_phone_number(phone_number)
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['phone_numbers'].append(clean_phone)
            
            await bot.send_message(message.chat.id, f'Nomor {clean_phone} ditambahkan. Tambahkan lagi, atau ketik /done jika sudah selesai.')
    except Exception as e:
        logging.error("Error in handle_phone_number: ", exc_info=True)
