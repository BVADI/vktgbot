import os
import json

import dotenv

dotenv.load_dotenv()


TG_CHANNEL: str = os.getenv("VAR_TG_CHANNEL", "")
TG_BOT_TOKEN: str = os.getenv("VAR_TG_BOT_TOKEN", "")
VK_TOKEN: str = os.getenv("VAR_VK_TOKEN", "")
VK_DOMAIN: str = os.getenv("VAR_VK_DOMAIN", "")

REQ_VERSION: float = float(os.getenv("VAR_REQ_VERSION", 5.103))
REQ_COUNT: int = int(os.getenv("VAR_REQ_COUNT", 10))
REQ_FILTER: str = os.getenv("VAR_REQ_FILTER", "owner")

SINGLE_START: bool = os.getenv("VAR_SINGLE_START", "False").lower() in ("true",)
TIME_TO_SLEEP: int = int(os.getenv("VAR_TIME_TO_SLEEP", 120))
SKIP_ADS_POSTS: bool = os.getenv("VAR_SKIP_ADS_POSTS", "True").lower() in ("true",)
SKIP_COPYRIGHTED_POST: bool = os.getenv("VAR_SKIP_COPYRIGHTED_POST", "False").lower() in ("true",)
SKIP_REPOSTS: bool = os.getenv("VAR_SKIP_REPOSTS", "False").lower() in ("true",)
SHOW_WEB_PAGE_PREVIEW: str = os.getenv("VAR_SHOW_WEB_PAGE_PREVIEW", "FV")
SIGN_UP: str = os.getenv("VAR_SIGN_UP", "")
SIGN: str = os.getenv("VAR_SIGN", "")
SRC_LINK: bool = os.getenv("VAR_SRC_LINK", "False").lower() in ("true",)
SIGN_LINK: str = os.getenv("VAR_SIGN_LINK", "➰ ВК")
DEL_HASHTAG: bool = os.getenv("VAR_DEL_HASHTAG", "False").lower() in ("true",)
SHOW_NOTIF: bool = os.getenv("VAR_SHOW_NOTIF", "True").lower() in ("true",)
DISABLE_NOTIF_START: int = int(os.getenv("VAR_DISABLE_NOTIF_START", 0))
DISABLE_NOTIF_STOP: int = int(os.getenv("VAR_DISABLE_NOTIF_STOP", 0))
SHOW_LINKS: bool = os.getenv("VAR_SHOW_LINKS", "True").lower() in ("true",)
SHOW_VIDEOS: bool = os.getenv("VAR_SHOW_VIDEOS", "True").lower() in ("true",)
SHOW_DOCS: bool = os.getenv("VAR_SHOW_DOCS", "True").lower() in ("true",)
SHOW_PHOTOALBUMS: bool = os.getenv("VAR_SHOW_PHOTOALBUMS", "True").lower() in ("true",)
SHOW_CREATOR: bool = os.getenv("VAR_SHOW_CREATOR", "True").lower() in ("true",)
SHOW_PHOTO: bool = os.getenv("VAR_SHOW_PHOTO", "True").lower() in ("true",)
SHOW_DOCS_PHOTO: bool = os.getenv("VAR_SHOW_DOCS_PHOTO", "True").lower() in ("true",)
SHOW_ALBUM_PHOTO: bool = os.getenv("VAR_SHOW_ALBUM_PHOTO", "True").lower() in ("true",)
SHOW_MESSAGE: bool = os.getenv("VAR_SHOW_MESSAGE", "True").lower() in ("true",)

WHITELIST: list = json.loads(os.getenv("VAR_WHITELIST", "[]"))
BLACKLIST: list = json.loads(os.getenv("VAR_BLACKLIST", "[]"))
BLACKLIST_ID_REPOST: list = json.loads(os.getenv("VAR_BLACKLIST_ID_REPOST", "[]"))
