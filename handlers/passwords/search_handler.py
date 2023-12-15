from aiogram import Router
from aiogram.types import Message, CallbackQuery
from db.opensearch.passwords import passwords
from aiogram.fsm.context import FSMContext as Context
from views.menus import OptionsMenu
from views.phrases import (
    password_not_found,
    logins_not_found,
    search_password as searching_password,
)
from views.menus import MainMenu
from asyncio import sleep
from aiogram.fsm.state import StatesGroup, State
from bot import bot


class SearchPasswordStates(StatesGroup):
    login = State()


router = Router()


@router.message(MainMenu.is_search_password)
async def search_password(message: Message, state: Context):
    await state.set_state(state=SearchPasswordStates.login)
    logins = await passwords.get_logins(message.chat.id)

    if logins:
        await message.answer(
            text=searching_password,
            reply_markup=OptionsMenu.generate_menu(logins)
        )
    else:
        await message.answer(text=logins_not_found)
        await state.clear()


@router.callback_query(SearchPasswordStates.login)
async def get_password(callback: CallbackQuery, state: Context):
    login = callback.data
    await get_password_answer(login, callback.message, state)


@router.message(SearchPasswordStates.login)
async def get_password(message: Message, state: Context):
    login = message.text
    await get_password_answer(login, message, state)


async def get_password_answer(login: str, message: Message, state: Context):
    password = await passwords.search_by_login(message.chat.id, login)
    if password:
        sent_message = await message.answer(text=password)
        await sleep(5)
        await bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)

    else:
        await message.answer(text=password_not_found)
    await state.clear()
