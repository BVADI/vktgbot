import asyncio

from aiogram import Bot, types
from aiogram.utils import exceptions
from loguru import logger

from tools import split_text


async def send_post(
        bot: Bot, tg_channel: str, text: str, photos: list, docs: list, diswebpagep, disnotif, num_tries: int = 0
) -> None:
    num_tries += 1
    if num_tries > 3:
        logger.error("Post was not sent to Telegram. Too many tries.")
        return
    try:
        if len(photos) == 0:
            await send_text_post(bot, tg_channel, text, diswebpagep, disnotif)
        elif len(photos) == 1:
            await send_photo_post(bot, tg_channel, text, photos, diswebpagep, disnotif)
        elif len(photos) >= 2:
            await send_photos_post(bot, tg_channel, text, photos, diswebpagep, disnotif)
        if docs:
            await send_docs_post(bot, tg_channel, docs, disnotif)
    except exceptions.RetryAfter as ex:
        logger.warning(f"Flood limit is exceeded. Sleep {ex.timeout} seconds. Try: {num_tries}")
        await asyncio.sleep(ex.timeout)
        await send_post(bot, tg_channel, text, photos, docs, diswebpagep, disnotif, num_tries)
    except exceptions.BadRequest as ex:
        logger.warning(f"Bad request. Wait 60 seconds. Try: {num_tries}. {ex}")
        logger.warning(f"{text}")
        await asyncio.sleep(60)
        await send_post(bot, tg_channel, text, photos, docs, diswebpagep, disnotif, num_tries)


async def send_text_post(bot: Bot, tg_channel: str, text: str, diswebpagep: bool, disnotif: bool) -> None:
    if not text:
        return

    if len(text) < 4096:
        await bot.send_message(
            tg_channel, text, parse_mode=types.ParseMode.HTML, disable_web_page_preview=diswebpagep,
            disable_notification=disnotif
        )
    else:
        text_parts = split_text(text, 4084)
        prepared_text_parts = (
            [text_parts[0] + " (...)"]
            + ["(...) " + part + " (...)" for part in text_parts[1:-1]]
            + ["(...) " + text_parts[-1]]
        )

        for part in prepared_text_parts:
            if part == prepared_text_parts[-1]:
                await bot.send_message(
                    tg_channel, part, parse_mode=types.ParseMode.HTML, disable_web_page_preview=diswebpagep,
                    disable_notification=disnotif
                )
            else:
                await bot.send_message(
                    tg_channel, part, parse_mode=types.ParseMode.HTML, disable_web_page_preview=True,
                    disable_notification=disnotif
                )
            await asyncio.sleep(0.5)
    logger.info("Text post sent to Telegram.")


async def send_photo_post(
        bot: Bot, tg_channel: str, text: str, photos: list, diswebpagep: bool, disnotif: bool) -> None:
    if len(text) <= 1024:
        await bot.send_photo(
            tg_channel, photos[0], text, parse_mode=types.ParseMode.HTML, disable_notification=disnotif
        )
        logger.info("Text post (<=1024) with photo sent to Telegram.")
    else:
        prepared_text = f'<a href="{photos[0]}"> </a>{text}'
        if len(prepared_text) <= 4096:
            await bot.send_message(
                tg_channel, prepared_text, parse_mode=types.ParseMode.HTML, disable_web_page_preview=diswebpagep,
                disable_notification=disnotif
            )
        else:
            await bot.send_photo(tg_channel, photos[0], disable_notification=disnotif)
            await send_text_post(bot, tg_channel, text, diswebpagep, disnotif)
        logger.info("Text post (>1024) with photo sent to Telegram.")


async def send_photos_post(
        bot: Bot, tg_channel: str, text: str, photos: list, diswebpagep: bool, disnotif: bool) -> None:
    media = types.MediaGroup()
    for photo in photos:
        media.attach_photo(types.InputMediaPhoto(photo))

    if (len(text) > 0) and (len(text) <= 1024):
        media.media[0].caption = text
        media.media[0].parse_mode = types.ParseMode.HTML
        await bot.send_media_group(tg_channel, media, disable_notification=disnotif)
    elif len(text) > 1024:
        await bot.send_media_group(tg_channel, media, disable_notification=disnotif)
        await send_text_post(bot, tg_channel, text, diswebpagep, disnotif)
        #    await bot.send_media_group(tg_channel, media)
    logger.info("Text post with photos sent to Telegram.")


async def send_docs_post(bot: Bot, tg_channel: str, docs: list, disnotif: bool) -> None:
    media = types.MediaGroup()
    for doc in docs:
        media.attach_document(
            types.InputMediaDocument(open(f"./temp/{doc['title']}", "rb"))
        )
    await bot.send_media_group(tg_channel, media, disable_notification=disnotif)
    logger.info("Documents sent to Telegram.")
