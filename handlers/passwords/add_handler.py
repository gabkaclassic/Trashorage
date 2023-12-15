from aiogram import Router
from aiogram.types import Message
from db.opensearch.passwords import passwords
from aiogram.fsm.context import FSMContext as Context
from views.phrases import (
    enter_login,
    enter_password,
    success_saving_password,
    failure_saving_password,
)
from views.menus import MainMenu
from aiogram.fsm.state import StatesGroup, State


class AddPasswordStates(StatesGroup):
    login = State()
    password = State()


router = Router()


@router.message(MainMenu.is_add_password)
async def add_password(message: Message, state: Context):
    await state.set_state(state=AddPasswordStates.login)
    await message.answer(text=enter_login)


@router.message(AddPasswordStates.login)
async def add_password_login(message: Message, state: Context):
    login = message.text
    await state.update_data(login=login)
    await state.set_state(AddPasswordStates.password)
    await message.answer(text=enter_password % {'login': login})


@router.message(AddPasswordStates.password)
async def add_password_value(message: Message, state: Context):
    try:
        await passwords.add_credentials(
            message.chat.id,
            (await state.get_data()).get('login'),
            message.text
        )
        await message.answer(text=success_saving_password)
        await message.delete()
    except Exception as e:
        print(e)
        await message.answer(text=failure_saving_password)
    finally:
        await state.clear()
