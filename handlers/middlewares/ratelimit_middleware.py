from typing import Callable, Dict, Any, Awaitable

from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from views.phrases import ratelimit_check_failed
from db.redis.ratelimits import ratelimits


class RateLimitMiddleware(BaseMiddleware):

    async def __call__(self,  handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], message_or_callback: [Message, CallbackQuery], data: dict):
        if isinstance(message_or_callback, Message):
            await self.on_pre_process_message(message_or_callback, data, handler)
        elif isinstance(message_or_callback, CallbackQuery):
            await self.on_pre_process_callback_query(message_or_callback, data, handler)

    async def on_pre_process_message(self, message: Message, data: dict, handler):
        if not await ratelimits.check_user(message.chat.id):
            await message.answer(text=ratelimit_check_failed)
            raise CancelHandler()

        return await handler(message, data)

    async def on_pre_process_callback_query(self, callback: CallbackQuery, data: dict, handler):
        message = callback.message
        return await self.on_pre_process_message(message, data, handler)
