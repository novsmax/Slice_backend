import os
import uuid
from fastapi import UploadFile
from typing import Optional
from pathlib import Path
from config import get_settings

settings = get_settings()

async def save_upload_file(upload_file: UploadFile, directory: str = None) -> Optional[str]:
    """
    Сохраняет загруженный файл в указанную директорию.
    
    Args:
        upload_file: Загруженный файл
        directory: Поддиректория в UPLOAD_DIR для сохранения файла (опционально)
    
    Returns:
        URL сохраненного файла или None в случае ошибки
    """
    # Проверяем, что это изображение
    if not upload_file.content_type.startswith("image/"):
        return None
    
    # Создаем уникальное имя файла
    file_extension = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Формируем путь для сохранения
    upload_dir = settings.UPLOAD_DIR
    if directory:
        upload_dir = os.path.join(upload_dir, directory)
    
    # Создаем директорию, если она не существует
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    
    # Полный путь к файлу
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Сохраняем файл
    try:
        contents = await upload_file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Формируем URL для доступа к файлу
        relative_path = os.path.join(directory or "", unique_filename) if directory else unique_filename
        file_url = f"/static/uploads/{relative_path}"
        
        return file_url
    except Exception as e:
        print(f"Error saving file: {e}")
        return None