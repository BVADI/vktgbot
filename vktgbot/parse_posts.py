import re
from typing import Union
from datetime import date, timedelta, datetime

import requests
from loguru import logger

from tools import prepare_text_for_html, prepare_text_for_reposts, add_urls_to_text, reformat_vk_links, del_hashtag_text
from api_requests import get_video_url, get_user_name, get_audio_url
from config import VK_DOMAIN, VK_TOKEN, REQ_VERSION, SIGN_UP, SIGN, SKIP_REPOSTS, SRC_LINK, SIGN_LINK, DEL_HASHTAG
from config import SHOW_WEB_PAGE_PREVIEW, SHOW_NOTIF, DISABLE_NOTIF_START, DISABLE_NOTIF_STOP
from config import SHOW_CREATOR, SHOW_LINKS, SHOW_PHOTO, SHOW_DOCS, SHOW_PHOTOALBUMS, SHOW_ALBUM_PHOTO, SHOW_DOCS_PHOTO
from config import SHOW_VIDEOS, SHOW_MESSAGE


def parse_post(
     item: dict, item_type: str, group_name: str
) -> dict:
    text = prepare_text_for_html(item["text"])

    if "copy_history" in item and not SKIP_REPOSTS:
        text = prepare_text_for_reposts(text, item, item_type, group_name)
    urls: list = []
    videos: list = []
    photos: list = []
    docs: list = []
    albums: list = []
    diswebpagep = ''

    text = reformat_vk_links(text)
    if "attachments" in item:
        parse_attachments(item["attachments"], text, urls, videos, photos, docs, albums)

    if "copy_history" in item:
        if "attachments" in item["copy_history"][0]:
            parse_attachments(item["copy_history"][0]["attachments"], text, urls, videos, photos, docs, albums)

    text = add_urls_to_text(text, urls, videos, albums)
    if SHOW_CREATOR and "signer_id" in item:
        name = get_user_name(VK_TOKEN, REQ_VERSION, abs(item["signer_id"]))
        text += f'\n\n{name}'
    if SHOW_CREATOR and "copy_history" in item and "signer_id" in item["copy_history"][0]:
        name = get_user_name(VK_TOKEN, REQ_VERSION, abs(item["copy_history"][0]["signer_id"]))
        text += f'\n\n{name}'
    if SHOW_CREATOR and item["from_id"] != item["owner_id"]:
        name = get_user_name(VK_TOKEN, REQ_VERSION, abs(item["from_id"]))
        text = f'{name}\n\n{text}'
    if DEL_HASHTAG:
        text = del_hashtag_text(text)
    if SIGN_UP != "":
        text = f'{SIGN_UP}\n{text}'
    if SIGN != "":
        text += f'\n{SIGN}'
    if SRC_LINK:
        text += f"\n\n<a href='https://vk.com/{VK_DOMAIN}?w=wall{item['owner_id']}_{item['id']}'>{SIGN_LINK}</a>"
    if not SHOW_MESSAGE:
        text = ''
    diswebpagep = get_disable_web_page_preview(text, videos, photos, diswebpagep)
    disnotif = get_show_notif(item)
    logger.info(f"{item_type.capitalize()} parsing is complete.")
    return {"text": text, "photos": photos, "docs": docs, "diswebpagep": diswebpagep, "disnotif": disnotif}


def parse_attachments(attachments, text, urls, videos, photos, docs, albums):
    for attachment in attachments:
        if attachment["type"] == "link" and SHOW_LINKS:
            url = get_url(attachment, text)
            if url:
                urls.append(url)
        elif attachment["type"] == "photo" and SHOW_PHOTO:
            photo = get_photo(attachment)
            if photo:
                photos.append(photo)
        elif attachment["type"] == "doc" and attachment["doc"]["ext"] == "jpg" and SHOW_DOCS_PHOTO:
            jpg = get_jpg(attachment)
            if jpg:
                photos.append(jpg)
        elif attachment["type"] == "doc" and SHOW_DOCS:
            doc = get_doc(attachment["doc"])
            if doc:
                docs.append(doc)
        elif attachment["type"] == "album" and (SHOW_PHOTOALBUMS or SHOW_ALBUM_PHOTO):
            album = get_album(attachment)
            album_photo = get_album_photo(attachment)
            if album and SHOW_PHOTOALBUMS:
                albums.append(album)
            if album_photo and SHOW_ALBUM_PHOTO:
                photos.append(album_photo)
        elif attachment["type"] == "video" and SHOW_VIDEOS:
            video = get_video(attachment)
            if video:
                videos.append(video)


