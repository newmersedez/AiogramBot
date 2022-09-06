import pandas as pd

from aiogram_bot.misc.db_connection import session_scope
from aiogram_bot.config.bot_config import RESOURCES_PATH
from aiogram_bot.models.user_favorites import UserFavorites


class ResourceType:
    Simple = 'simple_type'
    Complex = 'complex_type'
    Help = 'help_type'


class ResourceLoader:
    @staticmethod
    async def __read_sheet(resource_type: str, resource_path: str):
        sheet = None
        if resource_type == ResourceType.Simple:
            sheet = pd.read_excel(resource_path, sheet_name=0)
        elif resource_type == ResourceType.Complex:
            sheet = pd.read_excel(resource_path, sheet_name=1)
        elif resource_type == ResourceType.Help:
            sheet = pd.read_excel(resource_path, sheet_name=2)
        return sheet

    @staticmethod
    async def get_images_count(resource_type: str, resource_path=RESOURCES_PATH):
        sheet = await ResourceLoader.__read_sheet(resource_type, resource_path)
        return len(sheet)

    @staticmethod
    async def get_favorites_count(user_id: int):
        with session_scope() as s:
            request = s.query(UserFavorites).filter(UserFavorites.user_id == user_id).all()
            return len(request)

    @staticmethod
    async def load_images(resource_type: str, resource_index=0, resource_path=RESOURCES_PATH):
        sheet = await ResourceLoader.__read_sheet(resource_type, resource_path)
        if sheet is None:
            return None, False

        last_index = False
        simple_resources_sheet = [[*elem] for elem in sheet.values]
        if resource_index == len(simple_resources_sheet) - 1:
            last_index = True
        return simple_resources_sheet[resource_index], last_index

    @staticmethod
    async def load_favorites(user_id: int, resource_index=0):
        with session_scope() as s:
            last_index = False
            request = s.query(UserFavorites).filter(UserFavorites.user_id == user_id).all()
            if request is None or len(request) == 0:
                return None, last_index
            data = [data.resource.split(',') for data in request]
            if resource_index == len(data) - 1:
                last_index = True
            return data[resource_index], last_index
