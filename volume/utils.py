import re
from typing import List

from unidecode import unidecode

from chapter.types import ChapterData
from utils import strip_string

from .types import VolumeData


def volume_data_factory(title: str, image_link: str, chapter_data_tags: List[ChapterData], order: int) -> VolumeData:
    """Create Volume Data"""
    return {'title': strip_string(title), 'cover_link': image_link, 'chapters_data': chapter_data_tags, 'order': order}


def generate_volume_title(volume_title: str, series: str, order: int) -> str:
    """ Generate title """
    return ' '.join([f"[{order}]", series, volume_title])


def generate_volume_filename(title: str) -> str:
    """ Generate filename """
    return re.sub(r'[^A-Z\d]+', ' ', unidecode(title), flags=re.IGNORECASE).title().strip()