def get_url(attachment: dict, text: str) -> Union[dict, None]:
    url = attachment["link"]["url"]
    if "title" in attachment["link"]:
        title = attachment["link"]["title"]
    else:
        title = ''
    return {"title": title, "url": url} if url not in text else None


def get_video(attachment: dict) -> Union[dict, None]:
    owner_id = attachment["video"]["owner_id"]
    video_id = attachment["video"]["id"]
    access_key = attachment["video"]["access_key"]
    if "title" in attachment["video"]:
        title = attachment["video"]["title"]
    else:
        title = ''
    video = get_video_url(VK_TOKEN, REQ_VERSION, owner_id, video_id, access_key)
    return {"title": title, "url": video} if video else f"https://vk.com/video{owner_id}_{video_id}"


def get_album(attachment: dict) -> Union[dict, None]:
    url = f'https://vk.com/album{attachment["album"]["owner_id"]}_{attachment["album"]["id"]}'
    if "title" in attachment["album"]:
        title = attachment["album"]["title"]
    else:
        title = ''
    return {"title": title, "url": url}


def get_album_photo(attachment: dict) -> Union[str, None]:
    sizes = attachment["album"]["thumb"]["sizes"]
    types = ["w", "z", "y", "x", "r", "q", "p", "o", "m", "s"]
    for type_ in types:
        if next(
            (item for item in sizes if item["type"] == type_),
            False,
        ):
            return re.sub(
                "",
                "",
                next(
                    (item for item in sizes if item["type"] == type_),
                    False,
                )["url"],
            )
    else:
        return None


def get_jpg(attachment: dict) -> Union[str, None]:
    sizes = attachment["doc"]["preview"]["photo"]["sizes"]
    types = ["w", "z", "y", "x", "r", "q", "p", "o", "m", "s"]
    for type_ in types:
        if next(
            (item for item in sizes if item["type"] == type_),
            False,
        ):
            return re.sub(
                "",
                "",
                next(
                    (item for item in sizes if item["type"] == type_),
                    False,
                )["src"],
            )
    else:
        return None


def get_photo(attachment: dict) -> Union[str, None]:
    sizes = attachment["photo"]["sizes"]
    types = ["w", "z", "y", "x", "r", "q", "p", "o", "m", "s"]
    for type_ in types:
        if next(
            (item for item in sizes if item["type"] == type_),
            False,
        ):
            return re.sub(
                "&([a-zA-Z]+(_[a-zA-Z]+)+)=([a-zA-Z0-9-_]+)",
                "",
                next(
                    (item for item in sizes if item["type"] == type_),
                    False,
                )["url"],
            )
    else:
        return None


def get_doc(doc: dict) -> Union[dict, None]:
    if doc["size"] > 50000000:
        logger.info(
            "The document was skipped due to its size exceeding the "
            f"50MB limit: {doc['size']=}."
        )
        return None
    else:
        response = requests.get(doc["url"])

        with open(f'./temp/{doc["title"]}', "wb") as file:
            file.write(response.content)

    return {"title": doc["title"], "url": doc["url"]}


def get_disable_web_page_preview(text, videos, photos, diswebpagep) -> str:
    if SHOW_WEB_PAGE_PREVIEW == "True":
        diswebpagep = "False"
    elif SHOW_WEB_PAGE_PREVIEW == "False":
        diswebpagep = "True"
    elif SHOW_WEB_PAGE_PREVIEW == "FV":
        if (len(photos) == 1 and len(text) > 1024) or len(videos) > 0:
            diswebpagep = "False"
        else:
            diswebpagep = "True"
    logger.warning(f"disablewebpagepreview: {diswebpagep}")
    return diswebpagep


def get_show_notif(item) -> str:
    if SHOW_NOTIF:
        disnotif = "False"
    else:
        disnotif = "True"
    if DISABLE_NOTIF_START and DISABLE_NOTIF_STOP:
        dates = item["date"]
        dates_t = datetime.fromtimestamp(dates)
        today = date.today()
        today_t = datetime(
            year=today.year,
            month=today.month,
            day=today.day,
        )
        tstart = today_t + timedelta(hours=DISABLE_NOTIF_START)
        tstop = today_t + timedelta(hours=DISABLE_NOTIF_STOP)
        if tstart < tstop:
            if tstart < dates_t < tstop:
                disnotif = "True"
        else:
            if dates_t > tstart or dates_t < tstop:
                disnotif = "True"
    return disnotif
