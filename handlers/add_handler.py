from typing import List

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from views.phrases import (
    selecting_category,
    selecting_tags,
    add_object,
    tags_required,
    category_required
)
from views.menus import MainMenu, OptionsMenu
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext as Context
from db.opensearch_client import storage

router = Router()


class AddingStates(StatesGroup):
    category = State()
    tags = State()
    object = State()


@router.message(MainMenu.is_adding)
async def adding_category(message: Message, state: Context):
    await state.set_state(state=AddingStates.category)
    categories = await storage.get_categories(message.chat.id)

    if categories:
        await message.answer(
            text=selecting_category,
            reply_markup=OptionsMenu.generate_menu(categories)
        )
    else:
        await message.answer(text=category_required)


@router.callback_query(AddingStates.category)
async def adding_tags(callback: CallbackQuery, state: Context):
    category = callback.data
    await adding_test_answer(category, callback.message, state)
        
@router.message(AddingStates.category)
async def adding_tags(message: Message, state: Context):
    category = message.text
    await adding_test_answer(category, message, state)


async def adding_test_answer(category: str, message: Message, state: Context):
    await state.set_state(state=AddingStates.tags)
    await state.update_data(category=category)
    tags = await storage.get_tags(chat_id=message.chat.id, category=category)
    if tags:
        await message.answer(
            text=selecting_tags,
            reply_markup=OptionsMenu.generate_menu(tags)
        )
    else:
        await message.answer(text=tags_required)


@router.callback_query(AddingStates.tags)
async def adding_object(callback: CallbackQuery, state: Context):
    tags = callback.data.split()
    await adding_object_answer(callback.message, state, tags)

@router.message(AddingStates.tags)
async def adding_object(message: Message, state: Context):
    tags = message.text.split()
    await adding_object_answer(message, state, tags)


async def adding_object_answer(message: Message, state: Context, tags: List[str]):
    await state.set_state(state=AddingStates.object)
    await state.update_data(tags=tags)
    await message.answer(text=add_object)


@router.message(AddingStates.object)
async def adding_object(message: Message, state: Context):
    note = message.message_id
    await state.update_data(object=note)

    try:
        data = await state.get_data()
        created = await storage.add_object(
            chat_id=message.chat.id,
            category=data['category'],
            tags=data['tags'],
            object=data['object'],
        )
        if not created:
            raise Exception("Document creation error")
        await state.clear()
        await message.answer("Om-nom-nom... Tasty!")

    except Exception as e:
        await message.answer(text='Hmmm... Repeat your try')
