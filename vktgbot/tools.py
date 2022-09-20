import os
import re

from loguru import logger


def blacklist_check(blacklist: list, text: str) -> bool:
    if blacklist:
        text_lower = text.lower()
        for black_word in blacklist:
            if black_word.lower() in text_lower:
                logger.info(
                    "Post was skipped due to the detection of "
                    f"blacklisted word: {black_word}."
                )
                return True

    return False


def whitelist_check(whitelist: list, text: str) -> bool:
    if whitelist:
        text_lower = text.lower()
        for white_word in whitelist:
            if white_word.lower() in text_lower:
                return False
        logger.info("The post was skipped because no whitelist words were found.")
        return True

    return False


def prepare_temp_folder():
    if "temp" in os.listdir():
        for root, dirs, files in os.walk("temp"):
            for file in files:
                os.remove(os.path.join(root, file))
    else:
        os.mkdir("temp")


def prepare_text_for_reposts(
    text: str, item: dict, item_type: str, group_name: str
) -> str:
    if item_type == "post":
        from_id = item["copy_history"][0]["from_id"]
        idd = item["copy_history"][0]["id"]
        link_to_repost = f"https://vk.com/wall{from_id}_{idd}"
        repost = prepare_text_for_html(item["copy_history"][0]["text"])
        if text == '':
            text = f'<a href="{link_to_repost}"><b>↪ {group_name}</b></a>\n\n{repost}'
        else:
            text = f'{text}\n\n<a href="{link_to_repost}"><b>↪ {group_name}</b></a>\n\n{repost}'
    return text


def prepare_text_for_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def add_urls_to_text(text: str, urls: list, videos: list, albums: list) -> str:
    first_link = True
    urls2 = videos + urls + albums

    if not urls2:
        return text

    for video in videos:
        if video["url"] not in text:
            if first_link:
                text = f'<a href="{video["url"]}"> </a>{text}\n\n🎥 <a href="{video["url"]}">{video["title"]}</a>' \
                    if text else video
                first_link = False
            else:
                text += f'\n🎥 <a href="{video["url"]}">{video["title"]}</a>'
        elif video["url"] not in text:
            text = text.replace(f'{video["url"]}', f'🎥 <a href="{video["url"]}"> {video["title"]}</a>', 1)
        logger.info(f"Add video urls")

    for url in urls:
        if url["url"] not in text:
            text += f'\n\n🔗 <a href="{url["url"]}">{url["title"]}</a>'
        elif url["url"] in text:
            text = text.replace(f'{url["url"]}', f'🔗 <a href="{url["url"]}"> {url["title"]}</a>', 1)
        logger.info(f"Add urls")
    for album in albums:
        if album["url"] not in text:
            text += f'\n\n📷 <a href="{album["url"]}">{album["title"]}</a>'
        elif album["url"] in text:
            text = text.replace(f'{album["url"]}',  f'📷 <a href="{album["url"]}"> {album["title"]}</a>', 1)
        logger.info(f"Add album urls")
    return text


def split_text(text: str, fragment_size: int) -> list:
    fragments = []
    for fragment in range(0, len(text), fragment_size):
        fragments.append(text[fragment : fragment + fragment_size])
    return fragments


def reformat_vk_links(text: str) -> str:
    if re.search("\[(.+?)\|(.+?)\]", text):
        match = re.search("\[(.+?)\|(.+?)\]", text)
        while match:
            left_text = text[: match.span()[0]]
            right_text = text[match.span()[1] :]
            matching_text = text[match.span()[0] : match.span()[1]]

            link_domain, link_text = re.findall("\[(.+?)\|(.+?)\]", matching_text)[0]
            if link_domain[0:5] == 'https':
                text = left_text + f"""<a href="{f'{link_domain}'}">{link_text}</a>""" + right_text
            else:
                text = left_text + f"""<a href="{f'https://vk.com/{link_domain}'}">{link_text}</a>""" + right_text
            match = re.search("\[(.+?)\|(.+?)\]", text)
            logger.info(f"Reformat vk links")
    return text


def del_hashtag_text(text: str) -> str:
    text = re.sub("\s#(\S+)","", text)
    logger.info(f"Del hashtag")
    return text