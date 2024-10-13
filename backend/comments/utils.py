import base64
import os
import uuid
from django.core.files.base import ContentFile
from django.utils.text import slugify

from rest_framework.exceptions import ValidationError


def image_file(instance, filename):
    ext = filename.split(".")[-1]
    base_filename = slugify(".".join(filename.split(".")[:-1]))
    unique_filename = f"{base_filename}_{uuid.uuid4().hex}.{ext}"
    return os.path.join("chat/images", unique_filename)


def convert_base64_to_image(image_base64):
    try:
        format, imgstr = image_base64.split(';base64,') 
        ext = format.split('/')[-1]  # Получаем расширение файла
        return ContentFile(base64.b64decode(imgstr), name=f'image.{ext}')
    except Exception as e:
        raise ValidationError("Invalid image data.")