from telebot.asyncio_handler_backends import State, StatesGroup
from enum import Enum

class ConvertState(StatesGroup):
    filename = State()
    name = State()
    cname = State()
    totalc = State()
    totalf = State()

class ConvertVcfState(StatesGroup):
    filename = State()
    name = State()
    cname = State()
    totalc = State()
    totalf = State()

class ConvertXlsxState(StatesGroup):
    filename = State()
    name = State()

class PecahTxtState(StatesGroup):
    filename = State()
    name = State()
    totaln = State()
    totalf = State()

class PecahVcfState(StatesGroup):
    filename = State()
    name = State()
    totalc = State()
    totalf = State()

class ConvertVcfToTxtState(StatesGroup):
    filename = State()
    name = State()

class GabungVcfState(StatesGroup):
    waiting_for_files = State()  
    name = State()

class ChatToTxtState(StatesGroup):
    waiting_for_text_input = State()

class WiFiWpsWpaState(StatesGroup):
    waiting_for_interface = State()  # User input interface
    waiting_for_bssid = State()  # User input BSSID
    waiting_for_channel = State()  # User input channel

class GabungTxtState(StatesGroup):
    waiting_for_files = State()  # Menunggu pengguna mengunggah file
    name = State() 
    
class HapusSpasiState(StatesGroup):
    waiting_for_file = State()

class VipState(StatesGroup):
  user_id = State()
  durasi = State()

class kolomState(StatesGroup):
    waiting_for_file = State()

class Convert2State(StatesGroup):
    filename = State()  # Menunggu pengguna mengirimkan file txt
    name = State()      # Menunggu pengguna memasukkan nama file vcf
    cname = State()     # Menunggu pengguna memasukkan nama kontak
    totalc = State()    # Menunggu pengguna memasukkan jumlah kontak per file
    totalf = State()    # Menunggu pengguna memasukkan jumlah file
    change_name_prompt = State()  # Menunggu pengguna memilih apakah nama file akan berganti
    change_every = State()  # Menunggu input jumlah file sebelum nama berganti
    change_limit = State()  # Menunggu input batas pergantian nama
    new_name_1 = State()  # Menunggu input nama file baru
    new_name_2 = State()  # Menunggu input nama file baru berikutnya
