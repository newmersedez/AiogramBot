import pandas as pd
from aiogram_bot.config.bot_config import RESOURCES_PATH


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
