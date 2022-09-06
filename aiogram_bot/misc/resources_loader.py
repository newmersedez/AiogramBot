import pandas as pd

from aiogram_bot.misc.db_connection import session_scope
from aiogram_bot.config.bot_config import RESOURCES_PATH
from aiogram_bot.models.user_favorites import UserFavorites


class ResourceType:
    Simple = 'simple_type'
    Complex = 'complex_type'


class ResourceLoader:
    @staticmethod
    async def load_resources(resource_type: str, resource_index=0, resource_path=RESOURCES_PATH):
        sheet = None
        if resource_type == ResourceType.Simple:
            sheet = pd.read_excel(resource_path, sheet_name=0)
        elif resource_type == ResourceType.Complex:
            sheet = pd.read_excel(resource_path, sheet_name=1)
        simple_resources_sheet = [[*elem] for elem in sheet.values]
        return simple_resources_sheet[resource_index]

    @staticmethod
    async def load_favorites(user_id: int, resource_index=0):
        with session_scope() as s:
            request = s.query(UserFavorites).filter(UserFavorites.user_id == user_id).all()
            data = [data.resource.split(',') for data in request]
            if resource_index == len(data):
                raise Exception('Reached last index')
            return data[resource_index]
