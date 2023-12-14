from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from views.phrases import (
    start_phrase,
)
from views.menus import MainMenu
from aiogram.fsm.state import StatesGroup, State

router = Router()


class MainStates(StatesGroup):
    tags = State()
    categories = State()


class AddingStates(StatesGroup):
    category = State()
    tags = State()
    object = State()


@router.message(Command("start"))
async def start_dialog(message: Message):
    await message.answer(start_phrase, reply_markup=MainMenu.menu)
