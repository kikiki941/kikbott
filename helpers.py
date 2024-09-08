import pandas as pd

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

def check_number(path):
    numbers = []
    logging.info(f"Membaca file: {path}")

    try:
        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            if line.startswith('TEL'):
                number = line.split(':')[-1].replace('+', '').replace(' ', '')
                logging.info(f"Nomor ditemukan: {number}")
                if number.isdigit():
                    numbers.append(number)

    except Exception as e:
        logging.error(f"Kesalahan saat membaca file: {e}")

    if not numbers:
        logging.warning("Tidak ada nomor yang ditemukan dalam file.")
        return None

    logging.info(f"Jumlah nomor yang ditemukan: {len(numbers)}")
    return numbers

    
def pecah_txt(data):
    numbers = check_number(data['filename'])
    split_number = split(numbers, data['totalc'])
    countf = 0
    files = []

    for numbers in split_number:
        countf += 1
        txt_name = f"files/{data['name']}_{countf}.txt"
        files.append(txt_name)

        with open(txt_name, 'w', encoding='utf-8') as file:
            file.write("\n".join(numbers) + "\n")

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
    logging.info(f"Mulai mengonversi file VCF: {data['filename']}")

    # Membaca nomor telepon dari file VCF
    numbers = check_number(data['filename'])
    if not numbers:
        logging.error("Tidak ada nomor telepon yang ditemukan dalam file VCF.")
        return None
    
    split_number = split(numbers, data['totalc'])
    
    countc = 0
    countf = 0
    txt_file_name = f"files/{data['name']}.txt"
    
    logging.info(f"File TXT akan disimpan sebagai: {txt_file_name}")
    
    try:
        with open(txt_file_name, 'w', encoding='utf-8') as txt_file:
            for numbers in split_number:
                for number in numbers:
                    countc += 1
                    txt_file.write(f"{number}\n")
                countf += 1
                if countf >= data['totalf']:
                    break

        logging.info(f"File TXT {txt_file_name} berhasil dibuat.")
        return txt_file_name
    except Exception as e:
        logging.error(f"Kesalahan saat membuat file TXT: {e}")
        return None
    
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
