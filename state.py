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
    filename = State()  # State untuk menerima file
    name = State()  # State untuk nama file
    cname = State()  # State untuk nama kontak
    totalc = State()  # State untuk jumlah kontak per file
    totalf = State()  # State untuk jumlah file
    change_name_prompt = State()  # State untuk perubahan nama file
    change_every = State()  # State untuk setiap berapa file nama file berganti
    change_limit = State()  # State untuk batas pergantian nama file
    new_name_1 = State()  # State untuk nama file baru 1
    new_name_2 = State()  # State untuk nama file baru 2
    new_cname_1 = State()  # State untuk nama kontak baru 1
