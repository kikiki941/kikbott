import logging
from datetime import datetime, timedelta
from telebot.types import Message

from bot import *
from message import txt_vip
from state import VipState

@bot.message_handler(commands='addvip')
async def addvip_command(message: Message):
  try:
    if message.from_user.id not in owner:
      return
    
    await bot.delete_state(message.from_user.id, message.chat.id)
    await bot.set_state(message.from_user.id, VipState.user_id, message.chat.id)
    await bot.reply_to(message, txt_vip)
  except Exception as e:
    logging.error("error: ", exc_info=True)

@bot.message_handler(state=VipState.user_id, is_digit=True)
async def userid_get(message: Message):
  try:
    await bot.send_message(message.chat.id, 'ID Pengguna diterima. Silakan masukan durasi VIP:')
    await bot.set_state(message.from_user.id, VipState.durasi, message.chat.id)
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
      data['user_id'] = message.text

  except Exception as e:
    logging.error("error: ", exc_info=True)

@bot.message_handler(state=VipState.durasi, is_digit=True)
async def durasi_get(message: Message):
  try:
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
      data['durasi'] = int(message.text)

      durasi = (datetime.now(wib) + timedelta(days=data['durasi'])).strftime(datetime_format)
      whitelist[data['user_id']] = durasi

      await bot.send_message(message.chat.id, f"Durasi diterima. Berhasil memasukkan <b>{data['user_id']}</b> ke daftar VIP expired dalam <b>{durasi}</b>")

    await bot.delete_state(message.from_user.id, message.chat.id)
  except Exception as e:
    logging.error("error: ", exc_info=True)

@bot.message_handler(state=VipState.user_id, is_digit=False)
@bot.message_handler(state=VipState.durasi, is_digit=False)
async def name_get(message: Message):
  try:
    await bot.send_message(message.chat.id, 'Masukkan angka')
  except Exception as e:
    logging.error("error: ", exc_info=True)
