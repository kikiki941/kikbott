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
    filename = State()  # State to handle filename input
    name = State()  # State to handle vcf file name input
    cname = State()  # State to handle contact name input
    totalc = State()  # State to handle total contacts input
    totalf = State()  # State to handle total files input
    change_name_prompt = State()  # State for prompt if file names should change
    change_every = State()  # State for setting how often to change file names
    change_limit = State()  # State for setting the limit of name changes
    new_name_1 = State()  # State for first new file name
    new_cname_1 = State()  # State for first new contact name
    new_name_2 = State()  # State for second new file name
    new_cname_2 = State()  # State for second new contact name
