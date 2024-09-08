import pandas as pd
import os
import re
import logging

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

def create_vcf(contact_name: str, phone_numbers: list) -> str:
    vcf = ''
    for idx, phone_number in enumerate(phone_numbers):
        vcf += f"BEGIN:VCARD\n"
        vcf += f"VERSION:3.0\n"
        vcf += f"N:Nama_{idx+1};;;\n"
        vcf += f"FN:Nama_{idx+1}\n"
        vcf += f"TEL;TYPE=CELL:+{phone_number}\n"
        vcf += f"END:VCARD\n"
    return vcf

def save_vcf(content: str, filename: str) -> str:
    file_path = f"files/{filename}.vcf"
    with open(file_path, 'w') as vcf_file:
        vcf_file.write(content)
    return file_path

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
