import os
import logging
from telebot.types import Message

from bot import bot
from helpers import save_vcf  # Ganti fungsi save
from state import ChatToVcfState  # Sesuaikan nama state

# Pastikan direktori untuk menyimpan file ada
if not os.path.exists('files'):
    os.makedirs('files')

# Handler untuk perintah /chattovcf
@bot.message_handler(commands=['chattovcf'])
async def chat_to_vcf_command(message: Message):
    try:
        logging.info(f"User {message.from_user.id} memulai perintah /chattovcf")
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, ChatToVcfState.waiting_for_admin_contact, message.chat.id)
        await bot.reply_to(message, "Masukkan nama kontak admin")
    except Exception as e:
        logging.error("Error in chat_to_vcf_command: ", exc_info=True)

# Handler untuk menerima input nama kontak admin
@bot.message_handler(state=ChatToVcfState.waiting_for_admin_contact)
async def handle_admin_contact(message: Message):
    try:
        admin_contact_name = message.text
        logging.info(f"Nama kontak admin diterima: {admin_contact_name}")
        
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['admin_contact_name'] = admin_contact_name

        await bot.set_state(message.from_user.id, ChatToVcfState.waiting_for_admin_phone_numbers, message.chat.id)
        await bot.send_message(message.chat.id, "Kirim nomor telepon kontak admin (masukkan nomor dalam baris terpisah, tekan enter di antara nomor), lalu klik /done jika sudah selesai.")
    except Exception as e:
        logging.error("Error in handle_admin_contact: ", exc_info=True)

# Handler untuk menerima nomor telepon admin
@bot.message_handler(state=ChatToVcfState.waiting_for_admin_phone_numbers)
async def handle_admin_phone_numbers(message: Message):
    try:
        input_text = message.text
        
        if input_text.lower() == '/done':
            await bot.set_state(message.from_user.id, ChatToVcfState.waiting_for_navy_contact, message.chat.id)
            await bot.send_message(message.chat.id, "Masukkan nama kontak navy.")
        else:
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                phone_numbers = input_text.split('\n')
                numbered_contacts = [f"{data['admin_contact_name']} {i+1}" for i in range(len(phone_numbers))]
                contact_list = list(zip(numbered_contacts, phone_numbers))

                if 'admin_contacts' in data:
                    data['admin_contacts'] += contact_list
                else:
                    data['admin_contacts'] = contact_list

            await bot.send_message(message.chat.id, 'Nomor telepon admin ditambahkan. Kirim nomor lagi atau ketik /done jika sudah selesai.')
    except Exception as e:
        logging.error("Error in handle_admin_phone_numbers: ", exc_info=True)

# Handler untuk menerima input nama kontak navy
@bot.message_handler(state=ChatToVcfState.waiting_for_navy_contact)
async def handle_navy_contact(message: Message):
    try:
        navy_contact_name = message.text
        logging.info(f"Nama kontak navy diterima: {navy_contact_name}")
        
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['navy_contact_name'] = navy_contact_name

        await bot.set_state(message.from_user.id, ChatToVcfState.waiting_for_navy_phone_numbers, message.chat.id)
        await bot.send_message(message.chat.id, "Kirim nomor telepon kontak navy (masukkan nomor dalam baris terpisah, tekan enter di antara nomor), lalu klik /done jika sudah selesai.")
    except Exception as e:
        logging.error("Error in handle_navy_contact: ", exc_info=True)

# Handler untuk menerima nomor telepon navy
@bot.message_handler(state=ChatToVcfState.waiting_for_navy_phone_numbers)
async def handle_navy_phone_numbers(message: Message):
    try:
        input_text = message.text
        
        if input_text.lower() == '/done':
            await bot.set_state(message.from_user.id, ChatToVcfState.waiting_for_filename, message.chat.id)
            await bot.send_message(message.chat.id, "Masukkan nama file untuk menyimpan kontak.")
        else:
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                phone_numbers = input_text.split('\n')
                numbered_contacts = [f"{data['navy_contact_name']} {i+1}" for i in range(len(phone_numbers))]
                contact_list = list(zip(numbered_contacts, phone_numbers))

                if 'navy_contacts' in data:
                    data['navy_contacts'] += contact_list
                else:
                    data['navy_contacts'] = contact_list

            await bot.send_message(message.chat.id, 'Nomor telepon navy ditambahkan. Kirim nomor lagi atau ketik /done jika sudah selesai.')
    except Exception as e:
        logging.error("Error in handle_navy_phone_numbers: ", exc_info=True)

# Handler untuk menerima nama file
@bot.message_handler(state=ChatToVcfState.waiting_for_filename)
async def handle_filename(message: Message):
    try:
        filename = message.text
        logging.info(f"Nama file diterima: {filename}")
        
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            all_contacts = data.get('admin_contacts', []) + data.get('navy_contacts', [])
            
            if not all_contacts:
                return await bot.send_message(message.chat.id, "Tidak ada kontak yang ditemukan.")
            
            vcf_content = "\n".join([f"BEGIN:VCARD\nVERSION:3.0\nFN:{name}\nTEL:{phone}\nEND:VCARD" for name, phone in all_contacts])

            file_path = save_vcf(vcf_content, f"{filename}.vcf")
            logging.info(f"File VCF {filename}.vcf berhasil dibuat untuk user {message.from_user.id}")

            await bot.send_message(message.chat.id, f'File VCF berhasil dibuat dengan nama: {filename}.vcf')

            # Kirim file VCF ke user
            with open(file_path, 'rb') as doc:
                await bot.send_document(message.chat.id, doc)

            # Hapus file lokal setelah dikirim
            os.remove(file_path)
            logging.info(f"File {filename}.vcf dihapus dari server.")
            
            await bot.delete_state(message.from_user.id, message.chat.id)
            logging.info(f"State dihapus untuk user {message.from_user.id}")
    except Exception as e:
        logging.error("Error in handle_filename: ", exc_info=True)
        await bot.send_message(message.chat.id, "Terjadi kesalahan saat membuat file VCF.")
