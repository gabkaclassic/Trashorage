from typing import List

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from views.phrases import (
    selecting_category,
    selecting_tags,
    tags_not_found,
    categories_not_found,
    nothing_found,
    objects_found
)
from views.menus import MainMenu, OptionsMenu
from aiogram.fsm.context import FSMContext as Context
from db.opensearch.storage import storage
from aiogram.fsm.state import StatesGroup, State
from bot import bot

router = Router()


class SearchStates(StatesGroup):
    tags = State()
    category = State()


@router.message(MainMenu.is_tags)
async def to_tags(message: Message, state: Context):
    await state.set_state(state=SearchStates.tags)
    tags = await storage.get_tags(message.chat.id)

    if tags:
        await message.answer(
            text=selecting_tags,
            reply_markup=OptionsMenu.generate_menu(tags)
        )
    else:
        await message.answer(text=tags_not_found)


@router.message(MainMenu.is_all)
async def get_all(message: Message, state: Context):
    objects = await storage.search_by_user(message.chat.id)
    await search_result(objects, message, state)


@router.message(MainMenu.is_categories)
async def to_categories(message: Message, state: Context):
    await state.set_state(state=SearchStates.category)
    categories = await storage.get_categories(message.chat.id)

    if categories:
        await message.answer(
            text=selecting_category,
            reply_markup=OptionsMenu.generate_menu(categories)
        )
    else:
        await message.answer(text=categories_not_found)


@router.callback_query(SearchStates.tags)
async def search_by_tags(callback: CallbackQuery, state: Context):
    tags = callback.data.split()
    await search_by_tags_answer(callback.message, tags, state)


@router.message(SearchStates.tags)
async def search_by_tags(message: Message, state: Context):
    tags = message.text.split()
    await search_by_tags_answer(message, tags, state)


async def search_by_tags_answer(message: Message, tags: List[str], state: Context):
    objects = await storage.search_by_tags(message.chat.id, tags, (await state.get_data()).get('category'))
    await search_result(objects, message, state)


async def search_result(objects: List[str], message: Message, state: Context):
    if objects:
        await message.answer(text=objects_found)
        for object in objects:
            await bot.forward_message(
                message_id=object,
                chat_id=message.chat.id,
                from_chat_id=message.chat.id
            )
    else:
        await message.answer(text=nothing_found)

    await state.clear()


@router.message(SearchStates.category)
async def search_by_categories(message: Message, state: Context):
    category = message.text
    await search_by_categories_answer(category, message, state)


@router.callback_query(SearchStates.category)
async def search_by_categories(callback: CallbackQuery, state: Context):
    category = callback.data
    await search_by_categories_answer(category, callback.message, state)


async def search_by_categories_answer(category: str, message: Message, state: Context):
    await state.update_data(category=category)
    await state.set_state(SearchStates.tags)

    tags = await storage.get_tags(message.chat.id, category=category)

    if tags:
        await message.answer(
            text=selecting_tags,
            reply_markup=OptionsMenu.generate_menu(tags)
        )
    else:
        await message.answer(text=tags_not_found)
