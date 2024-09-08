from bot import bot
from telebot.types import BotCommand

async def set_commands():
  await bot.delete_my_commands(scope=None, language_code=None)
  await bot.set_my_commands(
    commands=[
      BotCommand('convert', 'Mengonversi file dari format TXT ke VCF'),
      BotCommand('pecahvcf', 'Membagi satu file VCF menjadi beberapa file'),
      BotCommand('pecahtxt', 'Membagi satu file TXT menjadi beberapa file'),
      BotCommand('convertxlsx', 'Mengonversi file dari format XLSX ke TXT'),
      BotCommand('convertvcf', 'Mengonversi file dari format XLSX ke VCF'),
      BotCommand('convertvcf_to_txt', 'mengonversi file dari format vcf ke txt'),
      BotCommand('gabungvcf', 'Menggabungkan beberapa file vcf menjadi 1'),
      BotCommand('chattovcf', 'Mengonversi chat ke vcf '),
      BotCommand('cancel', 'Membatalkan proses'),
    ],
  )
