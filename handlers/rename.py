import logging
from telebot.types import Message
from telebot.apihelper import ApiTelegramException
from bot import bot
from message import *
from helpers import rename_vcf_files_and_contacts
from state import RenameState  # Changed here

@bot.message_handler(commands='rename')
async def rename_command(message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, RenameState.file_names, message.chat.id)  # Changed here
        await bot.reply_to(message, "Silakan kirim file .vcf yang ingin diubah.")
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=RenameState.file_names, content_types=['document'])  # Changed here
async def vcf_file_get(message: Message):
    try:
        if not message.document.file_name.endswith(".vcf"):
            return await bot.send_message(message.chat.id, "Kirim file .vcf yang valid.")

        file = await bot.get_file(message.document.file_id)
        filename = f"files/{message.document.file_name}"
        logging.info(f"File akan disimpan dengan nama: {filename}")

        downloaded_file = await bot.download_file(file.file_path)
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)
        logging.info(f"File berhasil diunduh dan disimpan sebagai: {filename}")

        await bot.send_message(message.chat.id, 'Masukkan prefix nama file baru:')
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['vcf_file'] = filename

        await bot.set_state(message.from_user.id, RenameState.new_file_prefix, message.chat.id)  # Changed here
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=RenameState.new_file_prefix)  # Changed here
async def new_file_prefix_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['new_file_prefix'] = message.text

        await bot.send_message(message.chat.id, 'Masukkan nama kontak untuk file .vcf:')
        await bot.set_state(message.from_user.id, RenameState.contact_name, message.chat.id)  # Changed here
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=RenameState.contact_name)  # Changed here
async def contact_name_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['contact_name'] = message.text

        await bot.send_message(message.chat.id, 'Masukkan angka untuk memulai penomoran:')
        await bot.set_state(message.from_user.id, RenameState.start_number, message.chat.id)  # Changed here
    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=RenameState.start_number, is_digit=True)  # Changed here
async def start_number_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['start_number'] = int(message.text)

        # Get the file path from the saved data
        vcf_file_path = data['vcf_file']

        # Call the rename function
        rename_vcf_files_and_contacts([vcf_file_path], data['new_file_prefix'], data['contact_name'], data['start_number'])

        await bot.send_message(message.chat.id, "Proses rename selesai!")
        await bot.delete_state(message.from_user.id, message.chat.id)

    except Exception as e:
        logging.error("error: ", exc_info=True)

@bot.message_handler(state=RenameState.start_number, is_digit=False)  # Changed here
async def invalid_start_number(message: Message):
    try:
        await bot.send_message(message.chat.id, 'Masukkan angka yang valid untuk memulai penomoran.')
    except Exception as e:
        logging.error("error: ", exc_info=True)
