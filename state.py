from telebot.asyncio_handler_backends import State, StatesGroup
from enum import Enum
from states import StatesGroup, State

class Convert2State(StatesGroup):
    upload_file = State()         # Menunggu file .txt untuk diunggah
    file_name_change = State()    # Menunggu konfirmasi perubahan nama file
    file_name_count = State()     # Menunggu jumlah perubahan nama file
    file_names = State()          # Menunggu input nama file
    contact_names = State()       # Menunggu input nama kontak
    contacts_per_file = State()   # Menunggu jumlah kontak per file

class ConvertXlsImagesState(State):
    filename = State()
    name = State()

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
    filename = State()  # Menunggu input file .txt
    name = State()      # Menunggu input nama file
    cname = State()     # Menunggu input nama kontak
    totalc = State()    # Menunggu input jumlah kontak per file
    totalf = State()    # Menunggu input jumlah file
    change_name_prompt = State()  # Menunggu input apakah nama file akan berganti
    change_every = State()        # Menunggu input setiap berapa file nama akan berganti
    change_limit = State()        # Menunggu input batas pergantian nama
    new_name_1 = State()          # Menunggu input nama file baru
    contact_names = State()     

class HitungCtcState(StatesGroup):
    waiting_for_files = State()  # State where the bot is waiting for .vcf files

