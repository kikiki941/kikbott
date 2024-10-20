import logging
import os
from re import findall
from asyncio import sleep
from telebot.types import Message
from telebot.apihelper import ApiTelegramException
from bot import bot
from message import *
from helpers import rename_vcf_files_and_contacts
from state import RenameState

@bot.message_handler(commands='rename')
async def rename_command(message: Message):
    try:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.set_state(message.from_user.id, RenameState.directory, message.chat.id)
        await bot.reply_to(message, "Masukkan direktori tempat file .vcf berada:")
    except Exception as e:
        logging.error("Error in rename_command: ", exc_info=True)

@bot.message_handler(state=RenameState.directory)
async def directory_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['directory'] = message.text.strip()

        await bot.send_message(message.chat.id, "Masukkan prefix nama file baru:")
        await bot.set_state(message.from_user.id, RenameState.new_file_prefix, message.chat.id)
    except Exception as e:
        logging.error("Error in directory_get: ", exc_info=True)

@bot.message_handler(state=RenameState.new_file_prefix)
async def new_file_prefix_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['new_file_prefix'] = message.text.strip()

        await bot.send_message(message.chat.id, "Masukkan nama kontak baru:")
        await bot.set_state(message.from_user.id, RenameState.new_contact_name, message.chat.id)
    except Exception as e:
        logging.error("Error in new_file_prefix_get: ", exc_info=True)

@bot.message_handler(state=RenameState.new_contact_name)
async def new_contact_name_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['new_contact_name'] = message.text.strip()

        await bot.send_message(message.chat.id, "Masukkan angka untuk memulai penomoran:")
        await bot.set_state(message.from_user.id, RenameState.start_number, message.chat.id)
    except Exception as e:
        logging.error("Error in new_contact_name_get: ", exc_info=True)

@bot.message_handler(state=RenameState.start_number, is_digit=True)
async def start_number_get(message: Message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['start_number'] = int(message.text.strip())

            # Call the renaming function with the user-provided directory
            directory = data['directory']
            new_file_prefix = data['new_file_prefix']
            new_contact_name = data['new_contact_name']
            start_number = data['start_number']

            # Call the renaming function
            rename_vcf_files_and_contacts(directory, new_file_prefix, new_contact_name, start_number)

        await bot.send_message(message.chat.id, "Proses penggantian nama file dan kontak selesai!")
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        logging.error("Error in start_number_get: ", exc_info=True)

@bot.message_handler(state=RenameState.start_number, is_digit=False)
async def invalid_input(message: Message):
    try:
        await bot.send_message(message.chat.id, 'Masukkan angka yang valid.')
    except Exception as e:
        logging.error("Error in invalid_input: ", exc_info=True)
