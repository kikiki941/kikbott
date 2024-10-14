import logging
from telebot.types import Message
from bot import bot
from helpers import generate_vcf_files
from state import Convert2State

@bot.message_handler(commands=['convert2'])
async def convert2_command(message: Message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, Convert2State.upload_file, message.chat.id)
        await bot.reply_to(message, "Silakan kirim file .txt yang berisi daftar nomor telepon.")
    except Exception as e:
        logging.error(f"Error in convert2_command: {e}", exc_info=True)

@bot.message_handler(state=Convert2State.upload_file, content_types=['document'])
async def receive_txt_file(message: Message):
    try:
        if not message.document.file_name.endswith(".txt"):
            return await bot.send_message(message.chat.id, "Kirim file dalam format .txt")
        
        file_info = await bot.get_file(message.document.file_id)
        file_path = f"files/{message.document.file_name}"
        
        downloaded_file = await bot.download_file(file_info.file_path)
        with open(file_path, 'wb') as file:
            file.write(downloaded_file)
        
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['file_path'] = file_path
        
        await bot.set_state(message.from_user.id, Convert2State.file_name_change, message.chat.id)
        await bot.send_message(message.chat.id, "Apakah nama file akan berganti? (y/t)")
    except Exception as e:
        logging.error(f"Error in receive_txt_file: {e}", exc_info=True)

@bot.message_handler(state=Convert2State.file_name_change)
async def file_name_change_response(message: Message):
    try:
        response = message.text.lower()
        if response not in ['y', 't']:
            return await bot.send_message(message.chat.id, "Jawaban harus y atau t.")
        
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['file_name_change'] = response == 'y'
        
        if response == 'y':
            await bot.set_state(message.from_user.id, Convert2State.file_name_count, message.chat.id)
            await bot.send_message(message.chat.id, "Berapa kali nama file akan berganti? (1-10)")
        else:
            await bot.set_state(message.from_user.id, Convert2State.file_names, message.chat.id)
            await bot.send_message(message.chat.id, "Masukkan nama file pertama:")
    except Exception as e:
        logging.error(f"Error in file_name_change_response: {e}", exc_info=True)

@bot.message_handler(state=Convert2State.file_name_count)
async def file_name_count_response(message: Message):
    try:
        count = int(message.text)
        if count < 1 or count > 10:
            return await bot.send_message(message.chat.id, "Jumlah harus antara 1 hingga 10.")
        
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['file_name_count'] = count
        
        await bot.set_state(message.from_user.id, Convert2State.file_names, message.chat.id)
        await bot.send_message(message.chat.id, "Masukkan nama file pertama:")
    except Exception as e:
        logging.error(f"Error in file_name_count_response: {e}", exc_info=True)

@bot.message_handler(state=Convert2State.file_names)
async def file_names_response(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if 'file_names_list' not in data:
                data['file_names_list'] = []
            
            data['file_names_list'].append(message.text)
            
            if len(data['file_names_list']) < data.get('file_name_count', 1):
                await bot.send_message(message.chat.id, "Masukkan nama file berikutnya:")
            else:
                await bot.set_state(message.from_user.id, Convert2State.contact_names, message.chat.id)
                await bot.send_message(message.chat.id, "Masukkan nama kontak untuk file pertama:")
    except Exception as e:
        logging.error(f"Error in file_names_response: {e}", exc_info=True)

@bot.message_handler(state=Convert2State.contact_names)
async def contact_names_response(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if 'contact_names_list' not in data:
                data['contact_names_list'] = []

            data['contact_names_list'].append(message.text)
            
            if len(data['contact_names_list']) < len(data['file_names_list']):
                await bot.send_message(message.chat.id, f"Masukkan nama kontak untuk file berikutnya (file {len(data['contact_names_list']) + 1}):")
            else:
                await bot.set_state(message.from_user.id, Convert2State.contacts_per_file, message.chat.id)
                await bot.send_message(message.chat.id, "Berapa jumlah kontak per file?")
    except Exception as e:
        logging.error(f"Error in contact_names_response: {e}", exc_info=True)

@bot.message_handler(state=Convert2State.contacts_per_file)
async def contacts_per_file_response(message: Message):
    try:
        count = int(message.text)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['contacts_per_file'] = count
        
        await bot.send_message(message.chat.id, "Berapa jumlah file yang diinginkan?")
        await bot.set_state(message.from_user.id, Convert2State.total_files, message.chat.id)
    except Exception as e:
        logging.error(f"Error in contacts_per_file_response: {e}", exc_info=True)

@bot.message_handler(state=Convert2State.total_files)
async def total_files_response(message: Message):
    try:
        count = int(message.text)
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['total_files'] = count
        
        await generate_vcf_files(data)
        await bot.send_message(message.chat.id, "Proses konversi selesai, file VCF sedang dikirim.")
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error(f"Error in total_files_response: {e}", exc_info=True)

