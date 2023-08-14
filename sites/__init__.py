import importlib
import os
from inspect import isabstract, isclass
from pathlib import Path
from typing import List, Tuple

from pipe import select, where

from .site_abstract import Site


def __get_sites() -> Tuple[Site]:
    sites_: List[Site] = []

    SITES_FOLDER = 'customs'
    sites_path = Path(__file__).absolute().parent / SITES_FOLDER

    site_filenames = list(os.listdir(sites_path)
                          | where(lambda x: x.endswith('.py'))
                          | select(lambda x: x.removesuffix('.py')))

    for filename in site_filenames:
        module = importlib.import_module('.' + filename, 'sites.customs')

        for value in module.__dict__.values():
            if isclass(value) and issubclass(value, Site) and not isabstract(value):
                sites_.append(value)

    return tuple(sites_)


sites = __get_sites()
