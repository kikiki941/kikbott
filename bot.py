from telebot import logger
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import *
from telebot.asyncio_storage import StateMemoryStorage
from logging import ERROR

bot_token = '7370223134:AAFydWlZPdTHP5q4C43lHKDCjMIBwPCVIzE'
bot = AsyncTeleBot(bot_token, parse_mode='HTML', state_storage=StateMemoryStorage())

bot.add_custom_filter(StateFilter(bot))
bot.add_custom_filter(IsDigitFilter())

logger.setLevel(ERROR)
