import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import FileResponse, Http404
from django.conf import settings
from django.contrib import messages
from .forms import ContactForm, UploadXMLForm
from .utils import (
    save_contact_to_xml, get_all_contacts_from_xml,
    validate_xml_file, get_contacts_from_uploaded_xml,
    get_all_xml_files, generate_xml_filename, ensure_contacts_dir, get_contacts_xml_dir
)

def contact_form(request):
    """Форма для ввода контакта"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_data = form.cleaned_data
            if save_contact_to_xml(contact_data):
                messages.success(request, 'Контакт успешно сохранен!')
                return redirect('contact_list')
            else:
                messages.error(request, 'Ошибка при сохранении контакта')
    else:
        form = ContactForm()
    
    return render(request, 'contact_form.html', {'form': form})

def contact_list(request):
    """Список всех контактов из основного XML файла"""
    contacts = get_all_contacts_from_xml()
    
    context = {
        'contacts': contacts,
        'has_contacts': len(contacts) > 0
    }
    return render(request, 'contact_list.html', context)

def upload_xml(request):
    """Загрузка XML файла с контактами"""
    if request.method == 'POST':
        form = UploadXMLForm(request.POST, request.FILES)
        if form.is_valid():
            xml_file = request.FILES['xml_file']
            
            # Генерируем безопасное имя файла
            safe_filename = generate_xml_filename()
            upload_dir = ensure_contacts_dir()
            file_path = os.path.join(upload_dir, safe_filename)
            
            # Сохраняем файл
            with open(file_path, 'wb+') as destination:
                for chunk in xml_file.chunks():
                    destination.write(chunk)
            
            # Проверяем валидность XML
            if validate_xml_file(file_path):
                messages.success(request, f'Файл {xml_file.name} успешно загружен и проверен!')
                return redirect('xml_files_list')
            else:
                # Удаляем невалидный файл
                os.remove(file_path)
                messages.error(request, 'Файл не является валидным XML. Файл удален.')
                
    else:
        form = UploadXMLForm()
    
    return render(request, 'upload_xml.html', {'form': form})

def xml_files_list(request):
    """Список всех XML файлов и их содержимого"""
    xml_files = get_all_xml_files()
    
    # Для каждого файла получаем контакты
    files_data = []
    for file_info in xml_files:
        contacts = get_contacts_from_uploaded_xml(file_info['filepath'])
        file_info['contacts'] = contacts
        file_info['contacts_count'] = len(contacts)
        files_data.append(file_info)
    
    context = {
        'files_data': files_data,
        'has_files': len(files_data) > 0
    }
    return render(request, 'xml_files_list.html', context)

def view_xml_file(request, filename):
    """Просмотр содержимого конкретного XML файла"""
    contacts_dir = ensure_contacts_dir()
    file_path = os.path.join(contacts_dir, filename)
    
    if not os.path.exists(file_path):
        messages.error(request, 'Файл не найден')
        return redirect('xml_files_list')
    
    if not validate_xml_file(file_path):
        messages.error(request, 'Файл не является валидным XML')
        return redirect('xml_files_list')
    
    contacts = get_contacts_from_uploaded_xml(file_path)
    
    context = {
        'filename': filename,
        'contacts': contacts,
        'has_contacts': len(contacts) > 0
    }
    return render(request, 'xml_file_detail.html', context)

def download_xml_file(request, filename):
    """Скачивание XML файла"""
    contacts_dir = get_contacts_xml_dir()
    file_path = os.path.join(contacts_dir, filename)
    
    if not os.path.exists(file_path):
        messages.error(request, 'Файл не найден')
        return redirect('xml_files_list')
    
    try:
        # Проверяем, что файл является XML
        if not filename.endswith('.xml'):
            messages.error(request, 'Файл не является XML')
            return redirect('xml_files_list')
        
        # Открываем файл для чтения в бинарном режиме
        response = FileResponse(open(file_path, 'rb'))
        
        # Устанавливаем заголовки для скачивания
        response['Content-Type'] = 'application/xml'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Ошибка при скачивании файла: {str(e)}')
        return redirect('xml_files_list')