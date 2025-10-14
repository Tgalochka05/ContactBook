import os
import uuid
import xml.etree.ElementTree as ET
from django.conf import settings
from xml.etree.ElementTree import ParseError

def get_contacts_xml_dir():
    """Возвращает путь к директории для XML файлов контактов"""
    return os.path.join(settings.MEDIA_ROOT, 'contacts_xml')

def ensure_contacts_dir():
    """Создает директорию для XML файлов контактов"""
    contacts_dir = get_contacts_xml_dir()
    if not os.path.exists(contacts_dir):
        os.makedirs(contacts_dir)
    return contacts_dir

def generate_xml_filename():
    """Генерирует уникальное имя для XML файла"""
    return f"contacts_{uuid.uuid4().hex}.xml"

def save_contact_to_xml(contact_data):
    """Сохраняет контакт в XML файл"""
    contacts_dir = ensure_contacts_dir()
    file_path = os.path.join(contacts_dir, 'contacts.xml')  # ← Используем contacts.xml как основной файл
    
    try:
        if os.path.exists(file_path):
            # Если файл существует, добавляем новый контакт
            tree = ET.parse(file_path)
            root = tree.getroot()
        else:
            # Создаем новый файл
            root = ET.Element('Contacts')
            tree = ET.ElementTree(root)
        
        # Создаем элемент контакта
        contact = ET.Element('Contact')
        
        ET.SubElement(contact, 'Name').text = contact_data['name']
        ET.SubElement(contact, 'Phone').text = contact_data['phone']
        ET.SubElement(contact, 'Email').text = contact_data['email']
        if contact_data.get('address'):
            ET.SubElement(contact, 'Address').text = contact_data['address']
        
        root.append(contact)
        
        # Сохраняем файл
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
        return True
        
    except Exception as e:
        print(f"Error saving to XML: {e}")
        return False

def get_all_contacts_from_xml():
    """Получает все контакты из основного XML файла"""
    contacts_dir = get_contacts_xml_dir()
    file_path = os.path.join(contacts_dir, 'contacts.xml')
    contacts = []
    
    if not os.path.exists(file_path):
        return contacts
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        for contact_elem in root.findall('Contact'):
            contact = {
                'name': contact_elem.find('Name').text if contact_elem.find('Name') is not None else '',
                'phone': contact_elem.find('Phone').text if contact_elem.find('Phone') is not None else '',
                'email': contact_elem.find('Email').text if contact_elem.find('Email') is not None else '',
                'address': contact_elem.find('Address').text if contact_elem.find('Address') is not None else '',
            }
            contacts.append(contact)
            
    except (ParseError, ET.ParseError) as e:
        print(f"Error parsing XML: {e}")
    
    return contacts

def validate_xml_file(file_path):
    """Проверяет валидность XML файла"""
    try:
        ET.parse(file_path)
        return True
    except (ParseError, ET.ParseError):
        return False

def get_contacts_from_uploaded_xml(file_path):
    """Извлекает контакты из загруженного XML файла"""
    contacts = []
    
    if not validate_xml_file(file_path):
        return contacts
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Поддерживаем разные структуры XML
        for contact_elem in root.findall('.//Contact'):
            contact = {}
            
            name_elem = contact_elem.find('Name')
            phone_elem = contact_elem.find('Phone')
            email_elem = contact_elem.find('Email')
            address_elem = contact_elem.find('Address')
            
            if name_elem is not None:
                contact['name'] = name_elem.text
            if phone_elem is not None:
                contact['phone'] = phone_elem.text
            if email_elem is not None:
                contact['email'] = email_elem.text
            if address_elem is not None:
                contact['address'] = address_elem.text
            
            if contact:  # Добавляем только если есть хотя бы одно поле
                contacts.append(contact)
                
    except Exception as e:
        print(f"Error reading uploaded XML: {e}")
    
    return contacts

def get_all_xml_files():
    """Возвращает список всех XML файлов в директории"""
    contacts_dir = ensure_contacts_dir()
    xml_files = []
    
    for filename in os.listdir(contacts_dir):
        if filename.endswith('.xml'):
            file_path = os.path.join(contacts_dir, filename)
            file_info = {
                'filename': filename,
                'filepath': file_path,
                'size': os.path.getsize(file_path),
                'is_valid': validate_xml_file(file_path)
            }
            xml_files.append(file_info)
    
    return xml_files