from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MainMenuOptions:
    categories = "🔎 Find by categories"
    tags = "📌 Find by tags (in each category)"
    all = "🗂 All"
    add = "🗑 Add any trash"
    add_password = "🔑 Add password"
    search_password = "🔏 Search password"


class MainMenu:
    menu = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=MainMenuOptions.categories),
         KeyboardButton(text=MainMenuOptions.tags)],
        [KeyboardButton(text=MainMenuOptions.all)],
        [KeyboardButton(text=MainMenuOptions.add)],
        [KeyboardButton(text=MainMenuOptions.add_password),
         KeyboardButton(text=MainMenuOptions.search_password)],
    ])
    is_categories = lambda m: m.text == MainMenuOptions.categories
    is_tags = lambda m: m.text == MainMenuOptions.tags
    is_all = lambda m: m.text == MainMenuOptions.all
    is_adding = lambda m: m.text == MainMenuOptions.add
    is_search_password = lambda m: m.text == MainMenuOptions.search_password
    is_add_password = lambda m: m.text == MainMenuOptions.add_password


class OptionsMenu:
    @staticmethod
    def generate_menu(options: List[str]):
        builder = InlineKeyboardBuilder()
        for category in options:
            builder.button(text=category, callback_data=category)
        builder.adjust(2)

        return builder.as_markup()
