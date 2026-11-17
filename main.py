#!/usr/bin/env python3
"""NEXT GEN GIVEAWAYS — single-file Telegram giveaway bot (aiogram 3 + SQLite).
Hosted by TG MANDI (@tgmandi).

The whole bot in one file: config, premium emoji library, quote engine,
database, card copy, keyboards and every handler.

    pip install aiogram aiosqlite httpx python-dotenv
    BOT_TOKEN=123:abc python NextGenGiveaways.py

Environment (a .env file next to this script is read automatically):
    BOT_TOKEN                 required — token from @BotFather
    BRAND_NAME                NEXT GEN GIVEAWAYS
    HOST_NAME                 TG MANDI
    MAIN_CHANNEL_TITLE        TG Mandi Official
    MAIN_CHANNEL_USERNAME     @tgmandi
    MAIN_CHANNEL_ID           -1004388652593
    GIVEAWAY_CHANNEL_USERNAME @tgmandGiveaway
    GIVEAWAY_CHANNEL_ID       optional numeric ID for giveaway posting channel
    GROUP_USERNAME            @tgmandichats
    GROUP_ID                  -1004381705935
    OWNER_IDS                 8027403165
    CLAIM_HANDLE              @tgmandi (can also be changed live with /setclaim)
    PREMIUM_EMOJI             1 (enabled by default; set 0 to disable)
    DB_PATH                   optional, defaults to ./nextgen_giveaways.db
    LINES_API_*               optional OpenAI-compatible quote refill (LINES_API_KEY)
"""

import types


# ══════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════
"""NEXT GEN GIVEAWAYS — configuration."""
import os
import re
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:   # python-dotenv is optional
    def load_dotenv(*_a, **_k):
        return False

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _ids(value: str) -> set[int]:
    return {int(x) for x in re.findall(r"\d{5,}", value or "")}


def _int_or_zero(value: str) -> int:
    v = (value or "").strip()
    return int(v) if v and v.lstrip("-").isdigit() else 0


# ── identity & host ─────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "9234967804:AAFU1ESS6t3VjHeyPqpuAruZIrO4WHdzg4A").strip()
BRAND = os.getenv("BRAND_NAME", "TG MANDI GIVEAWAYS").strip()
HOST_NAME = os.getenv("HOST_NAME", "TG MANDI").strip()
BRAND_TAG = os.getenv("BRAND_TAG", f"Hosted by {HOST_NAME}").strip()
PREMIUM_EMOJI = os.getenv("PREMIUM_EMOJI", "1").strip().lower() not in {"0", "false", "off", "no"}

# ── force-join gate #1: main host channel (TG Mandi Official) ───────────────
MAIN_CHANNEL_TITLE = os.getenv("MAIN_CHANNEL_TITLE", "TG Mandi Official").strip()
MAIN_CHANNEL_USERNAME = os.getenv("MAIN_CHANNEL_USERNAME", "@tgmandi").strip()
MAIN_CHANNEL_ID = _int_or_zero(os.getenv("MAIN_CHANNEL_ID", "-1004388652593"))
MAIN_CHANNEL_URL = os.getenv(
    "MAIN_CHANNEL_URL",
    "https://t.me/" + MAIN_CHANNEL_USERNAME.lstrip("@"),
).strip()

# ── force-join gate #2 + posting channel: giveaway channel ──────────────────
GIVEAWAY_CHANNEL_USERNAME = os.getenv(
    "GIVEAWAY_CHANNEL_USERNAME",
    os.getenv("CHANNEL_USERNAME", "@tgmandGiveaway"),
).strip()
GIVEAWAY_CHANNEL_TITLE = os.getenv("GIVEAWAY_CHANNEL_TITLE", GIVEAWAY_CHANNEL_USERNAME).strip()
GIVEAWAY_CHANNEL_ID = _int_or_zero(os.getenv("GIVEAWAY_CHANNEL_ID", ""))
GIVEAWAY_CHANNEL_URL = os.getenv(
    "GIVEAWAY_CHANNEL_URL",
    "https://t.me/" + GIVEAWAY_CHANNEL_USERNAME.lstrip("@"),
).strip()
# Target passed to Bot API when posting/editing giveaways, cards and results
GIVEAWAY_CHANNEL_TARGET: int | str = GIVEAWAY_CHANNEL_ID or GIVEAWAY_CHANNEL_USERNAME

# ── force-join gate #3: community group ─────────────────────────────────────
GROUP_USERNAME = os.getenv("GROUP_USERNAME", "@tgmandichats").strip()
GROUP_TITLE = os.getenv("GROUP_TITLE", "tg mandi chats").strip()
GROUP_ID = _int_or_zero(os.getenv("GROUP_ID", "-1004381705935"))
GROUP_URL = os.getenv(
    "GROUP_URL",
    "https://t.me/" + GROUP_USERNAME.lstrip("@"),
).strip()

# Aliases pointing to the giveaway posting channel
CHANNEL_USERNAME = GIVEAWAY_CHANNEL_USERNAME
CHANNEL_URL = GIVEAWAY_CHANNEL_URL

# Optional extra promo button on voting cards (not a join gate; empty by default)
EXTRA_BTN_LABEL = os.getenv("EXTRA_BTN_LABEL", HOST_NAME).strip()
CHEAP_API_URL = os.getenv("EXTRA_BTN_URL", os.getenv("CHEAP_API_URL", "")).strip()

# ── prize claim ────────────────────────────────────────────────────────────
# Winners are told to contact this handle to collect their prize (also editable via /setclaim).
CLAIM_HANDLE = os.getenv("CLAIM_HANDLE", MAIN_CHANNEL_USERNAME).strip()
CLAIM_URL = os.getenv("CLAIM_URL", "https://t.me/" + CLAIM_HANDLE.lstrip("@")).strip()

# ── owners / admins ─────────────────────────────────────────────────────────
# Owners can add & remove other admins. Extra admins live in the database.
OWNER_IDS = _ids(os.getenv("OWNER_IDS", "8027403165"))

# ── storage ─────────────────────────────────────────────────────────────────
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "nextgen_giveaways.db"))

# ── optional AI quote refill engine ─────────────────────────────────────────
# Any OpenAI-compatible endpoint works: OpenRouter, Groq, DeepInfra, Together,
# Ollama, a local llama.cpp server, ... Leave the key empty to use the built-in
# quote pool (zero cost, zero downtime, no network calls).
LINES_API_BASE = os.getenv("LINES_API_BASE", "https://openrouter.ai/api/v1").strip()
LINES_API_KEY = os.getenv("LINES_API_KEY", "").strip()
LINES_API_MODEL = os.getenv("LINES_API_MODEL", "meta-llama/llama-3.3-70b-instruct:free").strip()
LINES_API_TIMEOUT = float(os.getenv("LINES_API_TIMEOUT", "6"))

config = types.SimpleNamespace(
    BASE_DIR=BASE_DIR,
    _ids=_ids,
    BOT_TOKEN=BOT_TOKEN,
    BRAND=BRAND,
    HOST_NAME=HOST_NAME,
    BRAND_TAG=BRAND_TAG,
    PREMIUM_EMOJI=PREMIUM_EMOJI,
    MAIN_CHANNEL_TITLE=MAIN_CHANNEL_TITLE,
    MAIN_CHANNEL_USERNAME=MAIN_CHANNEL_USERNAME,
    MAIN_CHANNEL_ID=MAIN_CHANNEL_ID,
    MAIN_CHANNEL_URL=MAIN_CHANNEL_URL,
    GIVEAWAY_CHANNEL_TITLE=GIVEAWAY_CHANNEL_TITLE,
    GIVEAWAY_CHANNEL_USERNAME=GIVEAWAY_CHANNEL_USERNAME,
    GIVEAWAY_CHANNEL_ID=GIVEAWAY_CHANNEL_ID,
    GIVEAWAY_CHANNEL_URL=GIVEAWAY_CHANNEL_URL,
    GIVEAWAY_CHANNEL_TARGET=GIVEAWAY_CHANNEL_TARGET,
    GROUP_TITLE=GROUP_TITLE,
    GROUP_USERNAME=GROUP_USERNAME,
    GROUP_ID=GROUP_ID,
    GROUP_URL=GROUP_URL,
    CHANNEL_USERNAME=CHANNEL_USERNAME,
    CHANNEL_URL=CHANNEL_URL,
    EXTRA_BTN_LABEL=EXTRA_BTN_LABEL,
    CHEAP_API_URL=CHEAP_API_URL,
    CLAIM_HANDLE=CLAIM_HANDLE,
    CLAIM_URL=CLAIM_URL,
    OWNER_IDS=OWNER_IDS,
    DB_PATH=DB_PATH,
    LINES_API_BASE=LINES_API_BASE,
    LINES_API_KEY=LINES_API_KEY,
    LINES_API_MODEL=LINES_API_MODEL,
    LINES_API_TIMEOUT=LINES_API_TIMEOUT,
)


# ══════════════════════════════════════════════════════════════════
#  PREMIUM
# ══════════════════════════════════════════════════════════════════
"""Premium (custom) emoji registry — text emoji + button icons.

Every id in this file was **rendered and eyeballed** before being shipped: the
old map trusted an emoji index whose name→id pairs were wrong for several packs
("green check mark" pointing at meme faces, logos, hands…), which is why cards
looked messy. Everything below is curated by hand from clean 3D packs.

Two maps:
  EMOJI : name -> (fallback emoji, custom_emoji_id)   used inside message text
  ICONS : name -> custom_emoji_id                     used on inline buttons
                                                        (icon_custom_emoji_id)

An empty id ("") means *plain fallback emoji only* — used where no good premium
sticker exists. That keeps the text clean instead of attaching a random sticker.

Use `{e:name}` inside any text and run it through `render()`:

    render("{e:crown} <b>Welcome</b>")
    ->  <tg-emoji emoji-id="6311999820714220870">👑</tg-emoji> <b>Welcome</b>

Run `python check_emoji.py <index>` to re-verify ids, and
`python preview_emoji.py` to render a contact sheet of the whole set.
"""
import re

# ── message text ────────────────────────────────────────────────────────────
EMOJI: dict[str, tuple[str, str]] = {
    # ── identity / luxe ───────────────────────────────────────────────────
    "crown":        ("👑", "6311999820714220870"),
    "owner_tag":    ("👑", "6311999820714220870"),
    "gem":          ("💎", "6310032545304026289"),
    "gem2":         ("💎", "6310032545304026289"),
    "diamond":      ("💎", "6310032545304026289"),
    "star_gold":    ("⭐", "6309890192907968770"),
    "star":         ("⭐", "6309890192907968770"),
    "star_soft":    ("⭐", "6309890192907968770"),
    "sparkle":      ("✨", "6140943183258849599"),
    "money":        ("💵", "6310069275864341980"),
    "cash":         ("💵", "6310069275864341980"),
    "dollar":       ("💵", "6310069275864341980"),
    "money_wings":  ("💸", ""),
    "credit_card":  ("💳", ""),
    "coin":         ("🪙", ""),
    "vip":          ("💠", ""),
    # ── hype ──────────────────────────────────────────────────────────────
    "gift":         ("🎁", "6312196994072847118"),
    "gift_blue":    ("🎁", "6309788668471025598"),
    "gift_green":   ("🎁", "6309602258300443734"),
    "party":        ("🎉", "6309961712703379735"),
    "confetti":     ("🎊", "6309961712703379735"),
    "fire":         ("🔥", "6309811869884358547"),
    "rocket":       ("🚀", "6309870788245724520"),
    "trophy":       ("🏆", "6311834808070708173"),
    "medal":        ("🏅", ""),
    "target":       ("🎯", "5310278924616356636"),
    "bolt":         ("⚡", "6309883501348919953"),
    "bolt2":        ("⚡", "6309883501348919953"),
    "clover":       ("🍀", "5395325195542078574"),
    "ticket":       ("🎟️", ""),
    "crystal":      ("🔮", ""),
    "firecracker":  ("🧨", ""),
    "heart_fire":   ("❤️‍🔥", "6309579091246850317"),
    # ── status / info ─────────────────────────────────────────────────────
    "check":        ("✅", "6310103949135322908"),
    "check2":       ("✅", "6310103949135322908"),
    "check_plain":  ("✔️", "6310103949135322908"),
    "verified":     ("✅", "6310103949135322908"),
    "verified2":    ("✅", "6336860667676462748"),
    "cross":        ("❌", "6312156428106737991"),
    "cross2":       ("❌", "6312156428106737991"),
    "warning":      ("⚠️", "6100590432209604692"),
    "lock":         ("🔒", "5472308992514464048"),
    "shield":       ("🛡️", "5197288647275071607"),
    "admin_tag":    ("🛡️", "5197288647275071607"),
    "skull":        ("💀", ""),
    "info":         ("📌", "6309960153630251694"),
    "pin":          ("📌", "6309960153630251694"),
    "pushpin":      ("📌", "6309960153630251694"),
    "bookmark":     ("🔖", ""),
    "flag":         ("🚩", "5460755126761312667"),
    "back":         ("🚩", "5460755126761312667"),
    "link":         ("🔗", "6309893061946121745"),
    "share":        ("📣", "6053308421443161790"),
    "channel":      ("📣", "6053308421443161790"),
    "megaphone":    ("📣", "6053308421443161790"),
    "bell":         ("🔔", "6311933167116753547"),
    "hourglass":    ("⏳", "5382194935057372936"),
    "timer":        ("⏱️", "5382194935057372936"),
    "clock":        ("🕓", ""),
    "calendar":     ("📅", "5431897022456145283"),
    "ballot":       ("🗳️", "5359741159566484212"),
    "vote":         ("🗳️", "5359741159566484212"),
    "users":        ("👥", "5316887736823591263"),
    "group":        ("💬", "5440493695851866311"),
    "user":         ("👤", "5258362837411045098"),
    "chart":        ("📊", "6309843875980648126"),
    "stats":        ("📊", "6309843875980648126"),
    "phone":        ("📱", ""),
    "globe":        ("🌐", ""),
    "signal":       ("📶", ""),
    "call":         ("📞", ""),
    "shop":         ("🛍️", ""),
    "photo":        ("🖼️", ""),
    "refresh":      ("🔄", ""),
    "plus":         ("➕", ""),
    "minus":        ("➖", ""),
    "handshake":    ("🤝", "5395732581780040886"),
    # ── people ────────────────────────────────────────────────────────────
    "heart":        ("❤️", "6309591606781549616"),
    "heart_eyes":   ("😍", "5354903467318061957"),
    "broken_heart": ("💔", ""),
    "starstruck":   ("🤩", "5330356071364046086"),
    "clap":         ("👏", ""),
    "thumbsup":     ("👍", ""),
    "wave":         ("👋", ""),
    "wink":         ("😉", ""),
    "smirk":        ("😏", ""),
    "thinking":     ("🤔", ""),
    "pleading":     ("🥺", ""),
    "sleep":        ("💤", ""),
    "eyes":         ("👀", ""),
}

# Extra stickers imported from the packs you named (Social networks RI №2,
# TG iOS & macOS Icons, TON, News, Summer, Love, Eyes, Game, Outline + @MY_YEMENY).
# ── extra stickers: Social networks RI №2, TG iOS & macOS Icons, TON, News,
#    Summer, Love, Eyes, Game, Outline + @MY_YEMENY (ids verified live)
EXTRA: dict[str, tuple[str, str]] = {
    "sparkles": ("✨", "5436064815770538547"),
    "airplane": ("✈️", "5434107826807022558"),
    "raised_fist": ("▫️", "5438351039747106655"),
    "gem_stone": ("💎", "5321179414174672491"),
    "purse": ("👛", "5321182386292039558"),
    "wrapped_gift": ("🎁", "5436325808048220069"),
    "open_lock": ("🔒", "5321134317018067989"),
    "globe_with_meridians": ("🌐", "5321241807164580935"),
    "white_medium_star": ("⭐", "5436083249770174610"),
    "red_apple": ("🍎", "5436399896234072301"),
    "bar_of_soap": ("▫️", "5438420888800239271"),
    "video_camera": ("📷", "5440360070829348445"),
    "camera": ("📷", "5438312655624380182"),
    "speech_balloon": ("💬", "5440493695851866311"),
    "rooster": ("▫️", "5440443625123126288"),
    "hamburger": ("🍔", "5440506164141918668"),
    "frog_face": ("🐸", "5438124484517206642"),
    "frame_with_picture": ("🖼️", "5433795930576953949"),
    "door": ("▫️", "5436293917916043911"),
    "money_mouth_face": ("💰", "5436036245648089027"),
    "money_bag": ("💰", "5436083451633639852"),
    "robot": ("🤖", "5435924494894013190"),
    "ringed_planet": ("▫️", "5436081325624827240"),
    "video_game": ("🎥", "5436028411627738779"),
    "i_love_you_hand_sign": ("▫️", "5436394703618611878"),
    "hatching_chick": ("▫️", "5436304698283958459"),
    "department_store": ("▫️", "5434048040862257754"),
    "whale": ("▫️", "5436179482807410466"),
    "circled_latin_capital_letter_m": ("▫️", "5436215380144070791"),
    "egg": ("▫️", "5435846760280924485"),
    "bank": ("▫️", "5433833670454582701"),
    "telephone_receiver": ("📱", "5436254296842739062"),
    "shopping_bags": ("🛍️", "5433814914332406095"),
    "oncoming_taxi": ("▫️", "5433614399489219928"),
    "musical_note": ("🎵", "5433826235866192560"),
    "red_heart": ("❤️", "5436054344640273901"),
    "mobile_phone": ("📱", "5435927913687980210"),
    "pile_of_poo": ("▫️", "5435887717089055135"),
    "green_apple": ("🍎", "5435913130410546524"),
    "input_symbol_for_numbers": ("▫️", "5226513232549664618"),
    "bust_in_silhouette": ("▫️", "5258362837411045098"),
    "open_file_folder": ("📁", "5258514780469075716"),
    "red_cross_mark": ("❌", "5258226313285607065"),
    "soccer_ball": ("⚽", "5258169263235013408"),
    "bear_face": ("🐻", "5258145898612924124"),
    "memo": ("📝", "5257965174979042426"),
    "gold_coin": ("🪙", "5258368777350816286"),
    "high_voltage_sign": ("⚡", "5258152182150077732"),
    "open_book": ("📖", "5258328383183396223"),
    "briefcase": ("💼", "5258260149037965799"),
    "man_artist_palette": ("▫️", "5258450450448915742"),
    "spiral_calendar_pad": ("📅", "5258105663359294787"),
    "call_me_hand": ("▫️", "5258337316715373336"),
    "camera_with_flash": ("📷", "5258205968025525531"),
    "woman_artist_palette": ("▫️", "5258215635996908355"),
    "cheering_megaphone": ("📱", "5260268501515377807"),
    "green_check_mark": ("✅", "5260726538302660868"),
    "chains": ("▫️", "5260730055880876557"),
    "page_facing_up": ("▫️", "5258477770735885832"),
    "copyright_sign": ("▫️", "5258507474729704350"),
    "busts_in_silhouette": ("▫️", "5258513401784573443"),
    "wastebasket": ("🗑️", "5258130763148172425"),
    "writing_hand": ("▫️", "5258331647358540449"),
    "left_right_arrow": ("▫️", "5260233433107407649"),
    "performing_arts": ("▫️", "5258430848218176413"),
    "file_folder": ("📁", "5257965810634202885"),
    "black_rightwards_arrow": ("▫️", "5260450573768990626"),
    "graduation_cap": ("▫️", "5258334872878980409"),
    "house_buildings": ("🏠", "5257963315258204021"),
    "electric_light_bulb": ("▫️", "5258216851472654189"),
    "round_pushpin": ("📌", "5258509201306557640"),
    "waning_crescent_moon_symbol": ("🌙", "5258011861273551368"),
    "bell_with_cancellation_stroke": ("🔔", "5260264520080695245"),
    "multiple_musical_notes": ("🎵", "5258334469152054985"),
    "north_east_arrow": ("▫️", "5257991477358763590"),
    "heavy_plus_sign": ("▫️", "5258108352008823107"),
    "peach": ("▫️", "5258330865674494479"),
    "pistol": ("▫️", "5260221883940347555"),
    "clapping_hands": ("👏", "5258501105293205250"),
    "anticlockwise_downwards_and_upwards_open_circle_arrows": ("🔒", "5258420634785947640"),
    "shooting_star": ("⭐", "5258212268742549391"),
    "clockwise_downwards_and_upwards_open_circle_arrows": ("🔒", "5260687681733533075"),
    "leftwards_black_arrow": ("▫️", "5258236805890710909"),
    "heavy_exclamation_mark_symbol": ("▫️", "5258474669769497337"),
    "raised_back_of_hand": ("▫️", "5260249440450520061"),
    "ballot_box_with_ballot": ("▫️", "5258200019495821936"),
    "downwards_black_arrow": ("▫️", "5258336354642697821"),
    "clock_face_five_oclock": ("🔒", "5258419835922030550"),
    "timer_clock": ("🔒", "5258258882022612173"),
    "cloud": ("☁️", "5280867942056108177"),
    "upwards_black_arrow": ("▫️", "5260652420052032852"),
    "up_pointing_small_red_triangle": ("▫️", "5260379144167890225"),
    "personal_computer": ("▫️", "5258423306255604960"),
    "information_source": ("▫️", "5258503720928288433"),
    "slightly_smiling_face": ("▫️", "5258262708838472996"),
    "speaker_with_cancellation_stroke": ("▫️", "5258267368877989660"),
    "rising_chart": ("📊", "5258391025281408576"),
    "black_sun_with_rays": ("☀️", "5258089153505009279"),
    "books": ("📖", "5260512129240276089"),
    "package": ("▫️", "5258134813302332906"),
    "raised_hand": ("▫️", "5258362429389152256"),
    "videocassette": ("🎥", "5258391252914676042"),
    "upside_down_face": ("▫️", "5258318251355545562"),
    "clock_face_nine_oclock": ("🔒", "5199457120428249992"),
    "studio_microphone": ("📱", "5260652149469094137"),
    "gear": ("⚙️", "5258096772776991776"),
    "permanent_paper_sign": ("▫️", "5271934788037517525"),
    "speaker_with_three_sound_waves": ("👋", "5260325873688518261"),
    "newspaper": ("▫️", "5249231689695115145"),
    "label": ("▫️", "5296348778012361146"),
    "right_pointing_magnifying_glass": ("🔍", "5429571366384842791"),
    "eye": ("👁️", "5253959125838090076"),
    "no_entry": ("▫️", "5275969776668134187"),
    "no_one_under_eighteen_symbol": ("▫️", "5325604415900504150"),
    "fork_and_knife": ("▫️", "5296727963495079440"),
    "ton_crypto_gold_coin": ("🪙", "5382164415019768638"),
    "ton_crypto_airplane_departure": ("✈️", "5463424023734014980"),
    "ton_crypto_currency_exchange": ("▫️", "5377336227533969892"),
    "ton_crypto_money_bag": ("💰", "5417924076503062111"),
    "ton_crypto_spiral_calendar_pad": ("📅", "5472279086657199080"),
    "ton_crypto_open_lock": ("🔒", "5429405838345265327"),
    "ton_crypto_shopping_trolley": ("▫️", "5400090058030075645"),
    "ton_crypto_jigsaw_puzzle_piece": ("🧩", "5213306719215577669"),
    "ton_crypto_link_symbol": ("🔗", "5440410042773824003"),
    "ton_crypto_trophy": ("🏆", "5188344996356448758"),
    "ton_crypto_bar_chart": ("📊", "5203993413346680064"),
    "ton_crypto_pig_face": ("▫️", "5417831807720642261"),
    "ton_crypto_bank": ("▫️", "5238132025323444613"),
    "ton_crypto_sports_medal": ("🏅", "5424746623462823358"),
    "ton_crypto_magnet": ("▫️", "5202106638508512484"),
    "ton_crypto_cheering_megaphone": ("📱", "5298609030321691620"),
    "ton_crypto_dollar_banknote": ("💵", "5201873447554145566"),
    "ton_crypto_seedling": ("▫️", "5474417568053745249"),
    "ton_crypto_placard": ("🚗", "5429278861932124623"),
    "ton_crypto_rising_chart": ("📊", "5298614648138919107"),
    "ton_crypto_palm_up_hand": ("▫️", "5440457429147997980"),
    "ton_crypto_scales": ("▫️", "5461152608804689572"),
    "ton_crypto_telephone_receiver": ("📱", "5213179235996294999"),
    "ton_crypto_rocket": ("🚀", "5188481279963715781"),
    "ton_crypto_credit_card": ("🚗", "5472250091332993630"),
    "ton_crypto_world_map": ("🗺️", "5235794253149394263"),
    "ton_crypto_gem_stone": ("💎", "5462902520215002477"),
    "ton_crypto_label": ("▫️", "5298877105000439431"),
    "ton_crypto_direct_hit": ("▫️", "5461009483314517035"),
    "ton_crypto_envelope_with_downwards_arrow_above": ("▫️", "5472239203590888751"),
    "ton_crypto_speech_balloon": ("💬", "5235570365094188078"),
    "ton_crypto_pick": ("▫️", "5461047575379466857"),
    "ton_crypto_slot_machine": ("▫️", "5235989279024373566"),
    "ton_crypto_parachute": ("▫️", "5461128651477111908"),
    "ton_crypto_receipt": ("▫️", "5204242830687494041"),
    "ton_crypto_purse": ("👛", "5215420556089776398"),
    "ton_crypto_keyboard": ("🔑", "5298975240708187753"),
    "ton_crypto_key": ("🔑", "5307843983102204243"),
    "ton_crypto_battery": ("🔋", "5307905813451397794"),
    "news_eyes": ("👁️", "5210956306952758910"),
    "news_slightly_smiling_face": ("▫️", "5461117441612462242"),
    "news_high_voltage_sign": ("⚡", "5456140674028019486"),
    "news_comet": ("▫️", "5224607267797606837"),
    "news_shopping_bags": ("🛍️", "5229064374403998351"),
    "news_no_entry": ("▫️", "5260293700088511294"),
    "news_no_entry_sign": ("▫️", "5240241223632954241"),
    "news_heavy_exclamation_mark_symbol": ("▫️", "5274099962655816924"),
    "news_double_exclamation_mark": ("▫️", "5440660757194744323"),
    "news_exclamation_question_mark": ("▫️", "5314504236132747481"),
    "news_black_question_mark_ornament": ("▫️", "5436113877181941026"),
    "news_warning_sign": ("⚠️", "5447644880824181073"),
    "news_globe_with_meridians": ("🌐", "5447410659077661506"),
    "news_speech_balloon": ("💬", "5443038326535759644"),
    "news_thought_balloon": ("▫️", "5467538555158943525"),
    "news_bar_chart": ("📊", "5231200819986047254"),
    "news_up_pointing_small_red_triangle": ("▫️", "5449683594425410231"),
    "news_down_pointing_small_red_triangle": ("▫️", "5447183459602669338"),
    "news_candle": ("▫️", "5451882707875276247"),
    "news_rising_chart": ("📊", "5244837092042750681"),
    "news_falling_chart": ("📊", "5246762912428603768"),
    "news_check_mark": ("✅", "5206607081334906820"),
    "news_red_cross_mark": ("❌", "5210952531676504517"),
    "news_squared_cool": ("▫️", "5222079954421818267"),
    "news_bell": ("🔔", "5458603043203327669"),
    "news_disguised_face": ("▫️", "5391112412445288650"),
    "news_clown_face": ("▫️", "5269531045165816230"),
    "news_biting_lip": ("▫️", "5395444514028529554"),
    "news_pushpin": ("📌", "5397782960512444700"),
    "news_dollar_banknote": ("💵", "5409048419211682843"),
    "news_money_with_wings": ("💰", "5233326571099534068"),
    "news_currency_exchange": ("▫️", "5402186569006210455"),
    "news_black_right_pointing_triangle": ("▫️", "5264919878082509254"),
    "news_large_red_circle": ("▫️", "5411225014148014586"),
    "news_large_green_circle": ("▫️", "5416081784641168838"),
    "news_black_rightwards_arrow": ("▫️", "5416117059207572332"),
    "news_fire": ("🔥", "5424972470023104089"),
    "news_collision_symbol": ("▫️", "5276032951342088188"),
    "news_studio_microphone": ("📱", "5294339927318739359"),
    "news_microphone": ("📱", "5224736245665511429"),
    "news_cheering_megaphone": ("📱", "5424818078833715060"),
    "news_shushing_face": ("▫️", "5431609822288033666"),
    "news_thumbs_down": ("👍", "5449875686837726134"),
    "news_speaking_head_in_silhouette": ("▫️", "5460795800101594035"),
    "news_left_pointing_magnifying_glass": ("🔍", "5231012545799666522"),
    "news_shield": ("🛡️", "5251203410396458957"),
    "yemeny": ("✅", "5807946423110475878"),
}


for _k, _v in EXTRA.items():
    EMOJI.setdefault(_k, _v)


# ── inline button icons (icon_custom_emoji_id) ──────────────────────────────
# Only ids that survive `get_custom_emoji_stickers` AND look right at 20px.
ICONS: dict[str, str] = {
    "crown":    "6311999820714220870",
    "gift":     "6312196994072847118",
    "gem":      "6310032545304026289",
    "star":     "6309890192907968770",
    "check":    "6310103949135322908",
    "verify":   "6310103949135322908",
    "cross":    "6312156428106737991",
    "delete":   "6312156428106737991",
    "skip":     "6312156428106737991",
    "end":      "6312156428106737991",
    "warning":  "6100590432209604692",
    "fire":     "6309811869884358547",
    "rocket":   "6309870788245724520",
    "trophy":   "6311834808070708173",
    "target":   "5310278924616356636",
    "bolt":     "6309883501348919953",
    "clover":   "5395325195542078574",
    "money":    "6310069275864341980",
    "export":   "6310069275864341980",
    "party":    "6309961712703379735",
    "chart":    "6309843875980648126",
    "stats":    "6309843875980648126",
    "users":    "5316887736823591263",
    "group":    "5316887736823591263",
    "ballot":   "5359741159566484212",
    "vote":     "5359741159566484212",
    "timer":    "5382194935057372936",
    "calendar": "5431897022456145283",
    "pin":      "6309960153630251694",
    "info":     "6309960153630251694",
    "flag":     "5460755126761312667",
    "back":     "5460755126761312667",
    "link":     "6309893061946121745",
    "share":    "6053308421443161790",
    "channel":  "6053308421443161790",
    "megaphone": "6053308421443161790",
    "lock":     "5472308992514464048",
    "shield":   "5197288647275071607",
    "admin":    "5197288647275071607",
    "handshake": "5395732581780040886",
    "heart":    "6309591606781549616",
    "sparkle":  "6140943183258849599",
    "refresh":  "",      # no clean premium sticker → colour-only button
    "plus":     "",
    "minus":    "",
    "photo":    "",
}

_TOKEN = re.compile(r"\{e:([a-z_0-9]+)\}")

# unicode fallback -> custom_emoji_id (first mapping wins, longest key first)
BY_CHAR: dict[str, str] = {}
for _name, (_fallback, _cid) in EMOJI.items():
    if _cid and _fallback != "▫️" and _fallback not in BY_CHAR:
        BY_CHAR[_fallback] = _cid

_EMOJI_RE = re.compile("|".join(re.escape(c) for c in sorted(BY_CHAR, key=len, reverse=True)))


# Skip existing <tg-emoji>, inline <code>/<pre> blocks (Telegram forbids nested tags inside code),
# and raw HTML tags so attributes like href="..." are never altered.
_TG_TAG = re.compile(
    r"<tg-emoji[^>]*>.*?</tg-emoji>|<code[^>]*>.*?</code>|<pre[^>]*>.*?</pre>|<[^>]+>",
    re.S,
)


def _premiumize_chunk(chunk: str) -> str:
    return _EMOJI_RE.sub(
        lambda m: f'<tg-emoji emoji-id="{BY_CHAR[m.group(0)]}">{m.group(0)}</tg-emoji>', chunk)


def premiumize(text: str) -> str:
    """Convert raw unicode emojis in HTML text into Telegram <tg-emoji> custom emojis."""
    if not text or not config.PREMIUM_EMOJI:
        return text or ""
    parts, tags = [], []
    pos = 0
    for m in _TG_TAG.finditer(text):
        parts.append(text[pos:m.start()])
        tags.append(m.group(0))
        pos = m.end()
    parts.append(text[pos:])

    out = []
    for i, chunk in enumerate(parts):
        out.append(_premiumize_chunk(chunk))
        if i < len(tags):
            out.append(tags[i])
    return "".join(out)


def catalogue() -> list[tuple[str, str, tuple[str, ...]]]:
    """(fallback, id, names) — one row per distinct sticker, aliases grouped."""
    grouped: dict[str, list[str]] = {}
    fallbacks: dict[str, str] = {}
    for name, (fallback, cid) in EMOJI.items():
        if not cid:
            continue
        grouped.setdefault(cid, []).append(name)
        fallbacks.setdefault(cid, fallback)
    return [(fallbacks[cid], cid, tuple(names)) for cid, names in grouped.items()]


def pe(name: str) -> str:
    """Return <tg-emoji> custom emoji tag (falls back to unicode when id is empty or disabled)."""
    try:
        fallback, emoji_id = EMOJI[name]
    except KeyError:
        raise KeyError(f"unknown premium emoji: {name!r}") from None
    if not config.PREMIUM_EMOJI or not emoji_id:
        return fallback
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'


def render(text: str) -> str:
    """Replace every {e:name} token in `text` with its premium emoji."""
    return _TOKEN.sub(lambda m: pe(m.group(1)), text)


def icon(name: str) -> str | None:
    """Return custom emoji id for inline button icons (Bot API 9.4+)."""
    if not config.PREMIUM_EMOJI or not name:
        return None
    return ICONS.get(name) or None

premium = types.SimpleNamespace(
    EMOJI=EMOJI,
    EXTRA=EXTRA,
    ICONS=ICONS,
    _TOKEN=_TOKEN,
    BY_CHAR=BY_CHAR,
    _EMOJI_RE=_EMOJI_RE,
    _TG_TAG=_TG_TAG,
    _premiumize_chunk=_premiumize_chunk,
    premiumize=premiumize,
    catalogue=catalogue,
    pe=pe,
    render=render,
    icon=icon,
)


# ══════════════════════════════════════════════════════════════════
#  LINES
# ══════════════════════════════════════════════════════════════════
"""Line & quote engine for NEXT GEN GIVEAWAYS.

Every card, announcement and result banner gets a fresh aesthetic one-liner.

Two sources:
  1. A built-in pool of hand-written lines  -> always available, instant, free.
  2. An optional *cheap* OpenAI-compatible API (OpenRouter free models, Groq,
     DeepInfra, local llama.cpp...) -> refills a small cache in the background.

The API is never allowed to block a reply: `get_line()` always returns
immediately from the cache or the local pool, and quietly tops the cache up
whenever it runs low. If the key is missing the bot simply never calls out.
"""
import asyncio
import logging
import random

import httpx


log_lines = logging.getLogger(__name__)

# ── built-in pool (short, aesthetic, giveaway flavoured) ────────────────────
POOL: list[str] = [
    "Fortune favours the ones who show up. {e:fire}",
    "Some win by luck. Legends win by showing up daily. {e:crown}",
    "One tap today, one trophy tomorrow. {e:trophy}",
    "The grind is silent, the results are loud. {e:chart}",
    "Winners are just participants who never left. {e:target}",
    "Your name deserves to be on that card. {e:gem}",
    "Small steps, royal results. {e:crown}",
    "Money moves to the patient ones. {e:money_wings}",
    "Every giveaway has one hero. Why not you? {e:star}",
    "Screenshot the doubt, show them the trophy. {e:trophy}",
    "The loudest flex is consistency. {e:bolt}",
    "Luck is a payment for the days nobody clapped. {e:clap}",
    "Be early, be active, be unforgettable. {e:rocket}",
    "Your future self is watching this moment. {e:eyes}",
    "Crowns are handed out, not borrowed. {e:crown}",
    "Keep the circle premium, keep the vibes clean. {e:sparkle}",
    "A single entry can rewrite the whole month. {e:ticket}",
    "Show up for the shot you said you wanted. {e:target}",
    "The card is live — make it look expensive. {e:credit_card}",
    "Numbers climb quietly, then all at once. {e:chart}",
    "Winners treat every round like the final one. {e:fire}",
    "Free to enter, priceless to win. {e:gift}",
    "Some doors only open for the ones still knocking. {e:bell}",
    "Your vote is worth more than your doubt. {e:ballot}",
    "Dream in gold, move in silence. {e:medal}",
    "Trophies love the persistent. {e:trophy}",
    "No shortcuts — only momentum. {e:bolt}",
    "Stay in the channel, stay in the story. {e:bookmark}",
    "Great things start with one tap. {e:clover}",
    "The best time to enter is before the hype. {e:hourglass}",
    "You cannot lose a round you never skipped. {e:shield}",
    "Aesthetic energy, winner's mindset. {e:sparkle}",
    "Real ones support real ones. {e:handshake}",
    "Claim your seat before the table fills. {e:crystal}",
    "Every legend had a first entry. {e:star}",
    "Don't watch the giveaway — be the giveaway's headline. {e:megaphone}",
    "Quiet grinders inherit the loud prizes. {e:dollar}",
    "The winner's list has room for one more. {e:check}",
    "Trust the process, log the wins. {e:chart}",
    "Keep your name in the room. {e:pushpin}",
    "Gold remembers those who stayed. {e:coin}",
    "Votes are respect, and respect is earned. {e:heart_fire}",
    "Give luck a place to land. {e:clover}",
    "Play bold. Win clean. Repeat. {e:trophy}",
    "The door is open, the crown is loose. {e:crown}",
]

TAGS = {
    "card": "a stylish one-line caption for a participant's voting card",
    "welcome": "a short welcome line for someone opening a giveaway bot",
    "created": "a hype line announcing that a new giveaway just went live",
    "result": "a dramatic one-line closer announcing the winner of a giveaway",
    "vote": "a tiny thank-you line after someone's vote is counted",
    "idle": "a short motivational aesthetic quote for a Telegram channel",
}

_cache: list[str] = []
_refilling = False
_lock = asyncio.Lock()


async def _fetch_batch(kind: str, n: int = 5) -> list[str]:
    """Ask the cheap API for a few fresh lines. Never raises."""
    if not config.LINES_API_KEY or not config.LINES_API_BASE:
        return []
    ask = TAGS.get(kind, TAGS["idle"])
    prompt = (
        f"Write {n} {ask}. Each line is max 12 words, aesthetic, confident, "
        "no hashtags, no emojis at the start, no numbering, no quotes around it. "
        f"The brand is {config.BRAND}. Put each line on its own line."
    )
    payload = {
        "model": config.LINES_API_MODEL,
        "messages": [
            {"role": "system", "content": "You write short, punchy premium Telegram giveaway copy."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 1.15,
        "max_tokens": 260,
    }
    headers = {
        "Authorization": f"Bearer {config.LINES_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": config.MAIN_CHANNEL_URL,
        "X-Title": config.BRAND,
    }
    try:
        async with httpx.AsyncClient(timeout=config.LINES_API_TIMEOUT) as client:
            r = await client.post(
                config.LINES_API_BASE.rstrip("/") + "/chat/completions",
                json=payload, headers=headers,
            )
            r.raise_for_status()
            text = r.json()["choices"][0]["message"]["content"]
    except Exception as exc:                       # noqa: BLE001 - never fatal
        log_lines.warning("line API unavailable (%s) — using local pool", exc)
        return []

    out = []
    for raw in text.splitlines():
        line = raw.strip().lstrip("-•*0123456789.) ").strip().strip('"').strip()
        if 12 <= len(line) <= 140:
            out.append(line)
    log_lines.info("line API supplied %s fresh lines", len(out))
    return out[:n]


async def _topup(kind: str) -> None:
    global _refilling
    async with _lock:
        if _refilling or len(_cache) >= 4:
            return
        _refilling = True
    try:
        fresh = await _fetch_batch(kind)
        _cache.extend(fresh)
    finally:
        _refilling = False


async def get_line(kind: str = "idle") -> str:
    """Return one line immediately; refresh the cache in the background."""
    if config.LINES_API_KEY:
        if _cache:
            line = _cache.pop(0)
        else:
            line = random.choice(POOL)
        if len(_cache) < 4:
            asyncio.create_task(_topup(kind))
        return line
    return random.choice(POOL)


def get_line_sync(kind: str = "idle") -> str:
    """Same as get_line but for places that cannot await."""
    return random.choice(POOL)

lines = types.SimpleNamespace(
    log_lines=log_lines,
    POOL=POOL,
    TAGS=TAGS,
    _cache=_cache,
    _refilling=_refilling,
    _lock=_lock,
    _fetch_batch=_fetch_batch,
    _topup=_topup,
    get_line=get_line,
    get_line_sync=get_line_sync,
    log=log_lines,
)


# ══════════════════════════════════════════════════════════════════
#  DB
# ══════════════════════════════════════════════════════════════════
"""SQLite storage for NEXT GEN GIVEAWAYS (auto-migrates older databases)."""
import aiosqlite


SCHEMA = """
CREATE TABLE IF NOT EXISTS giveaways (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    prize       TEXT    DEFAULT '',
    photo       TEXT    DEFAULT '',
    creator_id  INTEGER NOT NULL,
    created_at  TEXT    NOT NULL,
    ends_at     TEXT    NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS participants (
    giveaway_id  INTEGER NOT NULL,
    user_id      INTEGER NOT NULL,
    full_name    TEXT    NOT NULL,
    username     TEXT,
    message_id   INTEGER,
    message_kind TEXT    NOT NULL DEFAULT 'text',
    joined_at    TEXT    NOT NULL,
    PRIMARY KEY (giveaway_id, user_id),
    FOREIGN KEY (giveaway_id) REFERENCES giveaways(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS votes (
    giveaway_id    INTEGER NOT NULL,
    voter_id       INTEGER NOT NULL,
    participant_id INTEGER NOT NULL,
    voted_at       TEXT    NOT NULL,
    PRIMARY KEY (giveaway_id, voter_id),
    FOREIGN KEY (giveaway_id, participant_id)
        REFERENCES participants(giveaway_id, user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vote_adjust (
    giveaway_id    INTEGER NOT NULL,
    participant_id INTEGER NOT NULL,
    delta          INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (giveaway_id, participant_id)
);

CREATE TABLE IF NOT EXISTS gate_channels (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id     INTEGER,
    username    TEXT,
    title       TEXT    DEFAULT '',
    invite_link TEXT    DEFAULT '',
    added_by    INTEGER,
    added_at    TEXT,
    UNIQUE(chat_id)
);

CREATE TABLE IF NOT EXISTS admins (
    user_id  INTEGER PRIMARY KEY,
    added_by INTEGER NOT NULL,
    added_at TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    user_id    INTEGER PRIMARY KEY,
    full_name  TEXT    NOT NULL,
    username   TEXT,
    joined_at  TEXT    NOT NULL,
    verified   INTEGER NOT NULL DEFAULT 0,
    active     INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_votes_target  ON votes(giveaway_id, participant_id);
CREATE INDEX IF NOT EXISTS idx_giveaways_st  ON giveaways(status, ends_at);
"""

MIGRATIONS = [
    "ALTER TABLE giveaways ADD COLUMN photo TEXT DEFAULT ''",
    "ALTER TABLE users ADD COLUMN active INTEGER NOT NULL DEFAULT 1",
    "ALTER TABLE giveaways ADD COLUMN channel_msg_id INTEGER DEFAULT 0",
    "ALTER TABLE giveaways ADD COLUMN media_kind TEXT DEFAULT 'photo'",
]


async def init_db() -> None:
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        await db.executescript(SCHEMA)
        for stmt in MIGRATIONS:                    # safe on fresh + old DBs
            try:
                await db.execute(stmt)
            except Exception:
                pass
        await db.commit()


async def one(query: str, params=()):
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cur:
            return await cur.fetchone()


async def all_(query: str, params=()):
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cur:
            return await cur.fetchall()


async def run(query: str, params=()) -> int:
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys=ON")
        cur = await db.execute(query, params)
        await db.commit()
        return cur.lastrowid if cur.lastrowid else cur.rowcount


# ── users (everyone who ever opened the bot) ───────────────────────────────
async def upsert_user(user_id: int, full_name: str, username, stamp: str) -> None:
    await run(
        """INSERT INTO users(user_id, full_name, username, joined_at, verified)
           VALUES(?,?,?,?,0)
           ON CONFLICT(user_id) DO UPDATE SET
             full_name=excluded.full_name, username=excluded.username, active=1""",
        (user_id, full_name, username, stamp))


async def set_verified(user_id: int, verified: bool = True) -> None:
    await run("UPDATE users SET verified=?, active=1 WHERE user_id=?",
              (1 if verified else 0, user_id))


async def is_verified(user_id: int) -> bool:
    row = await one("SELECT verified FROM users WHERE user_id=?", (user_id,))
    return bool(row and row["verified"])


async def broadcast_targets():
    return await all_("SELECT user_id FROM users WHERE verified=1 AND active=1")


async def deactivate_user(user_id: int) -> None:
    await run("UPDATE users SET active=0 WHERE user_id=?", (user_id,))


# ── admins ──────────────────────────────────────────────────────────────────
async def is_admin(user_id: int) -> bool:
    if user_id in config.OWNER_IDS:
        return True
    row = await one("SELECT 1 AS x FROM admins WHERE user_id=?", (user_id,))
    return row is not None


async def add_admin(user_id: int, added_by: int, stamp: str) -> bool:
    if user_id in config.OWNER_IDS:
        return False
    await run("INSERT OR IGNORE INTO admins(user_id, added_by, added_at) VALUES(?,?,?)",
              (user_id, added_by, stamp))
    return True


async def del_admin(user_id: int) -> bool:
    return await run("DELETE FROM admins WHERE user_id=?", (user_id,)) > 0


async def list_admins():
    return await all_("SELECT user_id, added_by, added_at FROM admins ORDER BY added_at")


# ── giveaways ───────────────────────────────────────────────────────────────
async def create_giveaway(name: str, prize: str, photo: str, creator_id: int,
                          created: str, ends: str, media_kind: str = "photo") -> int:
    return await run(
        "INSERT INTO giveaways(name, prize, photo, creator_id, created_at, ends_at, status, media_kind) "
        "VALUES(?,?,?,?,?,?,'active',?)",
        (name, prize, photo or "", creator_id, created, ends, media_kind or "photo"))


async def get_giveaway(giveaway_id: int):
    return await one("SELECT * FROM giveaways WHERE id=?", (giveaway_id,))


async def giveaway_stats_row(giveaway_id: int):
    return await one(
        """SELECT g.*,
                  (SELECT COUNT(*) FROM participants p WHERE p.giveaway_id=g.id) AS participants,
                  (SELECT COUNT(*) FROM votes v WHERE v.giveaway_id=g.id)        AS votes
           FROM giveaways g WHERE g.id=?""", (giveaway_id,))


async def list_giveaways(status: str, limit: int = 30):
    return await all_(
        """SELECT g.*,
                  (SELECT COUNT(*) FROM participants p WHERE p.giveaway_id=g.id) AS participants,
                  (SELECT COUNT(*) FROM votes v WHERE v.giveaway_id=g.id)        AS votes
           FROM giveaways g WHERE g.status=? ORDER BY g.id DESC LIMIT ?""",
        (status, limit))


async def any_giveaways(limit: int = 30):
    return await all_(
        """SELECT g.*,
                  (SELECT COUNT(*) FROM participants p WHERE p.giveaway_id=g.id) AS participants,
                  (SELECT COUNT(*) FROM votes v WHERE v.giveaway_id=g.id)        AS votes
           FROM giveaways g ORDER BY (g.status='active') DESC, g.id DESC LIMIT ?""", (limit,))


async def mark_finished(giveaway_id: int) -> bool:
    return await run("UPDATE giveaways SET status='finished' WHERE id=? AND status='active'",
                     (giveaway_id,)) > 0


async def set_giveaway_post(giveaway_id: int, message_id: int) -> None:
    await run("UPDATE giveaways SET channel_msg_id=? WHERE id=?", (message_id, giveaway_id))


async def due_giveaways(stamp: str):
    return await all_("SELECT id FROM giveaways WHERE status='active' AND ends_at<=?", (stamp,))


# ── participants ────────────────────────────────────────────────────────────
async def add_participant(giveaway_id: int, user_id: int, name: str, username, joined: str) -> bool:
    return bool(await run(
        """INSERT INTO participants(giveaway_id,user_id,full_name,username,joined_at)
           VALUES(?,?,?,?,?) ON CONFLICT DO NOTHING""",
        (giveaway_id, user_id, name, username, joined)))


async def get_participant(giveaway_id: int, user_id: int):
    return await one("SELECT * FROM participants WHERE giveaway_id=? AND user_id=?",
                     (giveaway_id, user_id))


async def set_participant_post(giveaway_id: int, user_id: int, message_id: int, kind: str):
    await run("UPDATE participants SET message_id=?, message_kind=? WHERE giveaway_id=? AND user_id=?",
              (message_id, kind, giveaway_id, user_id))


async def all_participants(giveaway_id: int):
    return await all_("SELECT user_id, full_name, username FROM participants "
                      "WHERE giveaway_id=? ORDER BY joined_at", (giveaway_id,))


# ── extra force-join channels (the main channel lives in config) ────────────
async def add_gate_channel(chat_id: int, username, title, invite_link,
                           added_by: int, stamp: str) -> None:
    await run(
        """INSERT INTO gate_channels(chat_id, username, title, invite_link, added_by, added_at)
           VALUES(?,?,?,?,?,?)
           ON CONFLICT(chat_id) DO UPDATE SET
             username=excluded.username, title=excluded.title,
             invite_link=excluded.invite_link, added_at=excluded.added_at""",
        (chat_id, username, title, invite_link, added_by, stamp))


async def list_gate_channels():
    return await all_("SELECT * FROM gate_channels ORDER BY id")


async def del_gate_channel(row_id: int) -> bool:
    return await run("DELETE FROM gate_channels WHERE id=?", (row_id,)) > 0


async def get_setting(key: str, default: str = "") -> str:
    row = await one("SELECT value FROM settings WHERE key=?", (key,))
    if not row:
        return default
    return str(row["value"] or default)


async def set_setting(key: str, value: str) -> None:
    await run(
        """INSERT INTO settings(key, value) VALUES(?,?)
           ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
        (key, value or ""))


async def cheap_api_url() -> str:
    """Optional extra promo link on vote cards — not a required join."""
    stored = (await get_setting("cheap_api_url")).strip()
    return stored or (config.CHEAP_API_URL or "").strip()


async def claim_handle() -> str:
    """Prize-claim @handle or link (editable live via /setclaim)."""
    stored = (await get_setting("claim_handle")).strip()
    return stored or (config.CLAIM_HANDLE or config.MAIN_CHANNEL_USERNAME).strip()


async def claim_url() -> str:
    h = await claim_handle()
    if h.startswith("http://") or h.startswith("https://"):
        return h
    return "https://t.me/" + h.lstrip("@")


# ── votes (real + admin adjustment) ─────────────────────────────────────────
REAL = "SELECT COUNT(*) FROM votes v WHERE v.giveaway_id=p.giveaway_id AND v.participant_id=p.user_id"
ADJ = "SELECT COALESCE(SUM(a.delta),0) FROM vote_adjust a WHERE a.giveaway_id=p.giveaway_id AND a.participant_id=p.user_id"


async def real_votes(giveaway_id: int, participant_id: int) -> int:
    row = await one("SELECT COUNT(*) AS c FROM votes WHERE giveaway_id=? AND participant_id=?",
                    (giveaway_id, participant_id))
    return int(row["c"]) if row else 0


async def adjust_of(giveaway_id: int, participant_id: int) -> int:
    row = await one("SELECT COALESCE(SUM(delta),0) AS d FROM vote_adjust "
                    "WHERE giveaway_id=? AND participant_id=?", (giveaway_id, participant_id))
    return int(row["d"]) if row else 0


async def votes_for(giveaway_id: int, participant_id: int) -> int:
    return max(0, await real_votes(giveaway_id, participant_id)
               + await adjust_of(giveaway_id, participant_id))


async def ranking(giveaway_id: int):
    return await all_(
        f"""SELECT p.user_id, p.full_name, p.username, p.joined_at,
                   ({REAL}) AS real_votes,
                   MAX(0, ({REAL}) + ({ADJ})) AS votes
            FROM participants p
            WHERE p.giveaway_id=?
            ORDER BY votes DESC, p.joined_at ASC""", (giveaway_id,))


async def rank_of(giveaway_id: int, user_id: int):
    rows = await ranking(giveaway_id)
    highest = max([int(r["votes"]) for r in rows] or [0])
    for i, r in enumerate(rows, 1):
        if r["user_id"] == user_id:
            return i, len(rows), int(r["votes"]), highest
    return 0, len(rows), 0, highest


async def cast_vote(giveaway_id: int, voter_id: int, participant_id: int, stamp: str):
    await run(
        """INSERT INTO votes(giveaway_id,voter_id,participant_id,voted_at)
           VALUES(?,?,?,?)
           ON CONFLICT(giveaway_id,voter_id) DO UPDATE SET
             participant_id=excluded.participant_id, voted_at=excluded.voted_at""",
        (giveaway_id, voter_id, participant_id, stamp))


async def previous_vote(giveaway_id: int, voter_id: int):
    return await one("SELECT participant_id FROM votes WHERE giveaway_id=? AND voter_id=?",
                     (giveaway_id, voter_id))


async def voters_of(giveaway_id: int, participant_id: int):
    return await all_(
        """SELECT v.voter_id, u.full_name, u.username, v.voted_at
           FROM votes v LEFT JOIN users u ON u.user_id = v.voter_id
           WHERE v.giveaway_id=? AND v.participant_id=? ORDER BY v.voted_at""",
        (giveaway_id, participant_id))


async def drop_votes_by_voter(voter_id: int):
    rows = await all_("SELECT giveaway_id, participant_id FROM votes WHERE voter_id=?", (voter_id,))
    await run("DELETE FROM votes WHERE voter_id=?", (voter_id,))
    return rows


async def add_adjust(giveaway_id: int, participant_id: int, delta: int) -> None:
    await run(
        """INSERT INTO vote_adjust(giveaway_id, participant_id, delta) VALUES(?,?,?)
           ON CONFLICT(giveaway_id,participant_id) DO UPDATE SET delta = delta + excluded.delta""",
        (giveaway_id, participant_id, delta))


async def reset_adjust(giveaway_id: int, participant_id: int) -> None:
    """Make the total 0 by cancelling every real vote with an adjustment."""
    real = await real_votes(giveaway_id, participant_id)
    await run("DELETE FROM vote_adjust WHERE giveaway_id=? AND participant_id=?",
              (giveaway_id, participant_id))
    if real:
        await add_adjust(giveaway_id, participant_id, -real)


async def overall_stats():
    return await one(
        """SELECT (SELECT COUNT(*) FROM giveaways)                         AS giveaways,
                  (SELECT COUNT(*) FROM giveaways WHERE status='active')  AS active,
                  (SELECT COUNT(*) FROM giveaways WHERE status='finished') AS finished,
                  (SELECT COUNT(*) FROM participants)                     AS entries,
                  (SELECT COUNT(*) FROM users WHERE verified=1)            AS users,
                  (SELECT COUNT(*) FROM votes)                            AS votes""")

db = types.SimpleNamespace(
    SCHEMA=SCHEMA,
    MIGRATIONS=MIGRATIONS,
    init_db=init_db,
    one=one,
    all_=all_,
    run=run,
    upsert_user=upsert_user,
    set_verified=set_verified,
    is_verified=is_verified,
    broadcast_targets=broadcast_targets,
    deactivate_user=deactivate_user,
    is_admin=is_admin,
    add_admin=add_admin,
    del_admin=del_admin,
    list_admins=list_admins,
    create_giveaway=create_giveaway,
    get_giveaway=get_giveaway,
    giveaway_stats_row=giveaway_stats_row,
    list_giveaways=list_giveaways,
    any_giveaways=any_giveaways,
    mark_finished=mark_finished,
    set_giveaway_post=set_giveaway_post,
    due_giveaways=due_giveaways,
    add_participant=add_participant,
    get_participant=get_participant,
    set_participant_post=set_participant_post,
    all_participants=all_participants,
    add_gate_channel=add_gate_channel,
    list_gate_channels=list_gate_channels,
    del_gate_channel=del_gate_channel,
    get_setting=get_setting,
    set_setting=set_setting,
    cheap_api_url=cheap_api_url,
    claim_handle=claim_handle,
    claim_url=claim_url,
    REAL=REAL,
    ADJ=ADJ,
    real_votes=real_votes,
    adjust_of=adjust_of,
    votes_for=votes_for,
    ranking=ranking,
    rank_of=rank_of,
    cast_vote=cast_vote,
    previous_vote=previous_vote,
    voters_of=voters_of,
    drop_votes_by_voter=drop_votes_by_voter,
    add_adjust=add_adjust,
    reset_adjust=reset_adjust,
    overall_stats=overall_stats,
)


# ══════════════════════════════════════════════════════════════════
#  CARDS
# ══════════════════════════════════════════════════════════════════
"""All copy for NEXT GEN GIVEAWAYS — short, premium-emoji styled.

House rules for this file:
  * one idea per line, no filler sentences
  * hosted by TG MANDI (@tgmandi) displayed prominently
  * the quote (the aesthetic line) sits in a <blockquote> right under the header
"""
import hashlib
import html
from datetime import datetime, timezone


R = render
def host_line() -> str:
    return R("{e:verified} Hosted by <b>{host}</b> · {ch}").format(
        host=esc(config.HOST_NAME), ch=esc(config.MAIN_CHANNEL_USERNAME))


API_TAG = "{e:verified} Hosted by <b>" + config.HOST_NAME + "</b> · " + config.MAIN_CHANNEL_USERNAME


def esc(v) -> str:
    return html.escape(str(v or ""))


def flair(raw: str) -> str:
    """Escape a line, then turn its {e:name} tokens into premium emoji."""
    return render(esc(raw))


def fmt_dt(iso: str, style: str = "%d %b %Y · %H:%M UTC") -> str:
    try:
        return datetime.fromisoformat(iso).astimezone(timezone.utc).strftime(style)
    except Exception:
        return iso or "—"


def until(iso: str) -> str:
    try:
        delta = datetime.fromisoformat(iso) - datetime.now(timezone.utc)
    except Exception:
        return "—"
    secs = max(0, int(delta.total_seconds()))
    d, rem = divmod(secs, 86400)
    h, rem = divmod(rem, 3600)
    m = rem // 60
    if d:
        return f"{d}d {h}h"
    if h:
        return f"{h}h {m}m"
    return f"{m}m"


def bar(votes: int, highest: int, slots: int = 10) -> str:
    """10-slot progress bar relative to the current leader."""
    if highest <= 0:
        return "▱" * slots
    filled = max(1, min(slots, round(votes / highest * slots)))
    return "▰" * filled + "▱" * (slots - filled)


def pct_of_leader(votes: int, highest: int) -> int:
    if highest <= 0:
        return 0
    return min(100, round(votes / highest * 100))


# ── join gate ───────────────────────────────────────────────────────────────
async def gate_text(name: str, gates=None, joined=None) -> str:
    line = await lines.get_line("welcome")
    gates = gates or [
        {"key": "main_channel", "title": f"{config.MAIN_CHANNEL_TITLE} ({config.MAIN_CHANNEL_USERNAME})",
         "url": config.MAIN_CHANNEL_URL, "role": "Main Channel"},
        {"key": "giveaway_channel", "title": config.GIVEAWAY_CHANNEL_USERNAME,
         "url": config.GIVEAWAY_CHANNEL_URL, "role": "Giveaway Channel"},
        {"key": "main_group", "title": config.GROUP_USERNAME,
         "url": config.GROUP_URL, "role": "Community Group"},
    ]
    joined = set(joined or ())
    rows = []
    missing_count = 0
    for g in gates:
        gkey = g.get("key") or g["title"]
        is_in = (gkey in joined) or (g["title"] in joined)
        if not is_in:
            missing_count += 1
        mark = R("{e:check_plain}") if is_in else R("{e:cross}")
        role = f" · <i>{esc(g['role'])}</i>" if g.get("role") else ""
        rows.append(f"{mark} <b>{esc(g['title'])}</b>{role}")
    prompt = (
        R("{e:pushpin} Join the remaining chat, then tap <b>Verify</b>")
        if missing_count == 1 else
        R("{e:pushpin} Join all {n} required channels & group, then tap <b>Verify</b>").format(n=missing_count)
    )
    return R(
        "{e:star_gold} <b>{brand}</b>\n"
        "{host_line}\n"
        "\n"
        "{e:lock} <b>Join to unlock</b>\n"
        "<blockquote>{line}</blockquote>\n"
        "\n"
        "{list}\n"
        "\n"
        "{prompt}"
    ).format(
        brand=esc(config.BRAND),
        host_line=host_line(),
        line=flair(line),
        list="\n".join(rows),
        prompt=prompt,
    )


async def verify_failed() -> str:
    return R("{e:cross} Not verified — join both channels & the group first, then tap <b>Verify</b>")


# ── welcome ─────────────────────────────────────────────────────────────────
async def welcome(name: str, is_admin: bool) -> str:
    line = await lines.get_line("welcome")
    extra = R("\n\n{e:crown} <b>Admin</b> — /admin") if is_admin else ""
    return R(
        "{e:star_gold} <b>{brand}</b>\n"
        "{e:wave} <b>Hey {name}</b>\n"
        "<blockquote>{line}</blockquote>\n"
        "\n"
        "{e:gift} Enter a giveaway · collect votes · win\n"
        "{e:shield} One vote per verified member\n"
        "{host_line}{extra}"
    ).format(
        brand=esc(config.BRAND),
        name=esc(name),
        line=flair(line),
        host_line=host_line(),
        extra=extra,
    )


async def how_it_works() -> str:
    return R(
        "{e:thinking} <b>How it works — {brand}</b>\n"
        "{host_line}\n"
        "\n"
        "{e:verified} <b>1.</b> Join {main_ch}, {gch} & {grp} → tap <b>Verify</b>\n"
        "{e:gift} <b>2.</b> Enter a giveaway → your card goes live in {gch}\n"
        "{e:share} <b>3.</b> Share your card to collect votes\n"
        "{e:trophy} <b>4.</b> Most votes wins\n"
        "\n"
        "{e:warning} Leave any required channel or group → votes dropped"
    ).format(
        brand=esc(config.BRAND),
        host_line=host_line(),
        main_ch=esc(config.MAIN_CHANNEL_USERNAME),
        gch=esc(config.GIVEAWAY_CHANNEL_USERNAME),
        grp=esc(config.GROUP_USERNAME),
    )


# ── giveaway card ───────────────────────────────────────────────────────────
async def giveaway_card(row, compact: bool = False) -> str:
    line = await lines.get_line("created")
    state = R("{e:fire} <b>OPEN</b>") if row["status"] == "active" else R("{e:flag} <b>CLOSED</b>")
    prize = row["prize"] or "Surprise drop"
    if compact:
        return R(
            "{e:star_gold} <b>{brand}</b>\n"
            "{e:gift} <b>{name}</b>\n"
            "<i>{line}</i>\n"
            "\n"
            "{e:gem} {prize}\n"
            "{e:hourglass} <b>{left}</b> left · {e:users} <b>{n}</b> in · {state}\n"
            "\n"
            "{host_line}"
        ).format(
            brand=esc(config.BRAND),
            name=esc(row["name"]),
            line=flair(line),
            prize=esc(prize),
            left=until(row["ends_at"]),
            n=row["participants"],
            state=state,
            host_line=host_line(),
        )
    return R(
        "{e:star_gold} <b>{brand}</b>\n"
        "<blockquote>{line}</blockquote>\n"
        "\n"
        "{e:gift} <b>{name}</b>\n"
        "{e:gem} {prize}\n"
        "{e:hourglass} <b>{left}</b> left · {e:users} <b>{n}</b> in · {state}\n"
        "\n"
        "{host_line}"
    ).format(
        brand=esc(config.BRAND),
        line=flair(line),
        name=esc(row["name"]),
        prize=esc(prize),
        left=until(row["ends_at"]),
        n=row["participants"],
        state=state,
        host_line=host_line(),
    )


# ── unique participant card ─────────────────────────────────────────────────
_CARD_THEMES = [
    {"code": "ONYX",   "fill": "▓", "empty": "░", "rule": "━", "mark": "◆"},
    {"code": "AURORA", "fill": "▰", "empty": "▱", "rule": "─", "mark": "✦"},
    {"code": "NOVA",   "fill": "■", "empty": "□", "rule": "═", "mark": "◇"},
    {"code": "EMBER",  "fill": "▮", "empty": "▯", "rule": "┈", "mark": "✶"},
    {"code": "TIDAL",  "fill": "●", "empty": "○", "rule": "∙", "mark": "◈"},
    {"code": "IVORY",  "fill": "◆", "empty": "◇", "rule": "·", "mark": "✧"},
]


def card_fingerprint(giveaway_id: int, user_id: int) -> dict:
    """Stable unique identity for one participant card (same ids → same look)."""
    digest = hashlib.sha256(f"{giveaway_id}:{user_id}:ng-card".encode()).hexdigest()
    n = int(digest[:12], 16)
    theme = _CARD_THEMES[n % len(_CARD_THEMES)]
    serial = digest[:8].upper()
    layout = n % 3
    return {
        "id": f"NG-{serial[:4]}-{serial[4:]}",
        "theme": theme,
        "layout": layout,
        "seal": digest[8:12].upper(),
    }


def unique_bar(votes: int, highest: int, fill: str, empty: str, slots: int = 10) -> str:
    if highest <= 0:
        return empty * slots
    filled = max(1, min(slots, round(votes / highest * slots)))
    return fill * filled + empty * (slots - filled)


# ── participant card ────────────────────────────────────────────────────────
async def participant_caption(giveaway_id: int, user_id: int, ended: bool = False) -> str:
    row = await db.one(
        """SELECT p.*, g.name AS giveaway_name, g.prize, g.ends_at, g.status
           FROM participants p
           JOIN giveaways g ON g.id = p.giveaway_id
           WHERE p.giveaway_id=? AND p.user_id=?""",
        (giveaway_id, user_id))
    if not row:
        return ""
    votes = await db.votes_for(giveaway_id, user_id)
    rank, total, _, highest = await db.rank_of(giveaway_id, user_id)
    handle = f"@{esc(row['username'])}" if row["username"] else esc(row["full_name"])
    line = await lines.get_line("card")
    plural = "" if votes == 1 else "s"
    fp = card_fingerprint(giveaway_id, user_id)
    theme = fp["theme"]
    rule = theme["rule"] * 12
    mark = theme["mark"]
    meter = unique_bar(votes, highest, theme["fill"], theme["empty"])

    if ended:
        footer = f"🚩 Closed · final <b>{votes}</b>"
    else:
        footer = f"⏳ <b>{until(row['ends_at'])}</b> left"

    if votes == 0 and highest == 0:
        chase = "🎯 First vote leads"
    elif votes >= highest:
        chase = "👑 <b>Leading</b>"
    else:
        gap = highest - votes
        chase = f"🚀 <b>{gap}</b> behind #1"

    name = esc(row["full_name"])
    gname = esc(row["giveaway_name"])
    brand = esc(config.BRAND)
    fl = flair(line)
    stats = (
        f"🏆 <b>{votes}</b> vote{plural}  ·  🎯 <b>#{rank or '-'}</b>/{total or 0}\n"
        f"{meter}  {pct_of_leader(votes, highest)}%"
    )

    hline = host_line()
    if fp["layout"] == 0:
        body = (
            f"{mark} <b>{brand}</b>  ·  {theme['code']}\n"
            f"<blockquote>{fl}</blockquote>\n"
            f"{mark}{rule}{mark}\n"
            f"👤 <b>{name}</b>\n"
            f"   {handle}\n"
            f"🎁 {gname}\n"
            f"\n{stats}\n{chase}\n"
            f"{mark}{rule}{mark}\n"
            f"{footer}\n"
            f"<code>{fp['id']}</code>  ·  seal {fp['seal']}\n"
            f"{hline}"
        )
    elif fp["layout"] == 1:
        body = (
            f"<b>{brand}</b>\n"
            f"{mark} card <code>{fp['id']}</code>  ·  {theme['code']}\n"
            f"<blockquote>{fl}</blockquote>\n"
            f"👑 <b>{name}</b>  ·  {handle}\n"
            f"💎 {gname}\n"
            f"\n{stats}\n"
            f"{chase}  ·  {footer}\n"
            f"{mark}{rule}{mark}\n"
            f"{hline}"
        )
    else:
        body = (
            f"{mark}{rule}{mark}\n"
            f"<b>{name}</b>\n"
            f"{handle}  ·  {gname}\n"
            f"{mark}{rule}{mark}\n"
            f"<blockquote>{fl}</blockquote>\n"
            f"{stats}\n"
            f"{chase}\n"
            f"{footer}\n"
            f"🪪 <code>{fp['id']}</code>  ·  {theme['code']}/{fp['seal']}\n"
            f"<i>{brand}</i>\n"
            f"{hline}"
        )
    return premiumize(body)


# ── results ─────────────────────────────────────────────────────────────────
async def results_text(giveaway, ranking) -> str:
    line = await lines.get_line("result")
    if not ranking:
        return R(
            "{e:flag} <b>{name}</b> closed\n\n{e:sleep} No entries — prize rolls over."
        ).format(name=esc(giveaway["name"]))

    highest = max(int(r["votes"]) for r in ranking)
    winners = [r for r in ranking if int(r["votes"]) == highest]
    medals = ["🥇", "🥈", "🥉"]
    top = []
    for i, r in enumerate(ranking[:5], 1):
        label = f"@{esc(r['username'])}" if r["username"] else esc(r["full_name"])
        medal = medals[i - 1] if i <= 3 else f"{i}."
        top.append(f"{medal} {label} · <b>{r['votes']}</b>")

    if highest == 0:
        winners, wtitle = [ranking[0]], "WINNER"
    else:
        wtitle = "WINNER" if len(winners) == 1 else "WINNERS"

    who = " & ".join(
        f"@{esc(w['username'])}" if w["username"]
        else f'<a href="tg://user?id={w["user_id"]}">{esc(w["full_name"])}</a>'
        for w in winners)

    claim = await db.claim_handle()
    return R(
        "{e:star_gold} <b>{brand} — RESULT</b>\n"
        "<blockquote>{line}</blockquote>\n"
        "\n"
        "{e:gift} <b>{name}</b> · {prize}\n"
        "\n"
        "{e:trophy} <b>{wtitle}</b> — {who}\n"
        "\n"
        "{top}\n"
        "\n"
        "{e:pushpin} Winner: Contact <b>{claim}</b> to claim\n"
        "{host_line}"
    ).format(
        brand=esc(config.BRAND),
        line=flair(line),
        name=esc(giveaway["name"]),
        prize=esc(giveaway["prize"] or "Surprise drop"),
        wtitle=wtitle,
        who=who,
        top="\n".join(top),
        claim=esc(claim),
        host_line=host_line(),
    )


# ── direct messages ─────────────────────────────────────────────────────────
async def joined_text(name: str, giveaway: str) -> str:
    """The single confirmation shown *in place* of the joined message."""
    return R(
        "{e:check} <b>You're in · {giveaway}</b>\n"
        "{e:pushpin} Card live in {channel}\n"
        "{e:bolt} Cards don't win by sitting still — <b>share it</b>"
    ).format(giveaway=esc(giveaway), name=esc(name), channel=esc(config.GIVEAWAY_CHANNEL_USERNAME))


# Short motivational pushes, picked to fit the size of the gap.
CHASE_LINES = [
    "The gap is <b>{gap}</b> — that is {gap} people who simply haven't heard from you yet.",
    "You didn't enter to sit at <b>#{rank}</b>. Send the card.",
    "One share is one vote. One vote closes a gap.",
    "Leaders get comfortable. That's how they lose.",
    "Your card is doing nothing in the channel. Move it.",
    "Momentum is one message away — post it now.",
    "Somebody just took your spot. Take it back.",
    "The leader sleeps too. Share while they do.",
]


async def overtaken_text(name: str, by: str, giveaway: str, rank: int, gap: int) -> str:
    """Motivational nudge: someone passed you — here's how to get it back."""
    line = CHASE_LINES[(rank + gap) % len(CHASE_LINES)].format(gap=gap, rank=rank)
    drink = "vote" if gap == 1 else "votes"
    return R(
        "{e:fire} <b>{name}, you just got chased down</b>\n"
        "<blockquote>{by} passed you — you're <b>#{rank}</b>, {gap} {drink} behind</blockquote>\n"
        "\n"
        "{e:bolt} {line}\n"
        "\n"
        "{e:share} <b>Share your card</b> — one tap, your people vote, you jump back up."
    ).format(name=esc(name), by=esc(by), rank=rank, gap=gap, drink=drink, line=line)


async def ended_dm(giveaway, winner_label: str, winner_votes: int, my_rank: int,
                   my_votes: int, total: int) -> str:
    line = await lines.get_line("result")
    return R(
        "{e:flag} <b>{name}</b> ended\n"
        "<blockquote>{line}</blockquote>\n"
        "\n"
        "{e:trophy} <b>{winner}</b> · {wv} vote{v}\n"
        "{e:chart} You: <b>#{rank}</b>/{total} · {mv} vote{mv_s}"
    ).format(name=esc(giveaway["name"]), line=flair(line), winner=winner_label,
             wv=winner_votes, v="" if winner_votes == 1 else "s",
             rank=my_rank or "-", total=total, mv=my_votes,
             mv_s="" if my_votes == 1 else "s")


async def winner_dm(giveaway, who: str, my_votes: int) -> str:
    line = await lines.get_line("result")
    claim = await db.claim_handle()
    return R(
        "{e:trophy} <b>YOU WON, {who}</b>\n"
        "<blockquote>{line}</blockquote>\n"
        "\n"
        "{e:gift} <b>{name}</b>\n"
        "{e:gem} {prize}\n"
        "\n"
        "{e:pushpin} Contact <b>{claim}</b> to claim\n"
        "{host_line}"
    ).format(who=esc(who), line=flair(line), name=esc(giveaway["name"]),
             prize=esc(giveaway["prize"] or "Surprise drop"), claim=esc(claim),
             host_line=host_line())


# ── admin ───────────────────────────────────────────────────────────────────
async def admin_panel() -> str:
    s = await db.overall_stats()
    return R(
        "{e:owner_tag} <b>{brand} — Control room</b>\n"
        "{host_line}\n"
        "\n"
        "{e:gift} <b>{g}</b> total · {e:fire} <b>{a}</b> live · {e:flag} <b>{f}</b> done\n"
        "{e:users} <b>{u}</b> verified · {e:ballot} <b>{v}</b> votes\n"
        "{e:channel} Giveaways: {gch} · {e:group} Group: {grp}"
    ).format(
        brand=esc(config.BRAND),
        host_line=host_line(),
        g=s["giveaways"], a=s["active"], f=s["finished"],
        u=s["users"], v=s["votes"],
        gch=esc(config.GIVEAWAY_CHANNEL_USERNAME),
        grp=esc(config.GROUP_USERNAME),
    )


def giveaway_admin(row, link: str) -> str:
    state = R("{e:fire} Active") if row["status"] == "active" else R("{e:flag} Done")
    return R(
        "{e:gift} <b>{name}</b> · {state}\n"
        "{e:pushpin} <code>#{id}</code> · {e:users} <b>{p}</b> · {e:ballot} <b>{v}</b>\n"
        "{e:hourglass} {ends} ({left})\n"
        "{e:link} <code>{link}</code>"
    ).format(name=esc(row["name"]), state=state, id=row["id"], p=row["participants"],
             v=row["votes"], ends=fmt_dt(row["ends_at"]), left=until(row["ends_at"]),
             link=esc(link))


def gate_panel_text(rows) -> str:
    extra = "\n".join(
        R("{e:channel} <b>{title}</b>").format(title=esc(r["title"] or r["username"] or "chat"))
        for r in rows) or "<i>no extra channels/groups</i>"
    return R(
        "{e:channel} <b>Required channels & group</b>\n"
        "\n"
        "{e:check_plain} <b>{main_title}</b> ({main_ch}) <i>(main channel · always)</i>\n"
        "{e:check_plain} <b>{gch}</b> <i>(giveaway channel · always)</i>\n"
        "{e:check_plain} <b>{grp}</b> <i>(community group · always)</i>\n"
        "{extra}\n"
        "\n"
        "{e:shield} Bot must be <b>admin</b> in each chat."
    ).format(
        main_title=esc(config.MAIN_CHANNEL_TITLE),
        main_ch=esc(config.MAIN_CHANNEL_USERNAME),
        gch=esc(config.GIVEAWAY_CHANNEL_USERNAME),
        grp=esc(config.GROUP_USERNAME),
        extra=extra,
    )


async def gate_add_prompt(me: str) -> str:
    return R(
        "{e:plus} <b>Add required channel or group</b>\n"
        "\n"
        "Send <code>@username</code>, a t.me link, a chat id,\n"
        "or forward a message from it.\n"
        "\n"
        "{e:warning} Add <b>@{me}</b> as admin there first."
    ).format(me=esc(me))


# ── admin: broadcast + emoji index ──────────────────────────────────────────
async def broadcast_prompt() -> str:
    return R(
        "{e:megaphone} <b>Broadcast</b>\n"
        "\n"
        "Text, <b>photo</b> or <b>video</b> — caption works.\n"
        "\n"
        "{e:sparkle} Emoji you type → <b>premium emoji</b>\n"
        "❝ \"quoted text\" → styled quote block\n"
        "{e:pushpin} A premium emoji you paste stays premium"
    )


async def broadcast_preview(body: str, recipients: int) -> str:
    return R(
        "{e:megaphone} <b>Preview</b>\n"
        "━━━━━━━━━━━━━━━\n"
        "{body}\n"
        "━━━━━━━━━━━━━━━\n"
        "\n"
        "{e:users} <b>{n}</b> verified members will get this"
    ).format(body=body, n=recipients)


async def broadcast_done(sent: int, failed: int, note_: str = "") -> str:
    extra = R("\n{e:channel} {note}").format(note=esc(note_)) if note_ else ""
    return R(
        "{e:check} <b>Broadcast sent</b>\n"
        "\n"
        "{e:users} Delivered <b>{s}</b> · {e:cross} Failed <b>{f}</b>{extra}"
    ).format(s=sent, f=failed, extra=extra)


def emoji_index_text(page: int = 0, per_page: int = 20) -> tuple[str, int]:
    """Conversion table: normal emoji -> the premium emoji it becomes."""
    items = catalogue()
    pages = max(1, (len(items) + per_page - 1) // per_page)
    page = max(0, min(page, pages - 1))
    chunk = items[page * per_page:(page + 1) * per_page]
    lines = []
    for fallback, cid, names in chunk:
        premium_tag = f'<tg-emoji emoji-id="{cid}">{fallback}</tg-emoji>'
        lines.append(f"<code>{fallback}</code> ➜ {premium_tag}  <i>{names[0]}</i>")
    text = R(
        "{e:sparkle} <b>Normal emoji ➜ Premium emoji</b>\n"
        "<i>Left = what you type · right = premium sticker that gets sent.\n"
        "Copy a left emoji, paste it in a broadcast — it converts itself.</i>\n"
        "\n"
        + "\n".join(lines) +
        "\n\n"
        "{e:chart} page {p}/{pages} · {total} conversions"
    ).format(p=page + 1, pages=pages, total=len(items))
    return text, pages


async def vote_admin_list_intro() -> str:
    return R("{e:vote} <b>Manage votes</b>\n\nPick a giveaway.")


async def vote_participants_intro(giveaway) -> str:
    return R("{e:vote} <b>{name}</b>\n\nPick a card.").format(name=esc(giveaway["name"]))


def vote_edit_text(participant, giveaway, count: int, real: int) -> str:
    adjust = count - real
    sign = f"{adjust:+d}" if adjust else "0"
    return R(
        "{e:crown} <b>{who}</b>\n"
        "{e:ballot} Total <b>{count}</b> · {e:users} real <b>{real}</b> · {e:plus} adj <b>{sign}</b>"
    ).format(who=esc(participant["full_name"]), count=count, real=real, sign=sign)

cards = types.SimpleNamespace(
    R=R,
    API_TAG=API_TAG,
    host_line=host_line,
    esc=esc,
    flair=flair,
    fmt_dt=fmt_dt,
    until=until,
    bar=bar,
    pct_of_leader=pct_of_leader,
    gate_text=gate_text,
    verify_failed=verify_failed,
    welcome=welcome,
    how_it_works=how_it_works,
    giveaway_card=giveaway_card,
    participant_caption=participant_caption,
    results_text=results_text,
    joined_text=joined_text,
    CHASE_LINES=CHASE_LINES,
    overtaken_text=overtaken_text,
    ended_dm=ended_dm,
    winner_dm=winner_dm,
    admin_panel=admin_panel,
    giveaway_admin=giveaway_admin,
    gate_panel_text=gate_panel_text,
    gate_add_prompt=gate_add_prompt,
    broadcast_prompt=broadcast_prompt,
    broadcast_preview=broadcast_preview,
    broadcast_done=broadcast_done,
    emoji_index_text=emoji_index_text,
    vote_admin_list_intro=vote_admin_list_intro,
    vote_participants_intro=vote_participants_intro,
    vote_edit_text=vote_edit_text,
)


# ══════════════════════════════════════════════════════════════════
#  KEYBOARDS
# ══════════════════════════════════════════════════════════════════
"""Keyboards with native premium-emoji button icons (Bot API 9.4) + colours."""
from urllib.parse import quote

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup



_BTN_FIELDS = getattr(InlineKeyboardButton, "model_fields", None)


def btn(text, *, cb=None, url=None, ic=None, style=None) -> InlineKeyboardButton:
    """Inline button with optional custom-emoji icon (Bot API 9.4+) and colour style."""
    kw = {"text": text}
    if cb is not None:
        kw["callback_data"] = cb
    if url is not None:
        kw["url"] = url
    emoji_id = icon(ic) if ic else None
    if emoji_id and (_BTN_FIELDS is None or "icon_custom_emoji_id" in _BTN_FIELDS):
        kw["icon_custom_emoji_id"] = emoji_id
    if style and (_BTN_FIELDS is None or "style" in _BTN_FIELDS):
        kw["style"] = style
    try:
        return InlineKeyboardButton(**kw)
    except Exception:
        kw.pop("icon_custom_emoji_id", None)
        kw.pop("style", None)
        return InlineKeyboardButton(**kw)


# ── Telegram share dialog ───────────────────────────────────────────────────
def share_href(url: str, text: str = "") -> str:
    """Native Telegram share sheet for a link + message."""
    href = "https://t.me/share/url?url=" + quote(url or "", safe="")
    if text:
        href += "&text=" + quote(text, safe="")
    return href


def share_btn(label: str, url: str, text: str = "", ic: str = "share",
              style: str = "success") -> InlineKeyboardButton:
    return btn(label, url=share_href(url, text), ic=ic, style=style)


# ── gates ───────────────────────────────────────────────────────────────────
def join_gate(missing, giveaway_id: int | None = None,
             participant_id: int | None = None) -> InlineKeyboardMarkup:
    """One Join button per channel/group the member is still missing, then Verify."""
    gid = giveaway_id or 0
    pid = participant_id or 0
    verify_cb = f"verify:{gid}:{pid}"
    rows = [
        [btn(
            f"Join {g.get('btn_title') or g['title']}",
            url=g["url"],
            ic="group" if g.get("kind") == "group" else "channel",
            style="primary",
        )]
        for g in (missing or [])
    ]
    rows.append([btn("Verify membership", cb=verify_cb, ic="verify", style="success")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── user menu (trimmed: no live / winners / random-line buttons) ────────────
def main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
    """No repeated 'Join channel' button — the gate already handles that."""
    rows = [
        [btn("How it works", cb="menu:help", ic="info", style="primary")],
    ]
    if is_admin:
        rows.append([btn("Admin panel", cb="admin:home", ic="admin", style="success")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def participate(giveaway_id: int, share_target: str = "", share_text: str = "") -> InlineKeyboardMarkup:
    """Enter + native Share (no raw link in the message text)."""
    rows = [[btn("Enter this giveaway", cb=f"enter:{giveaway_id}", ic="gift", style="success")]]
    if share_target:
        rows.append([share_btn("Share giveaway", share_target, share_text, style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def vote_kb(giveaway_id: int, participant_id: int, count: int,
            card_url: str = "", share_text: str = "",
            extra_url: str = "") -> InlineKeyboardMarkup:
    """Vote on a card + share that card (every entrant may share their own card)."""
    rows = [[btn(f"Vote • {count}", url=vote_start_link(giveaway_id, participant_id),
                 ic="vote", style="primary")]]
    if card_url:
        rows[0].append(share_btn("Share card", card_url, share_text, style="success"))
    rows.append([btn("Join giveaway", url=start_link(giveaway_id), ic="gift", style="success")])
    if extra_url:
        rows.append([btn(config.EXTRA_BTN_LABEL, url=extra_url, ic="link", style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def share_my_card(card_url: str, share_text: str) -> InlineKeyboardMarkup:
    """DM keyboard after entering — the entrant's own share button."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [share_btn("Share my card", card_url, share_text, style="success")],
    ])


def joined_kb(card_url: str, share_text: str) -> InlineKeyboardMarkup:
    """Compact keyboard used when the join confirmation replaces a message."""
    return share_my_card(card_url, share_text)


def overtaken_kb(card_url: str, share_text: str) -> InlineKeyboardMarkup:
    return share_my_card(card_url, share_text)


def winner_claim(claim_handle: str | None = None,
                 claim_url: str | None = None) -> InlineKeyboardMarkup:
    handle = claim_handle or config.CLAIM_HANDLE
    url = claim_url or config.CLAIM_URL
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn(f"Contact {handle} to claim", url=url,
             ic="trophy", style="success")],
    ])


# ── admin: giveaway creation ────────────────────────────────────────────────
def duration_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("1 day", cb="duration:1d", style="primary"),
         btn("2 days", cb="duration:2d", style="primary"),
         btn("3 days", cb="duration:3d", style="primary")],
        [btn("5 days", cb="duration:5d", style="primary"),
         btn("7 days", cb="duration:7d", style="primary")],
        [btn("Cancel", cb="admin:cancel", ic="skip", style="danger")],
    ])


def photo_step() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Skip — no media", cb="photo:skip", ic="skip", style="danger")],
    ])


def admin_home_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("New giveaway", cb="admin:create", ic="gift", style="success")],
        [btn("Active", cb="admin:list:active", ic="fire", style="primary"),
         btn("Finished", cb="admin:list:finished", ic="flag", style="primary")],
        [btn("Manage votes", cb="admin:votelist", ic="vote", style="primary"),
         btn("Statistics", cb="admin:stats", ic="stats", style="primary")],
        [btn("Broadcast", cb="admin:bc", ic="megaphone", style="success"),
         btn("Emojis", cb="admin:emoji:0", ic="sparkle", style="primary")],
        [btn("Required chats", cb="admin:gates", ic="channel", style="primary"),
         btn("Extra card link", cb="admin:cheap", ic="link", style="primary")],
        [btn("Admins", cb="admin:admins", ic="admin", style="primary")],
        [btn("Setup", cb="admin:help", ic="info", style="primary")],
    ])


def broadcast_confirm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Send to members", cb="bc:send", ic="users", style="success")],
        [btn("Members + channel", cb="bc:sendall", ic="channel", style="primary")],
        [btn("Cancel", cb="admin:cancel", ic="skip", style="danger")],
    ])


def emoji_index_kb(page: int, pages: int) -> InlineKeyboardMarkup:
    rows = []
    nav = []
    if page > 0:
        nav.append(btn("Prev", cb=f"admin:emoji:{page - 1}", ic="back", style="primary"))
    if page < pages - 1:
        nav.append(btn("Next", cb=f"admin:emoji:{page + 1}", ic="link", style="primary"))
    if nav:
        rows.append(nav)
    rows.append([btn("Broadcast", cb="admin:bc", ic="megaphone", style="success")])
    rows.append([btn("Admin panel", cb="admin:home", ic="back", style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_home() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Admin panel", cb="admin:home", ic="back", style="primary")]])


def cancel_only() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Cancel", cb="admin:cancel", ic="skip", style="danger")]])


def giveaway_actions(giveaway_id: int, status: str, link: str,
                     share_text: str = "") -> InlineKeyboardMarkup:
    rows = [
        [btn("Participation link", url=link, ic="link", style="primary"),
         share_btn("Share", link, share_text, style="success")],
    ]
    if status == "active":
        rows.append([
            btn("End + publish", cb=f"admin:endask:{giveaway_id}", ic="end", style="danger"),
            btn("Refresh cards", cb=f"admin:refresh:{giveaway_id}", ic="refresh", style="primary"),
        ])
    rows.append([
        btn("Export entries", cb=f"admin:export:{giveaway_id}", ic="export", style="primary"),
        btn("Delete", cb=f"admin:delask:{giveaway_id}", ic="delete", style="danger"),
    ])
    rows.append([btn("Admin panel", cb="admin:home", ic="back", style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_end(giveaway_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Yes, end & publish results", cb=f"admin:end:{giveaway_id}", ic="end", style="danger")],
        [btn("Go back", cb=f"admin:view:{giveaway_id}", ic="back", style="primary")],
    ])


def confirm_delete(giveaway_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Yes, delete for good", cb=f"admin:del:{giveaway_id}", ic="delete", style="danger")],
        [btn("Go back", cb=f"admin:view:{giveaway_id}", ic="back", style="primary")],
    ])


# ── admin: force-join channels ──────────────────────────────────────────────
def gate_panel(rows) -> InlineKeyboardMarkup:
    kb = [[btn("Add channel / group", cb="admin:gateadd", ic="plus", style="success")]]
    for r in rows:
        label = (r["title"] or r["username"] or str(r["chat_id"]))[:26]
        kb.append([btn(f"Remove {label}", cb=f"admin:gatedel:{r['id']}",
                       ic="minus", style="danger")])
    kb.append([btn("Admin panel", cb="admin:home", ic="back", style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def admins_panel_kb(rows) -> InlineKeyboardMarkup:
    kb = [[btn("Add admin", cb="admin:addadmin", ic="plus", style="success")]]
    for r in rows:
        kb.append([btn(f"Remove {r['user_id']}", cb=f"admin:rmadmin:{r['user_id']}",
                       ic="minus", style="danger")])
    kb.append([btn("Admin panel", cb="admin:home", ic="back", style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


# ── admin: vote management ──────────────────────────────────────────────────
def vote_giveaway_list(rows) -> InlineKeyboardMarkup:
    kb = [[btn(f"#{r['id']} · {r['name'][:26]} ({r['votes']} votes)",
               cb=f"admin:voters:{r['id']}", ic="gift", style="primary")] for r in rows]
    kb.append([btn("Admin panel", cb="admin:home", ic="back", style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def vote_participants(giveaway_id: int, rows, page: int = 0, per_page: int = 8) -> InlineKeyboardMarkup:
    start = page * per_page
    chunk = rows[start:start + per_page]
    kb = []
    for r in chunk:
        label = (f"@{r['username']}" if r["username"] else r["full_name"])[:24]
        kb.append([btn(f"{label} — {r['votes']} votes",
                       cb=f"admin:votes:{giveaway_id}:{r['user_id']}", ic="vote", style="primary")])
    nav = []
    if page > 0:
        nav.append(btn("Prev", cb=f"admin:voters:{giveaway_id}:{page - 1}", ic="back", style="primary"))
    if start + per_page < len(rows):
        nav.append(btn("Next", cb=f"admin:voters:{giveaway_id}:{page + 1}", ic="link", style="primary"))
    if nav:
        kb.append(nav)
    kb.append([btn("Admin panel", cb="admin:home", ic="back", style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def vote_edit(giveaway_id: int, participant_id: int, count: int, real: int) -> InlineKeyboardMarkup:
    """One-tap vote deltas — including bulk +10 / +20."""
    def delta(n: int) -> InlineKeyboardButton:
        return btn(f"{n:+d}", cb=f"admin:vote:{giveaway_id}:{participant_id}:{n}",
                   style="success" if n > 0 else "danger")

    return InlineKeyboardMarkup(inline_keyboard=[
        [delta(1), delta(5), delta(10), delta(20)],
        [delta(-1), delta(-5), delta(-10), delta(-20)],
        [btn(f"Reset to 0  ·  real {real}", cb=f"admin:vote:{giveaway_id}:{participant_id}:0",
             ic="refresh", style="primary")],
        [btn("Back to list", cb=f"admin:voters:{giveaway_id}", ic="back", style="primary")],
    ])

kb = types.SimpleNamespace(
    btn=btn,
    share_href=share_href,
    share_btn=share_btn,
    join_gate=join_gate,
    main_menu=main_menu,
    participate=participate,
    vote_kb=vote_kb,
    share_my_card=share_my_card,
    joined_kb=joined_kb,
    overtaken_kb=overtaken_kb,
    winner_claim=winner_claim,
    duration_kb=duration_kb,
    photo_step=photo_step,
    admin_home_kb=admin_home_kb,
    broadcast_confirm=broadcast_confirm,
    emoji_index_kb=emoji_index_kb,
    back_home=back_home,
    cancel_only=cancel_only,
    giveaway_actions=giveaway_actions,
    confirm_end=confirm_end,
    confirm_delete=confirm_delete,
    gate_panel=gate_panel,
    admins_panel_kb=admins_panel_kb,
    vote_giveaway_list=vote_giveaway_list,
    vote_participants=vote_participants,
    vote_edit=vote_edit,
    admin_home=admin_home_kb,
    admins_panel=admins_panel_kb,
    emoji_index=emoji_index_kb,
)


# ══════════════════════════════════════════════════════════════════
#  BOT
# ══════════════════════════════════════════════════════════════════
"""NEXT GEN GIVEAWAYS — premium voting giveaway bot (aiogram 3).
Hosted by TG MANDI (@tgmandi).

Flows:
  /start            -> force-join gate (@tgmandi + @tgmandGiveaway + @tgmandichats) -> Verify -> menu
  giveaway launch   -> posted in @tgmandGiveaway AND broadcast to every verified user
  entering          -> card posted in @tgmandGiveaway with the member's photo
  voting            -> verified members only, one vote each, votes can move but never duplicate
  admin             -> create (title/prize/photo/duration), manage votes, end, export
"""
import array
import asyncio
import csv
import html
import io
import logging
import random
import re
import secrets
import time
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BotCommand,
    CallbackQuery,
    ChatMemberUpdated,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    Message,
)


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger("nextgen")

router = Router()
bot_username = ""
NO_PREVIEW = LinkPreviewOptions(is_disabled=True)
BROADCAST_DELAY = 0.045          # ~22 msg/s, under Telegram's 30 msg/s limit


# ── helpers ─────────────────────────────────────────────────────────────────
def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)


def full_name(user) -> str:
    parts = [getattr(user, "first_name", None), getattr(user, "last_name", None)]
    return " ".join(p for p in parts if p).strip() or "Telegram User"


def start_link(giveaway_id: int) -> str:
    return f"https://t.me/{bot_username}?start=g_{giveaway_id}"


def vote_start_link(giveaway_id: int, participant_id: int) -> str:
    return f"https://t.me/{bot_username}?start=v_{giveaway_id}_{participant_id}"


def channel_post_link(message_id) -> str:
    """Public link to a post inside the giveaway channel (@tgmandGiveaway)."""
    if not message_id:
        return ""
    uname = config.GIVEAWAY_CHANNEL_USERNAME.lstrip("@")
    if not uname:
        return ""
    return f"https://t.me/{uname}/{message_id}"


def giveaway_share_target(row) -> str:
    try:
        msg_id = row["channel_msg_id"]
    except (KeyError, IndexError):
        msg_id = 0
    return channel_post_link(msg_id) or start_link(row["id"])


def giveaway_share_text(name: str) -> str:
    return f"{config.BRAND} · {name} — enter now, collect votes, win the prize"


def card_share_text(name: str) -> str:
    return f"Vote for my card in {name} — {config.BRAND}"


def _esc_plain(value: str) -> str:
    """Escape HTML but keep quotes, so "…" can become a blockquote later."""
    return html.escape(value or "", quote=False)


def _units(text: str) -> "array.array":
    """Text as UTF-16 code units — the unit Telegram counts entity offsets in."""
    return array.array("H", text.encode("utf-16-le"))


def _from_units(chunk) -> str:
    return chunk.tobytes().decode("utf-16-le", errors="replace")


def _u16_slice(text: str, offset: int, length: int) -> str:
    return _from_units(_units(text)[offset:offset + length])


def _safe_href(value: str) -> str:
    """Telegram rejects scheme-less hrefs — but auto-links them as text."""
    low = value.lower()
    if low.startswith(("http://", "https://", "tg://")):
        return value
    return "https://" + value.lstrip("/")


_TAG_SPLIT = re.compile(r"(<[^>]+>)")
_QUOTE_RE = re.compile(r'["\u201c]([^"\n\u201d]{1,300})["\u201d]')
_HTML_TAGS = {
    "bold": ("<b>", "</b>"), "italic": ("<i>", "</i>"), "underline": ("<u>", "</u>"),
    "strikethrough": ("<s>", "</s>"), "code": ("<code>", "</code>"), "pre": ("<pre>", "</pre>"),
    "spoiler": ("<tg-spoiler>", "</tg-spoiler>"), "blockquote": ("<blockquote>", "</blockquote>"),
}


def quoteize(html_text: str) -> str:
    """Anything wrapped in "quotes" becomes a Telegram blockquote."""
    parts = _TAG_SPLIT.split(html_text)
    for i, part in enumerate(parts):
        if part.startswith("<") and part.endswith(">"):
            continue
        parts[i] = _QUOTE_RE.sub(lambda m: f"<blockquote>{m.group(1)}</blockquote>", part)
    return "".join(parts)


def message_to_html(message: Message) -> str:
    """Rebuild an admin message as HTML — keeps premium emoji and formatting.

    Entity offsets are UTF-16 code units, so all slicing happens on a UTF-16
    unit array. Slicing the Python string directly shifts every entity that
    comes after an emoji and duplicates characters (broken links).
    """
    text = message.text or message.caption or ""
    units = _units(text)
    entities = sorted(message.entities or message.caption_entities or [],
                      key=lambda e: (e.offset, -e.length))
    if not entities:
        return _esc_plain(text)

    out, pos = [], 0
    for ent in entities:
        if ent.offset < pos:                       # overlapping / nested entity
            continue
        out.append(_esc_plain(_from_units(units[pos:ent.offset])))
        seg = _esc_plain(_from_units(units[ent.offset:ent.offset + ent.length]))
        kind = str(ent.type)
        if kind == "custom_emoji":
            out.append(f'<tg-emoji emoji-id="{ent.custom_emoji_id}">{seg}</tg-emoji>')
        elif kind in _HTML_TAGS:
            open_tag, close_tag = _HTML_TAGS[kind]
            out.append(f"{open_tag}{seg}{close_tag}")
        elif kind == "text_link":
            out.append(f'<a href="{ent.url}">{seg}</a>')
        elif kind == "url":
            out.append(f'<a href="{_safe_href(_from_units(units[ent.offset:ent.offset + ent.length]))}">{seg}</a>')
        else:
            out.append(seg)
        pos = ent.offset + ent.length
    out.append(_esc_plain(_from_units(units[pos:])))
    return "".join(out)


def compose_body(message: Message) -> str:
    """Full broadcast pipeline: entities → quotes → premium emoji → {e:token}."""
    body = message_to_html(message)
    body = quoteize(body)
    body = premium.premiumize(body)
    try:
        body = premium.render(body)               # {e:crown} style tokens
    except KeyError as exc:
        raise ValueError(f"unknown emoji token {exc}") from None
    return body


def parse_duration(value: str):
    m = re.fullmatch(r"\s*(\d+)\s*([mhdw])\s*", (value or "").lower())
    if not m:
        return None
    n, unit = int(m.group(1)), m.group(2)
    delta = {"m": timedelta(minutes=n), "h": timedelta(hours=n),
             "d": timedelta(days=n), "w": timedelta(weeks=n)}[unit]
    if delta < timedelta(minutes=5) or delta > timedelta(days=365):
        return None
    return delta


async def required_gates() -> list[dict]:
    """Core 3 force-join gates (2 channels + 1 group), then any admin-added chats."""
    gates = [
        {
            "key": "main_channel",
            "target": config.MAIN_CHANNEL_ID or config.MAIN_CHANNEL_USERNAME,
            "chat_id": config.MAIN_CHANNEL_ID,
            "username": config.MAIN_CHANNEL_USERNAME,
            "title": f"{config.MAIN_CHANNEL_TITLE} ({config.MAIN_CHANNEL_USERNAME})",
            "btn_title": config.MAIN_CHANNEL_TITLE,
            "url": config.MAIN_CHANNEL_URL,
            "kind": "channel",
            "role": "Main Channel",
        },
        {
            "key": "giveaway_channel",
            "target": config.GIVEAWAY_CHANNEL_ID or config.GIVEAWAY_CHANNEL_USERNAME,
            "chat_id": config.GIVEAWAY_CHANNEL_ID,
            "username": config.GIVEAWAY_CHANNEL_USERNAME,
            "title": config.GIVEAWAY_CHANNEL_USERNAME,
            "btn_title": config.GIVEAWAY_CHANNEL_USERNAME,
            "url": config.GIVEAWAY_CHANNEL_URL,
            "kind": "channel",
            "role": "Giveaway Channel",
        },
        {
            "key": "main_group",
            "target": config.GROUP_ID or config.GROUP_USERNAME,
            "chat_id": config.GROUP_ID,
            "username": config.GROUP_USERNAME,
            "title": config.GROUP_USERNAME,
            "btn_title": config.GROUP_USERNAME,
            "url": config.GROUP_URL,
            "kind": "group",
            "role": "Community Group",
        },
    ]
    for row in await db.list_gate_channels():
        url = row["invite_link"] or (f"https://t.me/{row['username'].lstrip('@')}"
                                     if row["username"] else "")
        if not url:
            continue
        label = row["title"] or row["username"] or str(row["chat_id"])
        gates.append({
            "key": f"extra_{row['id']}",
            "target": row["chat_id"] or row["username"],
            "chat_id": row["chat_id"] or 0,
            "username": row["username"] or "",
            "title": label,
            "btn_title": label,
            "url": url,
            "kind": "channel",
            "role": "",
        })
    return gates


async def is_member_of(bot: Bot, gate, user_id: int) -> bool:
    targets = []
    if isinstance(gate, dict):
        if gate.get("chat_id"):
            targets.append(gate["chat_id"])
        if gate.get("username"):
            uname = "@" + gate["username"].lstrip("@")
            if uname not in targets:
                targets.append(uname)
        if gate.get("target") and gate["target"] not in targets:
            targets.append(gate["target"])
    else:
        targets.append(gate)

    for target in targets:
        try:
            member = await bot.get_chat_member(target, user_id)
            if member.status in {ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR,
                                 ChatMemberStatus.MEMBER}:
                return True
            return (member.status == ChatMemberStatus.RESTRICTED
                    and bool(getattr(member, "is_member", False)))
        except Exception as exc:                      # noqa: BLE001
            log.warning("membership check failed for %s in %s: %s", user_id, target, exc)
            continue
    return False


async def gate_state(bot: Bot, user_id: int):
    """-> (all gates, joined keys, missing gates)."""
    gates = await required_gates()
    joined, missing = [], []
    for gate in gates:
        if await is_member_of(bot, gate, user_id):
            joined.append(gate["key"])
        else:
            missing.append(gate)
    return gates, joined, missing


async def is_channel_member(bot: Bot, user_id: int) -> bool:
    """True only when the member has joined every required channel."""
    return not (await gate_state(bot, user_id))[2]


async def remember_user(user) -> None:
    await db.upsert_user(user.id, full_name(user), user.username, iso(utcnow()))


# ── channel cards ───────────────────────────────────────────────────────────
async def refresh_card(bot: Bot, giveaway_id: int, user_id: int, ended: bool = False) -> None:
    row = await db.get_participant(giveaway_id, user_id)
    if not row or not row["message_id"]:
        return
    caption = await cards.participant_caption(giveaway_id, user_id, ended=ended)
    count = await db.votes_for(giveaway_id, user_id)
    giveaway = await db.get_giveaway(giveaway_id)
    markup = None
    if not ended:
        markup = kb.vote_kb(giveaway_id, user_id, count,
                            channel_post_link(row["message_id"]),
                            card_share_text(giveaway["name"] if giveaway else ""),
                            extra_url=await db.cheap_api_url())
    try:
        if row["message_kind"] == "photo":
            await bot.edit_message_caption(
                chat_id=config.GIVEAWAY_CHANNEL_TARGET, message_id=row["message_id"],
                caption=caption, reply_markup=markup, parse_mode=ParseMode.HTML)
        else:
            await bot.edit_message_text(
                chat_id=config.GIVEAWAY_CHANNEL_TARGET, message_id=row["message_id"],
                text=caption, reply_markup=markup, parse_mode=ParseMode.HTML,
                link_preview_options=NO_PREVIEW)
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(exc).lower():
            log.warning("card refresh failed (%s/%s): %s", giveaway_id, user_id, exc)
    except Exception as exc:                      # noqa: BLE001
        log.warning("card refresh error: %s", exc)


async def post_card(bot: Bot, user, giveaway_id: int):
    """Post the entrant's card in the channel, then wire up its Share button."""
    caption = await cards.participant_caption(giveaway_id, user.id)
    markup = kb.vote_kb(giveaway_id, user.id, 0, extra_url=await db.cheap_api_url())
    sent, kind = None, "text"
    try:
        photos = await bot.get_user_profile_photos(user.id, limit=1)
        if photos.total_count and photos.photos:
            sent = await bot.send_photo(
                config.GIVEAWAY_CHANNEL_TARGET, photos.photos[0][-1].file_id, caption=caption,
                reply_markup=markup, parse_mode=ParseMode.HTML)
            kind = "photo"
    except Exception as exc:                      # noqa: BLE001
        log.info("no profile photo for %s: %s", user.id, exc)
    if sent is None:
        sent = await bot.send_message(config.GIVEAWAY_CHANNEL_TARGET, caption, reply_markup=markup,
                                      parse_mode=ParseMode.HTML, link_preview_options=NO_PREVIEW)
    await db.set_participant_post(giveaway_id, user.id, sent.message_id, kind)
    await refresh_card(bot, giveaway_id, user.id)   # adds "Share card"


async def send_giveaway_card(bot: Bot, chat_id: int, giveaway_id: int,
                             markup=None):
    """Sends the giveaway card; returns the sent Message (or None)."""
    row = await db.giveaway_stats_row(giveaway_id)
    if not row:
        return None
    caption = await cards.giveaway_card(row, compact=bool(row["photo"]))
    markup = markup if markup is not None else kb.participate(
        giveaway_id, giveaway_share_target(row), giveaway_share_text(row["name"]))
    if row["photo"]:
        kind = row["media_kind"] if "media_kind" in row.keys() else "photo"
        if kind == "video":
            return await bot.send_video(chat_id, row["photo"], caption=caption,
                                        reply_markup=markup, parse_mode=ParseMode.HTML)
        return await bot.send_photo(chat_id, row["photo"], caption=caption, reply_markup=markup,
                                    parse_mode=ParseMode.HTML)
    return await bot.send_message(chat_id, await cards.giveaway_card(row), reply_markup=markup,
                                  parse_mode=ParseMode.HTML, link_preview_options=NO_PREVIEW)


# ── registration / voting ───────────────────────────────────────────────────
async def register(bot: Bot, user, giveaway_id: int) -> tuple[bool, str]:
    giveaway = await db.get_giveaway(giveaway_id)
    if not giveaway:
        return False, "MISSING"
    if giveaway["status"] != "active" or parse_iso(giveaway["ends_at"]) <= utcnow():
        return False, "ENDED"
    if not await is_channel_member(bot, user.id):
        return False, "JOIN_REQUIRED"
    if await db.get_participant(giveaway_id, user.id):
        return True, "ALREADY"
    await db.add_participant(giveaway_id, user.id, full_name(user), user.username, iso(utcnow()))
    await post_card(bot, user, giveaway_id)
    return True, "OK"


async def joined_view(user, giveaway_id: int):
    """The one compact 'joined' state, reused by every entry path."""
    giveaway = await db.get_giveaway(giveaway_id)
    row = await db.get_participant(giveaway_id, user.id)
    if not giveaway or not row:
        return None, None
    card_url = channel_post_link(row["message_id"])
    text = await cards.joined_text(user.first_name or "friend", giveaway["name"])
    markup = (kb.joined_kb(card_url, card_share_text(giveaway["name"]))
              if card_url else kb.main_menu(await db.is_admin(user.id)))
    return text, markup


async def show_joined(target, user, giveaway_id: int, edit: bool, bot: Bot | None = None) -> None:
    """Edit the tapped message in place; only send when there is nothing to edit."""
    text, markup = await joined_view(user, giveaway_id)
    if not text:
        return
    sender = bot or getattr(target, "bot", None)

    async def send() -> None:
        if sender is not None:
            await sender.send_message(user.id, text, reply_markup=markup,
                                      parse_mode=ParseMode.HTML, link_preview_options=NO_PREVIEW)

    if edit and target is not None:
        try:
            await target.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML,
                                   link_preview_options=NO_PREVIEW)
            return
        except TelegramBadRequest as exc:
            log.info("joined view edit skipped: %s", exc)
            # the tapped message may be the photo/video giveaway card
            if getattr(target, "photo", None) or getattr(target, "video", None):
                try:
                    await target.edit_caption(caption=text, reply_markup=markup,
                                              parse_mode=ParseMode.HTML)
                    return
                except TelegramBadRequest as exc2:
                    log.info("caption edit skipped: %s", exc2)
    try:
        await send()
    except Exception as exc:                      # noqa: BLE001
        log.info("joined DM failed for %s: %s", user.id, exc)


async def close_giveaway(bot: Bot, giveaway_id: int) -> bool:
    if not await db.mark_finished(giveaway_id):
        return False
    giveaway = await db.get_giveaway(giveaway_id)
    ranking = await db.ranking(giveaway_id)
    for row in ranking:
        await refresh_card(bot, giveaway_id, row["user_id"], ended=True)
    try:
        await bot.send_message(config.GIVEAWAY_CHANNEL_TARGET,
                               await cards.results_text(giveaway, ranking),
                               parse_mode=ParseMode.HTML, link_preview_options=NO_PREVIEW)
    except Exception as exc:                      # noqa: BLE001
        log.error("could not publish results: %s", exc)
    asyncio.create_task(announce_results(bot, giveaway, ranking))
    return True


def pick_winners(ranking):
    """Highest-vote cards; with zero votes the first entrant wins."""
    if not ranking:
        return [], 0
    highest = max(int(r["votes"]) for r in ranking)
    if highest == 0:
        return [ranking[0]], 0
    return [r for r in ranking if int(r["votes"]) == highest], highest


async def announce_results(bot: Bot, giveaway, ranking) -> None:
    """DM every participant the winner — and tell the winner how to claim."""
    winners, highest = pick_winners(ranking)
    winner_ids = {w["user_id"] for w in winners}
    label = " & ".join(f"@{w['username']}" if w["username"] else w["full_name"] for w in winners)
    ranks = {r["user_id"]: i for i, r in enumerate(ranking, 1)}
    sent = failed = 0
    for row in ranking:
        try:
            if row["user_id"] in winner_ids:
                text = await cards.winner_dm(giveaway, row["full_name"], int(row["votes"]))
                markup = kb.winner_claim(await db.claim_handle(), await db.claim_url())
            else:
                text = await cards.ended_dm(giveaway, label, highest, ranks[row["user_id"]],
                                            int(row["votes"]), len(ranking))
                markup = kb.main_menu(await db.is_admin(row["user_id"]))
            await bot.send_message(row["user_id"], text, reply_markup=markup,
                                   parse_mode=ParseMode.HTML, link_preview_options=NO_PREVIEW)
            sent += 1
        except TelegramForbiddenError:
            await db.deactivate_user(row["user_id"])
            failed += 1
        except Exception as exc:                  # noqa: BLE001
            log.info("result DM failed for %s: %s", row["user_id"], exc)
            failed += 1
        await asyncio.sleep(BROADCAST_DELAY)
    log.info("giveaway #%s result DMs: %s sent, %s failed (winner %s)",
             giveaway["id"], sent, failed, label)


async def broadcast_giveaway(bot: Bot, giveaway_id: int) -> tuple[int, int]:
    """DM the new giveaway card to every verified user."""
    sent = failed = 0
    for row in await db.broadcast_targets():
        try:
            await send_giveaway_card(bot, row["user_id"], giveaway_id)
            sent += 1
        except TelegramForbiddenError:
            await db.deactivate_user(row["user_id"])
            failed += 1
        except Exception as exc:                  # noqa: BLE001
            log.info("broadcast failed for %s: %s", row["user_id"], exc)
            failed += 1
        await asyncio.sleep(BROADCAST_DELAY)
    log.info("giveaway #%s broadcast: %s sent, %s failed", giveaway_id, sent, failed)
    return sent, failed


# ── FSM ─────────────────────────────────────────────────────────────────────
class NewGiveaway(StatesGroup):
    name = State()
    prize = State()
    photo = State()
    duration = State()


class AddAdmin(StatesGroup):
    user_id = State()


class AddGate(StatesGroup):
    channel = State()


class Broadcast(StatesGroup):
    body = State()


class SetCheap(StatesGroup):
    url = State()


# ── vote captcha (colour match only) ────────────────────────────────────────
_CAPTCHA: dict[str, dict] = {}
_CAPTCHA_BY_USER: dict[int, str] = {}
_CAPTCHA_TTL = 300
_CAPTCHA_MAX_TRIES = 4
_COLOR_POOL = [
    ("🔴", "red"), ("🔵", "blue"), ("🟢", "green"),
    ("🟡", "yellow"), ("🟣", "purple"), ("🟠", "orange"),
    ("⚫", "black"), ("⚪", "white"),
]


def _captcha_purge() -> None:
    now = time.time()
    dead = [k for k, v in _CAPTCHA.items() if v["expires"] < now]
    for k in dead:
        rec = _CAPTCHA.pop(k, None)
        if rec:
            _CAPTCHA_BY_USER.pop(rec["user_id"], None)


def _color_puzzle() -> tuple[str, list[tuple[str, str]], str]:
    picks = random.sample(_COLOR_POOL, 6)
    target = random.choice(picks)
    options = [(e, n) for e, n in picks]
    instr = f"Match this colour  {target[0]}"
    return instr, options, target[1]


def _captcha_keyboard(token: str, options: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    random.shuffle(options)
    rows, pair = [], []
    for label, value in options:
        pair.append(btn(label, cb=f"cap:{token}:{value}", style="primary"))
        if len(pair) == 3:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _captcha_text(rec: dict, instr: str) -> str:
    who = rec.get("for_name") or "this card"
    left = _CAPTCHA_MAX_TRIES - rec["tries"]
    return (
        f"{R('{e:shield}')} <b>Match the colour</b>\n"
        f"{R('{e:ballot}')} Voting for <b>{cards.esc(who)}</b>\n\n"
        f"{instr}\n\n"
        f"<i>{left} tries left</i>"
    )


def _arm_step(rec: dict) -> tuple[str, InlineKeyboardMarkup]:
    instr, options, answer = _color_puzzle()
    rec["answer"] = answer
    rec["expires"] = time.time() + _CAPTCHA_TTL
    return _captcha_text(rec, instr), _captcha_keyboard(rec["token"], options)


async def _start_captcha_session(user_id: int, giveaway_id: int, participant_id: int,
                                 for_name: str) -> tuple[str, InlineKeyboardMarkup]:
    _captcha_purge()
    old = _CAPTCHA_BY_USER.pop(user_id, None)
    if old:
        _CAPTCHA.pop(old, None)
    token = secrets.token_hex(4)
    rec = {
        "token": token,
        "user_id": user_id,
        "giveaway_id": giveaway_id,
        "participant_id": participant_id,
        "for_name": for_name,
        "tries": 0,
        "expires": time.time() + _CAPTCHA_TTL,
        "answer": "",
    }
    _CAPTCHA[token] = rec
    _CAPTCHA_BY_USER[user_id] = token
    return _arm_step(rec)


async def send_vote_captcha(target: Message, user, giveaway_id: int, participant_id: int,
                            edit: bool = False):
    part = await db.get_participant(giveaway_id, participant_id)
    for_name = (part["full_name"] if part else "this card") or "this card"
    prompt, markup = await _start_captcha_session(user.id, giveaway_id, participant_id, for_name)
    if edit:
        try:
            await target.edit_text(prompt, reply_markup=markup, parse_mode=ParseMode.HTML)
            return
        except TelegramBadRequest:
            pass
    await target.answer(prompt, reply_markup=markup, parse_mode=ParseMode.HTML)


async def ask_confirm_vote(target: Message, user, giveaway_id: int, participant_id: int,
                           edit: bool = False):
    part = await db.get_participant(giveaway_id, participant_id)
    who = (part["full_name"] if part else "this card") or "this card"
    text = (
        f"{R('{e:ballot}')} <b>Confirm to vote</b>\n\n"
        f"You're voting for <b>{cards.esc(who)}</b>.\n"
        f"Tap confirm, then match the colour."
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [btn("Confirm to vote", cb=f"vok:{giveaway_id}:{participant_id}",
             ic="vote", style="success")],
    ])
    if edit:
        try:
            await target.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
            return
        except TelegramBadRequest:
            pass
    await target.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)


# ── /start + verification gate ──────────────────────────────────────────────
@router.message(CommandStart())
async def start(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    await remember_user(message.from_user)
    parts = (message.text or "").split(maxsplit=1)
    giveaway_id = 0
    vote_payload = None
    if len(parts) == 2:
        payload = parts[1]
        if re.fullmatch(r"g_\d+", payload):
            giveaway_id = int(payload[2:])
        elif re.fullmatch(r"v_\d+_\d+", payload):
            _, gs, ps = payload.split("_")
            vote_payload = (int(gs), int(ps))

    admin = await db.is_admin(message.from_user.id)
    gates, joined, missing = await gate_state(bot, message.from_user.id)
    if missing:
        vg, vp = (vote_payload if vote_payload else (giveaway_id or 0, 0))
        return await message.answer(
            await cards.gate_text(message.from_user.first_name or "friend", gates, joined),
            reply_markup=kb.join_gate(missing, vg or None, vp or None),
            parse_mode=ParseMode.HTML)

    await db.set_verified(message.from_user.id)
    if vote_payload:
        return await begin_vote_flow(message, bot, message.from_user, *vote_payload)
    if giveaway_id:
        return await enter_giveaway(message, bot, message.from_user, giveaway_id, admin)

    await message.answer(await cards.welcome(message.from_user.first_name or "friend", admin),
                         reply_markup=kb.main_menu(admin), parse_mode=ParseMode.HTML)


async def enter_giveaway(message: Message, bot: Bot, user, giveaway_id: int, admin: bool):
    ok, status = await register(bot, user, giveaway_id)
    giveaway = await db.get_giveaway(giveaway_id)
    name = cards.esc(giveaway["name"]) if giveaway else "this giveaway"

    if status == "JOIN_REQUIRED":
        gates, joined, missing = await gate_state(bot, user.id)
        return await message.answer(
            await cards.gate_text(user.first_name or "friend", gates, joined),
            reply_markup=kb.join_gate(missing, giveaway_id), parse_mode=ParseMode.HTML)
    if status in {"OK", "ALREADY"}:
        return await show_joined(message, user, giveaway_id, edit=True)
    if status == "ENDED":
        return await message.answer(
            R("{e:flag} <b>{name}</b> is already closed.\n\n"
              "Watch {channel} — the next drop lands soon {e:bell}")
            .format(name=name, channel=cards.esc(config.GIVEAWAY_CHANNEL_USERNAME)),
            reply_markup=kb.main_menu(admin), parse_mode=ParseMode.HTML)
    await message.answer(
        R("{e:cross} That giveaway doesn't exist. Check the link you were given."),
        reply_markup=kb.main_menu(admin), parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("verify:"))
async def verify_cb(callback: CallbackQuery, bot: Bot):
    bits = (callback.data or "verify:0:0").split(":")
    giveaway_id = int(bits[1]) if len(bits) > 1 and bits[1].isdigit() else 0
    participant_id = int(bits[2]) if len(bits) > 2 and bits[2].isdigit() else 0
    await remember_user(callback.from_user)
    gates, joined, missing = await gate_state(bot, callback.from_user.id)
    if missing:
        names = ", ".join(g.get("btn_title") or g["title"] for g in missing)
        await callback.answer(f"Join first: {names}", show_alert=True)
        try:
            await callback.message.edit_text(
                await cards.gate_text(callback.from_user.first_name or "friend", gates, joined),
                reply_markup=kb.join_gate(missing, giveaway_id or None, participant_id or None),
                parse_mode=ParseMode.HTML)
        except TelegramBadRequest:
            pass
        return

    await db.set_verified(callback.from_user.id)
    admin = await db.is_admin(callback.from_user.id)
    await callback.answer("Verified ✅", show_alert=False)

    if participant_id and giveaway_id:
        return await ask_confirm_vote(callback.message, callback.from_user,
                                      giveaway_id, participant_id, edit=True)

    if giveaway_id:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except TelegramBadRequest:
            pass
        return await enter_giveaway(callback.message, bot, callback.from_user, giveaway_id, admin)

    try:
        await callback.message.edit_text(
            await cards.welcome(callback.from_user.first_name or "friend", admin),
            reply_markup=kb.main_menu(admin), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(
            await cards.welcome(callback.from_user.first_name or "friend", admin),
            reply_markup=kb.main_menu(admin), parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("enter:"))
async def enter_cb(callback: CallbackQuery, bot: Bot):
    giveaway_id = int(callback.data.split(":", 1)[1])
    await remember_user(callback.from_user)
    gates, joined, missing = await gate_state(bot, callback.from_user.id)
    if missing:
        return await callback.answer(
            "Join first: " + ", ".join(g.get("btn_title") or g["title"] for g in missing), show_alert=True)
    await db.set_verified(callback.from_user.id)
    admin = await db.is_admin(callback.from_user.id)
    ok, status = await register(bot, callback.from_user, giveaway_id)
    if status in {"OK", "ALREADY"}:
        in_dm = callback.message.chat.type == "private"
        await show_joined(callback.message, callback.from_user, giveaway_id,
                          edit=in_dm, bot=bot)
        await callback.answer("Joined ✅" if status == "OK" else "Already joined ✅")
        return
    if status == "ENDED":
        await callback.answer("This giveaway has ended.", show_alert=True)
    else:
        await callback.answer("Giveaway not found.", show_alert=True)


# ── user commands ───────────────────────────────────────────────────────────
@router.message(Command("help"))
async def help_cmd(message: Message, bot: Bot):
    gates, joined, missing = await gate_state(bot, message.from_user.id)
    if missing:
        return await message.answer(
            await cards.gate_text(message.from_user.first_name or "friend", gates, joined),
            reply_markup=kb.join_gate(missing), parse_mode=ParseMode.HTML)
    await message.answer(await cards.how_it_works(),
                         reply_markup=kb.main_menu(await db.is_admin(message.from_user.id)),
                         parse_mode=ParseMode.HTML)


@router.message(Command("quote", "line"))
async def quote_cmd(message: Message):
    line = await lines.get_line("idle")
    await message.answer(
        R("{e:star_gold} <b>{brand}</b>\n<blockquote>{line}</blockquote>").format(
            brand=cards.esc(config.BRAND), line=cards.flair(line)), parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "menu:help")
async def menu_help(callback: CallbackQuery):
    await callback.message.edit_text(await cards.how_it_works(),
                                     reply_markup=kb.main_menu(await db.is_admin(callback.from_user.id)),
                                     parse_mode=ParseMode.HTML)
    await callback.answer()


# ── voting ──────────────────────────────────────────────────────────────────
async def begin_vote_flow(message: Message, bot: Bot, user, giveaway_id: int, participant_id: int):
    status = await vote_precheck(bot, user, giveaway_id, participant_id)
    if status == "closed":
        return await message.answer(R("{e:flag} Voting is closed."), parse_mode=ParseMode.HTML)
    if status == "self":
        return await message.answer("You can't vote for yourself 😏")
    if status == "missing":
        gates, joined, missing = await gate_state(bot, user.id)
        return await message.answer(
            await cards.gate_text(user.first_name or "friend", gates, joined),
            reply_markup=kb.join_gate(missing, giveaway_id, participant_id),
            parse_mode=ParseMode.HTML)
    if status == "gone":
        return await message.answer("Participant not found.")
    if status == "already":
        return await message.answer("Already counted — one vote per member 😉")
    await ask_confirm_vote(message, user, giveaway_id, participant_id)


async def vote_precheck(bot: Bot, user, giveaway_id: int, participant_id: int) -> str:
    giveaway = await db.get_giveaway(giveaway_id)
    if not giveaway or giveaway["status"] != "active" or \
            parse_iso(giveaway["ends_at"]) <= utcnow():
        return "closed"
    if user.id == participant_id:
        return "self"
    gates, joined, missing = await gate_state(bot, user.id)
    if missing:
        return "missing"
    await db.set_verified(user.id)
    if not await db.get_participant(giveaway_id, participant_id):
        return "gone"
    previous = await db.previous_vote(giveaway_id, user.id)
    if previous and previous["participant_id"] == participant_id:
        return "already"
    return "ok"


async def apply_vote(bot: Bot, user, giveaway_id: int, participant_id: int) -> str:
    previous = await db.previous_vote(giveaway_id, user.id)
    before = {r["user_id"]: i for i, r in enumerate(await db.ranking(giveaway_id), 1)}
    await db.cast_vote(giveaway_id, user.id, participant_id, iso(utcnow()))
    await refresh_card(bot, giveaway_id, participant_id)
    asyncio.create_task(notify_overtaken(bot, giveaway_id, participant_id, before))
    if previous:
        await refresh_card(bot, giveaway_id, previous["participant_id"])
        return "moved"
    return "counted"


@router.callback_query(F.data.startswith("cap:"))
async def captcha_cb(callback: CallbackQuery, bot: Bot):
    try:
        _, token, choice = callback.data.split(":", 2)
    except (ValueError, AttributeError):
        return await callback.answer("Invalid captcha.", show_alert=True)

    rec = _CAPTCHA.get(token)
    if not rec or rec["expires"] < time.time():
        _CAPTCHA.pop(token, None)
        return await callback.answer("Captcha expired — tap Vote again.", show_alert=True)
    if rec["user_id"] != callback.from_user.id:
        return await callback.answer("This captcha isn't yours.", show_alert=True)

    async def _paint(text: str, markup=None):
        try:
            await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
        except TelegramBadRequest:
            if markup is not None:
                await callback.message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)

    if choice != rec["answer"]:
        rec["tries"] += 1
        left = _CAPTCHA_MAX_TRIES - rec["tries"]
        if rec["tries"] >= _CAPTCHA_MAX_TRIES:
            _CAPTCHA.pop(token, None)
            _CAPTCHA_BY_USER.pop(rec["user_id"], None)
            await _paint(R("{e:cross} <b>Captcha locked</b>\n\n"
                           "Too many wrong answers. Tap <b>Vote</b> on the card to start over."))
            return await callback.answer("Locked — tap Vote again.", show_alert=True)
        prompt, markup = _arm_step(rec)
        await _paint(R("{e:warning} <b>Wrong.</b> Match again.\n\n") + prompt, markup)
        return await callback.answer(f"Wrong · {left} left")

    gid, pid = rec["giveaway_id"], rec["participant_id"]
    _CAPTCHA.pop(token, None)
    _CAPTCHA_BY_USER.pop(rec["user_id"], None)
    status = await vote_precheck(bot, callback.from_user, gid, pid)
    if status != "ok":
        msg = {
            "closed": "Voting is closed 🚩",
            "self": "You can't vote for yourself 😏",
            "missing": "Join all required channels & group first.",
            "gone": "Participant not found.",
            "already": "Already counted — one vote per member 😉",
        }.get(status, "Can't vote.")
        await _paint(msg)
        return await callback.answer(msg, show_alert=True)

    result = await apply_vote(bot, callback.from_user, gid, pid)
    text = "Vote moved ✅" if result == "moved" else "Vote counted ✅"
    await _paint(R("{e:check} <b>{t}</b>").format(t=text))
    await callback.answer(text, show_alert=True)


@router.callback_query(F.data.startswith("vok:"))
async def confirm_vote_cb(callback: CallbackQuery, bot: Bot):
    try:
        _, gid, pid = callback.data.split(":")
        giveaway_id, participant_id = int(gid), int(pid)
    except (ValueError, AttributeError):
        return await callback.answer("Invalid.", show_alert=True)
    status = await vote_precheck(bot, callback.from_user, giveaway_id, participant_id)
    if status == "missing":
        gates, joined, missing = await gate_state(bot, callback.from_user.id)
        try:
            await callback.message.edit_text(
                await cards.gate_text(callback.from_user.first_name or "friend", gates, joined),
                reply_markup=kb.join_gate(missing, giveaway_id, participant_id),
                parse_mode=ParseMode.HTML)
        except TelegramBadRequest:
            pass
        return await callback.answer("Join all required channels & group first.", show_alert=True)
    if status != "ok":
        msg = {
            "closed": "Voting is closed 🚩",
            "self": "You can't vote for yourself 😏",
            "gone": "Participant not found.",
            "already": "Already counted — one vote per member 😉",
        }.get(status, "Can't vote.")
        return await callback.answer(msg, show_alert=True)
    await callback.answer()
    await send_vote_captcha(callback.message, callback.from_user,
                            giveaway_id, participant_id, edit=True)


@router.callback_query(F.data.startswith("vote:"))
async def vote_cb(callback: CallbackQuery, bot: Bot):
    """Legacy cards still using a callback — send the voter into the bot captcha."""
    try:
        _, gid, pid = callback.data.split(":")
        giveaway_id, participant_id = int(gid), int(pid)
    except (ValueError, AttributeError):
        return await callback.answer("Invalid button.", show_alert=True)

    status = await vote_precheck(bot, callback.from_user, giveaway_id, participant_id)
    if status == "closed":
        return await callback.answer("Voting is closed 🚩", show_alert=True)
    if status == "self":
        return await callback.answer("You can't vote for yourself 😏", show_alert=True)
    if status == "missing":
        gates, joined, missing = await gate_state(bot, callback.from_user.id)
        try:
            await callback.from_user.send_message(
                await cards.gate_text(callback.from_user.first_name or "friend", gates, joined),
                reply_markup=kb.join_gate(missing), parse_mode=ParseMode.HTML)
        except Exception:                          # noqa: BLE001
            pass
        return await callback.answer(
            "Join first: " + ", ".join(g.get("btn_title") or g["title"] for g in missing), show_alert=True)
    if status == "gone":
        return await callback.answer("Participant not found.", show_alert=True)
    if status == "already":
        return await callback.answer("Already counted — one vote per member 😉", show_alert=True)

    try:
        dm = await callback.from_user.send_message("Opening vote captcha…")
        await send_vote_captcha(dm, callback.from_user, giveaway_id, participant_id)
        try:
            await dm.delete()
        except TelegramBadRequest:
            pass
        await callback.answer("Captcha sent in the bot — complete it there.", show_alert=True)
    except Exception:                              # noqa: BLE001
        link = vote_start_link(giveaway_id, participant_id)
        await callback.answer("Open the bot to complete captcha, then vote.", show_alert=True)
        try:
            await callback.from_user.send_message(
                R("{e:shield} Open <b>{b}</b> to complete the vote captcha.").format(b=cards.esc(config.BRAND)),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [btn("Continue", url=link, ic="vote", style="primary")],
                ]),
                parse_mode=ParseMode.HTML)
        except Exception:                          # noqa: BLE001
            pass


async def notify_overtaken(bot: Bot, giveaway_id: int, passer_id: int, before: dict) -> None:
    """DM everyone in the top 10 who just lost their place to the new vote."""
    after = await db.ranking(giveaway_id)
    if not after:
        return
    passer_row = await db.get_participant(giveaway_id, passer_id)
    if not passer_row:
        return
    passer = passer_row["full_name"]
    giveaway = await db.get_giveaway(giveaway_id)
    highest = max(int(r["votes"]) for r in after)
    for rank, row in enumerate(after, 1):
        if rank > 10:
            break
        if row["user_id"] == passer_id:
            continue
        was = before.get(row["user_id"])
        if was is None or was >= rank:            # did not move down
            continue
        try:
            post = await db.get_participant(giveaway_id, row["user_id"])
            card_url = channel_post_link(post["message_id"]) if post else ""
            await bot.send_message(
                row["user_id"],
                await cards.overtaken_text(row["full_name"], passer, giveaway["name"], rank,
                                           highest - int(row["votes"])),
                reply_markup=(kb.overtaken_kb(card_url, card_share_text(giveaway["name"]))
                              if card_url else None),
                parse_mode=ParseMode.HTML, link_preview_options=NO_PREVIEW)
        except TelegramForbiddenError:
            await db.deactivate_user(row["user_id"])
        except Exception as exc:                  # noqa: BLE001
            log.info("overtake alert failed for %s: %s", row["user_id"], exc)
        await asyncio.sleep(BROADCAST_DELAY)


# ── admin: panel ────────────────────────────────────────────────────────────
async def show_admin(target: Message | CallbackQuery):
    text = await cards.admin_panel()
    if isinstance(target, CallbackQuery):
        try:
            await target.message.edit_text(text, reply_markup=kb.admin_home(),
                                           parse_mode=ParseMode.HTML)
        except TelegramBadRequest:
            await target.message.answer(text, reply_markup=kb.admin_home(),
                                        parse_mode=ParseMode.HTML)
        await target.answer()
    else:
        await target.answer(text, reply_markup=kb.admin_home(), parse_mode=ParseMode.HTML)


@router.message(Command("admin", "panel"))
async def admin_cmd(message: Message, state: FSMContext):
    if not await db.is_admin(message.from_user.id):
        return await message.answer(R("{e:lock} Admins only."), parse_mode=ParseMode.HTML)
    await state.clear()
    await show_admin(message)


@router.callback_query(F.data == "admin:home")
async def admin_home(callback: CallbackQuery, state: FSMContext):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    await state.clear()
    await show_admin(callback)


@router.callback_query(F.data == "admin:cancel")
async def admin_cancel(callback: CallbackQuery, state: FSMContext):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    await state.clear()
    await show_admin(callback)


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    s = await db.overall_stats()
    await callback.message.edit_text(
        R("{e:stats} <b>" + cards.esc(config.BRAND) + " — Statistics</b>\n\n"
          "{e:gift} Giveaways: <b>{g}</b>\n"
          "{e:fire} Active: <b>{a}</b> · {e:flag} Finished: <b>{f}</b>\n"
          "{e:users} Verified users: <b>{u}</b>\n"
          "{e:crown} Total entries: <b>{e_}</b>\n"
          "{e:ballot} Stored votes: <b>{v}</b>").format(
            g=s["giveaways"], a=s["active"], f=s["finished"], u=s["users"],
            e_=s["entries"], v=s["votes"]),
        reply_markup=kb.back_home(), parse_mode=ParseMode.HTML)
    await callback.answer()


def _cheap_link(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw or raw.lower() in {"-", "none", "clear", "off", "remove"}:
        return ""
    if raw.startswith("@"):
        return "https://t.me/" + raw.lstrip("@")
    if re.fullmatch(r"[A-Za-z0-9_]{4,}", raw):
        return "https://t.me/" + raw
    if raw.startswith("t.me/"):
        return "https://" + raw
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    return ""


@router.callback_query(F.data == "admin:cheap")
async def cheap_start(callback: CallbackQuery, state: FSMContext):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    current = await db.cheap_api_url()
    shown = current or "not set"
    await state.set_state(SetCheap.url)
    await callback.message.edit_text(
        R("{e:link} <b>Extra card link ({label})</b>\n\n"
          "Optional button shown under every voting card.\n"
          "Not required to vote.\n\n"
          "Current: <code>{cur}</code>\n\n"
          "Send a channel/group link or @username.\n"
          "Send <code>-</code> to remove it.").format(
            label=cards.esc(config.EXTRA_BTN_LABEL), cur=cards.esc(shown)),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [btn("Cancel", cb="admin:cancel", ic="skip", style="danger")],
        ]),
        parse_mode=ParseMode.HTML)
    await callback.answer()


@router.message(SetCheap.url)
async def cheap_receive(message: Message, state: FSMContext):
    if not await db.is_admin(message.from_user.id):
        return
    url = _cheap_link(message.text or "")
    if (message.text or "").strip() and url == "" and (message.text or "").strip() not in {"-", "none", "clear", "off", "remove"}:
        return await message.answer("Send a t.me link, @username, or - to clear.")
    await db.set_setting("cheap_api_url", url)
    await state.clear()
    if url:
        await message.answer(
            R("{e:check} Extra card button set to\n{url}").format(url=cards.esc(url)),
            parse_mode=ParseMode.HTML,
            reply_markup=kb.admin_home())
    else:
        await message.answer(
            R("{e:check} Extra card button removed from cards."),
            parse_mode=ParseMode.HTML,
            reply_markup=kb.admin_home())


@router.callback_query(F.data == "admin:help")
async def admin_help(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    claim = await db.claim_handle()
    await callback.message.edit_text(
        R("{e:info} <b>Required setup — {brand}</b>\n\n"
          "{e:check_plain} Bot <b>@{me}</b> is admin in <b>{gch}</b> with <i>Post + Edit</i> rights (giveaways, cards & results post here)\n"
          "{e:check_plain} Bot <b>@{me}</b> is admin in <b>{main_title}</b> ({main_ch} · <code>{main_id}</code>)\n"
          "{e:check_plain} Bot <b>@{me}</b> is admin in <b>{grp}</b> (<code>{grp_id}</code>)\n"
          "{e:check_plain} Bot owner needs Telegram Premium for custom emojis & button icons\n\n"
          "{e:shield} Members who leave any required channel or group lose their votes automatically.\n"
          "{e:trophy} Prize claim contact: <b>{claim}</b> (change anytime with <code>/setclaim @handle</code>)\n"
          "{e:owner_tag} Owners: <code>{owners}</code>").format(
            brand=cards.esc(config.BRAND),
            me=cards.esc(bot_username),
            gch=cards.esc(config.GIVEAWAY_CHANNEL_USERNAME),
            main_title=cards.esc(config.MAIN_CHANNEL_TITLE),
            main_ch=cards.esc(config.MAIN_CHANNEL_USERNAME),
            main_id=config.MAIN_CHANNEL_ID,
            grp=cards.esc(config.GROUP_USERNAME),
            grp_id=config.GROUP_ID,
            claim=cards.esc(claim),
            owners=", ".join(map(str, sorted(config.OWNER_IDS)))),
        reply_markup=kb.back_home(), parse_mode=ParseMode.HTML)
    await callback.answer()


# ── admin: create giveaway ──────────────────────────────────────────────────
@router.callback_query(F.data == "admin:create")
async def create_start(callback: CallbackQuery, state: FSMContext):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    await state.set_state(NewGiveaway.name)
    await callback.message.edit_text(
        R("{e:gift} <b>New giveaway — step 1/4</b>\n\n"
          "Send the giveaway <b>title</b>.\n"
          "<i>Example: iPhone 17 Pro Drop · USDT 500 Round · TG Mandi Mega Drop</i>"),
        reply_markup=kb.cancel_only(), parse_mode=ParseMode.HTML)
    await callback.answer()


@router.message(NewGiveaway.name)
async def create_name(message: Message, state: FSMContext):
    if not await db.is_admin(message.from_user.id):
        return
    name = (message.text or "").strip()
    if not (2 <= len(name) <= 100):
        return await message.answer(R("{e:warning} Title must be 2–100 characters."),
                                    parse_mode=ParseMode.HTML)
    await state.update_data(name=name)
    await state.set_state(NewGiveaway.prize)
    await message.answer(
        R("{e:gem} <b>Step 2/4 — prize</b>\n\n"
          "What is being given away?\n<i>Example: 500 USDT · iPhone 17 Pro · 3x Premium Gift</i>"),
        reply_markup=kb.cancel_only(), parse_mode=ParseMode.HTML)


@router.message(NewGiveaway.prize)
async def create_prize(message: Message, state: FSMContext):
    if not await db.is_admin(message.from_user.id):
        return
    prize = (message.text or "").strip()
    if not (2 <= len(prize) <= 500):
        return await message.answer(R("{e:warning} Prize must be 2–500 characters."),
                                    parse_mode=ParseMode.HTML)
    await state.update_data(prize=prize)
    await state.set_state(NewGiveaway.photo)
    await message.answer(
        R("{e:photo} <b>Step 3/4 — giveaway media</b>\n\n"
          "Send a <b>photo</b> or a <b>video</b>. It is shown when anyone opens this giveaway.\n\n"
          "{e:thinking} No media? Tap the button below."),
        reply_markup=kb.photo_step(), parse_mode=ParseMode.HTML)


@router.message(NewGiveaway.photo, F.photo | F.video)
async def create_photo(message: Message, state: FSMContext):
    if not await db.is_admin(message.from_user.id):
        return
    if message.video:
        await state.update_data(photo=message.video.file_id, media_kind="video")
    else:
        await state.update_data(photo=message.photo[-1].file_id, media_kind="photo")
    await state.set_state(NewGiveaway.duration)
    await message.answer(
        R("{e:check} Media attached.\n\n"
          "{e:hourglass} <b>Step 4/4 — duration</b>\n\n"
          "Pick how long voting stays open, or type <code>12h</code>, <code>30m</code>, "
          "<code>3d</code>, <code>1w</code>."),
        reply_markup=kb.duration_kb(), parse_mode=ParseMode.HTML)


@router.callback_query(NewGiveaway.photo, F.data == "photo:skip")
async def create_photo_skip(callback: CallbackQuery, state: FSMContext):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    await state.update_data(photo="")
    await state.set_state(NewGiveaway.duration)
    await callback.message.edit_text(
        R("{e:cross} No photo — fine.\n\n"
          "{e:hourglass} <b>Step 4/4 — duration</b>\n\n"
          "Pick how long voting stays open, or type <code>12h</code>, <code>3d</code>, "
          "<code>1w</code>."),
        reply_markup=kb.duration_kb(), parse_mode=ParseMode.HTML)
    await callback.answer()


@router.message(NewGiveaway.photo)
async def create_photo_wrong(message: Message):
    if not await db.is_admin(message.from_user.id):
        return
    await message.answer(
        R("{e:warning} Send a <b>photo</b> or a <b>video</b>, or tap <b>Skip</b>."),
        reply_markup=kb.photo_step(), parse_mode=ParseMode.HTML)


async def finish_creation(message: Message, state: FSMContext, bot: Bot, admin_id: int, value: str):
    delta = parse_duration(value)
    if not delta:
        return await message.answer(
            R("{e:cross} Invalid duration. Use <code>5m</code>–<code>365d</code> "
              "(<code>12h</code>, <code>2d</code>, <code>1w</code>)."),
            reply_markup=kb.duration_kb(), parse_mode=ParseMode.HTML)
    data = await state.get_data()
    name, prize = data.get("name"), data.get("prize", "")
    photo = data.get("photo", "")
    media_kind = data.get("media_kind", "photo")
    if not name:
        await state.clear()
        return await message.answer(R("{e:warning} Session expired — open /admin and start again."),
                                    parse_mode=ParseMode.HTML)

    created, ends = utcnow(), utcnow() + delta
    giveaway_id = await db.create_giveaway(name, prize, photo, admin_id, iso(created), iso(ends),
                                          media_kind)
    await state.clear()

    published = False
    try:
        sent = await send_giveaway_card(bot, config.GIVEAWAY_CHANNEL_TARGET, giveaway_id)
        published = sent is not None
        if sent:
            await db.set_giveaway_post(giveaway_id, sent.message_id)
            try:                                   # point Share at the giveaway channel post
                await bot.edit_message_reply_markup(
                    config.GIVEAWAY_CHANNEL_TARGET, sent.message_id,
                    reply_markup=kb.participate(
                        giveaway_id, channel_post_link(sent.message_id),
                        giveaway_share_text(name)))
            except Exception as exc:               # noqa: BLE001
                log.info("share target update skipped: %s", exc)
    except Exception as exc:                      # noqa: BLE001
        log.error("could not publish giveaway card: %s", exc)

    asyncio.create_task(broadcast_giveaway(bot, giveaway_id))

    row = await db.giveaway_stats_row(giveaway_id)
    link = start_link(giveaway_id)
    status_line = (
        R("{e:rocket} <b>Live now</b> — posted in {ch}, broadcasting to every member").format(
            ch=cards.esc(config.GIVEAWAY_CHANNEL_USERNAME))
        if published else
        R("{e:warning} <b>Created, but the giveaway channel post failed.</b>\n"
          "Make the bot admin in {ch} with post + edit rights.").format(
            ch=cards.esc(config.GIVEAWAY_CHANNEL_USERNAME)))
    await message.answer(
        cards.giveaway_admin(row, link) + "\n\n" + status_line,
        reply_markup=kb.giveaway_actions(giveaway_id, "active", link,
                                         giveaway_share_text(name)),
        parse_mode=ParseMode.HTML)


@router.callback_query(NewGiveaway.duration, F.data.startswith("duration:"))
async def duration_button(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    await callback.answer()
    await finish_creation(callback.message, state, bot, callback.from_user.id,
                          callback.data.split(":", 1)[1])


@router.message(NewGiveaway.duration)
async def duration_custom(message: Message, state: FSMContext, bot: Bot):
    if await db.is_admin(message.from_user.id):
        await finish_creation(message, state, bot, message.from_user.id, message.text or "")


# ── admin: lists / view / end / delete / export ─────────────────────────────
@router.callback_query(F.data.startswith("admin:list:"))
async def admin_list(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    status = callback.data.rsplit(":", 1)[1]
    rows = await db.list_giveaways(status, 30)
    title = R("{e:fire} <b>Active giveaways</b>") if status == "active" \
        else R("{e:flag} <b>Finished giveaways</b>")
    buttons = [[kb.btn(f"#{r['id']} · {r['name'][:28]} ({r['participants']}👤/{r['votes']}🗳)",
                       cb=f"admin:view:{r['id']}", ic="gift")] for r in rows]
    buttons.append([kb.btn("Admin panel", cb="admin:home", ic="back")])
    await callback.message.edit_text(
        title + "\n\n" + ("Pick a giveaway:" if rows else "Nothing here yet."),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:view:"))
async def admin_view(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    giveaway_id = int(callback.data.rsplit(":", 1)[1])
    row = await db.giveaway_stats_row(giveaway_id)
    if not row:
        return await callback.answer("Giveaway not found.", show_alert=True)
    link = start_link(giveaway_id)
    await callback.message.edit_text(cards.giveaway_admin(row, link),
                                     reply_markup=kb.giveaway_actions(giveaway_id, row["status"],
                                                                     giveaway_share_target(row),
                                                                     giveaway_share_text(row["name"])),
                                     parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:refresh:"))
async def admin_refresh(callback: CallbackQuery, bot: Bot):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    giveaway_id = int(callback.data.rsplit(":", 1)[1])
    await callback.answer("Refreshing cards…")
    rows = await db.ranking(giveaway_id)
    for r in rows:
        await refresh_card(bot, giveaway_id, r["user_id"])
    await callback.message.answer(R("{e:refresh} Refreshed <b>{n}</b> cards.").format(n=len(rows)),
                                  parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("admin:export:"))
async def admin_export(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    giveaway_id = int(callback.data.rsplit(":", 1)[1])
    giveaway = await db.get_giveaway(giveaway_id)
    rows = await db.ranking(giveaway_id)
    if not rows:
        return await callback.answer("No entries to export yet.", show_alert=True)

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["rank", "user_id", "full_name", "username", "votes", "real_votes", "joined_at"])
    for i, r in enumerate(rows, 1):
        w.writerow([i, r["user_id"], r["full_name"], r["username"] or "",
                    r["votes"], r["real_votes"], r["joined_at"]])
    path = f"/tmp/nextgen_{giveaway_id}_entries.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        fh.write(buf.getvalue())
    await callback.message.answer_document(
        FSInputFile(path, filename=f"NextGen_giveaway_{giveaway_id}_entries.csv"),
        caption=R("{e:chart} <b>{name}</b> — {n} entries").format(
            name=cards.esc(giveaway["name"]), n=len(rows)), parse_mode=ParseMode.HTML)
    await callback.answer("Exported ✅")


@router.callback_query(F.data.startswith("admin:endask:"))
async def end_ask(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    gid = int(callback.data.rsplit(":", 1)[1])
    await callback.message.edit_text(
        R("{e:warning} <b>End this giveaway now?</b>\n\n"
          "Voting stops, every card freezes at its final count and the result banner "
          "is published in {ch}.").format(ch=cards.esc(config.GIVEAWAY_CHANNEL_USERNAME)),
        reply_markup=kb.confirm_end(gid), parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:end:"))
async def end_now(callback: CallbackQuery, bot: Bot):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    gid = int(callback.data.rsplit(":", 1)[1])
    await callback.answer("Closing…")
    closed = await close_giveaway(bot, gid)
    await callback.message.edit_text(
        R("{e:party} <b>Giveaway ended.</b>\n\nResults are published in {ch}.").format(
            ch=cards.esc(config.GIVEAWAY_CHANNEL_USERNAME)) if closed
        else R("{e:warning} This giveaway is already finished."),
        reply_markup=kb.back_home(), parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("admin:delask:"))
async def del_ask(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    gid = int(callback.data.rsplit(":", 1)[1])
    await callback.message.edit_text(
        R("{e:skull} <b>Delete giveaway #{gid}?</b>\n\n"
          "Every entry, vote and adjustment is erased.\n<i>This cannot be undone.</i>").format(gid=gid),
        reply_markup=kb.confirm_delete(gid), parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:del:"))
async def del_confirm(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    gid = int(callback.data.rsplit(":", 1)[1])
    await db.run("DELETE FROM vote_adjust WHERE giveaway_id=?", (gid,))
    await db.run("DELETE FROM giveaways WHERE id=?", (gid,))
    await callback.message.edit_text(R("{e:check} Giveaway <code>#{g}</code> deleted.").format(g=gid),
                                     reply_markup=kb.back_home(), parse_mode=ParseMode.HTML)
    await callback.answer()


# ── admin: broadcast ───────────────────────────────────────────────────────
@router.callback_query(F.data == "admin:bc")
async def bc_start(callback: CallbackQuery, state: FSMContext):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    await state.set_state(Broadcast.body)
    await callback.message.edit_text(await cards.broadcast_prompt(),
                                     reply_markup=kb.cancel_only(), parse_mode=ParseMode.HTML)
    await callback.answer()


@router.message(Broadcast.body)
async def bc_receive(message: Message, state: FSMContext):
    if not await db.is_admin(message.from_user.id):
        return
    try:
        body = compose_body(message)
    except ValueError as exc:
        return await message.answer(R("{e:cross} {err}").format(err=cards.esc(str(exc))),
                                    parse_mode=ParseMode.HTML)

    if message.photo:
        payload = {"kind": "photo", "file_id": message.photo[-1].file_id, "body": body}
    elif message.video:
        payload = {"kind": "video", "file_id": message.video.file_id, "body": body}
    elif message.text:
        payload = {"kind": "text", "body": body}
    else:
        return await message.answer(
            R("{e:cross} Send text, a photo or a video (caption works too)."),
            parse_mode=ParseMode.HTML)
    await state.update_data(payload=payload)
    recipients = len(await db.broadcast_targets())
    await message.answer(await cards.broadcast_preview(payload["body"], recipients),
                         reply_markup=kb.broadcast_confirm(), parse_mode=ParseMode.HTML,
                         link_preview_options=NO_PREVIEW)


@router.callback_query(F.data.in_({"bc:send", "bc:sendall"}))
async def bc_go(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    payload = (await state.get_data()).get("payload")
    if not payload:
        return await callback.answer("Nothing to send — start again.", show_alert=True)
    await state.clear()
    to_channel = callback.data == "bc:sendall"
    await callback.answer("Sending…")
    try:
        await callback.message.edit_text(R("{e:megaphone} <b>Sending…</b>"),
                                         parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        pass
    asyncio.create_task(run_broadcast(bot, payload, to_channel,
                                      callback.message.chat.id, callback.message.message_id))


async def run_broadcast(bot: Bot, payload: dict, to_channel: bool,
                        chat_id: int, message_id: int) -> None:
    note = ""
    async def deliver(chat_id: int) -> None:
        kind = payload["kind"]
        try:
            await _deliver_raw(chat_id, kind)
        except TelegramBadRequest as exc:
            log.info("broadcast HTML rejected (%s) — retrying as plain text", exc)
            plain = re.sub(r"<[^>]+>", "", payload["body"] or "")
            if kind == "text":
                await bot.send_message(chat_id, plain, link_preview_options=NO_PREVIEW)
            elif kind == "photo":
                await bot.send_photo(chat_id, payload["file_id"], caption=plain or None)
            else:
                await bot.send_video(chat_id, payload["file_id"], caption=plain or None)

    async def _deliver_raw(chat_id: int, kind: str) -> None:
        if kind == "photo":
            await bot.send_photo(chat_id, payload["file_id"],
                                 caption=payload["body"] or None, parse_mode=ParseMode.HTML)
        elif kind == "video":
            await bot.send_video(chat_id, payload["file_id"],
                                 caption=payload["body"] or None, parse_mode=ParseMode.HTML)
        else:
            await bot.send_message(chat_id, payload["body"], parse_mode=ParseMode.HTML,
                                   link_preview_options=NO_PREVIEW)

    if to_channel:
        try:
            await deliver(config.GIVEAWAY_CHANNEL_TARGET)
            note = f"also posted in {config.GIVEAWAY_CHANNEL_USERNAME}"
        except Exception as exc:                  # noqa: BLE001
            note = f"channel post failed: {str(exc)[:60]}"

    sent = failed = 0
    for row in await db.broadcast_targets():
        try:
            await deliver(row["user_id"])
            sent += 1
        except TelegramForbiddenError:
            await db.deactivate_user(row["user_id"])
            failed += 1
        except Exception as exc:                  # noqa: BLE001
            log.info("broadcast failed for %s: %s", row["user_id"], exc)
            failed += 1
        await asyncio.sleep(BROADCAST_DELAY)

    log.info("admin broadcast: %s sent, %s failed", sent, failed)
    try:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text=await cards.broadcast_done(sent, failed, note),
                                    parse_mode=ParseMode.HTML)
    except Exception:                             # noqa: BLE001
        pass


# ── admin: emoji index ─────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("admin:emoji:"))
async def emoji_index(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    page = int(callback.data.rsplit(":", 1)[1])
    text, pages = cards.emoji_index_text(page)
    await callback.message.edit_text(
        text, reply_markup=kb.emoji_index(min(page, pages - 1), pages),
        parse_mode=ParseMode.HTML)
    await callback.answer()


# ── admin: required channels (extra force-join) ─────────────────────────────
@router.callback_query(F.data == "admin:gates")
async def gates_panel(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    rows = await db.list_gate_channels()
    await callback.message.edit_text(cards.gate_panel_text(rows),
                                     reply_markup=kb.gate_panel(rows),
                                     parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data == "admin:gateadd")
async def gate_add_start(callback: CallbackQuery, state: FSMContext):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    await state.set_state(AddGate.channel)
    await callback.message.edit_text(await cards.gate_add_prompt(bot_username),
                                     reply_markup=kb.cancel_only(),
                                     parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:gatedel:"))
async def gate_del(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    row_id = int(callback.data.rsplit(":", 1)[1])
    await db.del_gate_channel(row_id)
    await callback.answer("Channel removed")
    rows = await db.list_gate_channels()
    await callback.message.edit_text(cards.gate_panel_text(rows),
                                     reply_markup=kb.gate_panel(rows),
                                     parse_mode=ParseMode.HTML)


@router.message(AddGate.channel)
async def gate_add_receive(message: Message, state: FSMContext, bot: Bot):
    if not await db.is_admin(message.from_user.id):
        return
    text = (message.text or "").strip()
    target = None
    if message.forward_from_chat:
        target = message.forward_from_chat.id
    elif text.startswith("@") or text.lstrip("-").isdigit():
        target = int(text) if text.lstrip("-").isdigit() else text
    else:
        m = re.fullmatch(r"https?://t\.me/([A-Za-z0-9_]{4,})/?", text)
        if m:
            target = "@" + m.group(1)
    if target is None:
        return await message.answer(
            R("{e:cross} Send <code>@username</code>, a t.me link, a numeric chat id, "
              "or forward a message from that channel."), parse_mode=ParseMode.HTML)

    try:
        chat = await bot.get_chat(target)
    except Exception as exc:                      # noqa: BLE001
        return await message.answer(
            R("{e:cross} Can't resolve that channel.\n\n{e:info} <code>{err}</code>\n\n"
              "{e:thinking} Private channels: add <b>@{me}</b> as admin first, then forward "
              "a message from it.").format(err=cards.esc(str(exc)[:160]), me=cards.esc(bot_username)),
            parse_mode=ParseMode.HTML)

    builtin_ids = {x for x in (config.MAIN_CHANNEL_ID, config.GIVEAWAY_CHANNEL_ID, config.GROUP_ID) if x}
    builtin_names = {
        x.lstrip("@").lower()
        for x in (config.MAIN_CHANNEL_USERNAME, config.GIVEAWAY_CHANNEL_USERNAME, config.GROUP_USERNAME)
        if x
    }
    if chat.id in builtin_ids or (chat.username and chat.username.lower() in builtin_names):
        await state.clear()
        return await message.answer(
            R("{e:info} That's already one of the core required channels/groups — always required."),
            reply_markup=kb.back_home(), parse_mode=ParseMode.HTML)

    me = await bot.get_me()
    try:
        status = (await bot.get_chat_member(chat.id, me.id)).status
    except Exception:                             # noqa: BLE001
        status = None
    if status not in {ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR}:
        return await message.answer(
            R("{e:lock} <b>@{me} must be an admin in {title}</b>\n\n"
              "Telegram only lets a bot check membership where it is an administrator.\n"
              "Add the bot as admin there, then send the channel again.")
            .format(me=cards.esc(bot_username),
                    title=cards.esc(chat.title or chat.username or chat.id)),
            reply_markup=kb.cancel_only(), parse_mode=ParseMode.HTML)

    url = f"https://t.me/{chat.username}" if chat.username else ""
    if not url:
        try:
            url = await bot.export_chat_invite_link(chat.id)
        except Exception:                         # noqa: BLE001
            url = ""
    if not url:
        return await message.answer(
            R("{e:warning} Can't build an invite link for <b>{title}</b>.\n"
              "Make the bot admin with <i>invite users</i> rights and send it again.")
            .format(title=cards.esc(chat.title or chat.id)), parse_mode=ParseMode.HTML)

    await db.add_gate_channel(chat.id, chat.username, chat.title or "", url,
                              message.from_user.id, iso(utcnow()))
    await state.clear()
    rows = await db.list_gate_channels()
    await message.answer(
        R("{e:check} <b>{title}</b> is now a required channel.").format(
            title=cards.esc(chat.title or chat.username or chat.id)) + "\n\n" +
        cards.gate_panel_text(rows),
        reply_markup=kb.gate_panel(rows), parse_mode=ParseMode.HTML)


# ── admin: vote management ──────────────────────────────────────────────────
@router.callback_query(F.data == "admin:votelist")
async def vote_list(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    rows = await db.any_giveaways(20)
    if not rows:
        return await callback.answer("No giveaways yet.", show_alert=True)
    await callback.message.edit_text(await cards.vote_admin_list_intro(),
                                     reply_markup=kb.vote_giveaway_list(rows),
                                     parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:voters:"))
async def vote_participants_list(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    parts = callback.data.split(":")
    giveaway_id = int(parts[2])
    page = int(parts[3]) if len(parts) > 3 else 0
    giveaway = await db.get_giveaway(giveaway_id)
    rows = await db.ranking(giveaway_id)
    if not rows:
        return await callback.answer("No entries in this giveaway yet.", show_alert=True)
    await callback.message.edit_text(
        await cards.vote_participants_intro(giveaway),
        reply_markup=kb.vote_participants(giveaway_id, rows, page),
        parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:votes:"))
async def vote_edit_screen(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    _, _, gid, pid = callback.data.split(":")
    giveaway_id, participant_id = int(gid), int(pid)
    giveaway = await db.get_giveaway(giveaway_id)
    participant = await db.get_participant(giveaway_id, participant_id)
    if not giveaway or not participant:
        return await callback.answer("Card not found.", show_alert=True)
    await callback.message.edit_text(
        cards.vote_edit_text(participant, giveaway,
                             await db.votes_for(giveaway_id, participant_id),
                             await db.real_votes(giveaway_id, participant_id)),
        reply_markup=kb.vote_edit(giveaway_id, participant_id,
                                  await db.votes_for(giveaway_id, participant_id),
                                  await db.real_votes(giveaway_id, participant_id)),
        parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:vote:"))
async def vote_edit_apply(callback: CallbackQuery, bot: Bot):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    _, _, gid, pid, action = callback.data.split(":")
    giveaway_id, participant_id, action = int(gid), int(pid), int(action)
    if action == 0:
        await db.reset_adjust(giveaway_id, participant_id)
        msg = "Votes reset to 0"
    else:
        await db.add_adjust(giveaway_id, participant_id, action)
        msg = "Vote added ✅" if action > 0 else "Vote removed ✅"
    await refresh_card(bot, giveaway_id, participant_id)
    await callback.answer(msg, show_alert=True)

    giveaway = await db.get_giveaway(giveaway_id)
    participant = await db.get_participant(giveaway_id, participant_id)
    count = await db.votes_for(giveaway_id, participant_id)
    real = await db.real_votes(giveaway_id, participant_id)
    if giveaway and participant:
        try:
            await callback.message.edit_text(
                cards.vote_edit_text(participant, giveaway, count, real),
                reply_markup=kb.vote_edit(giveaway_id, participant_id, count, real),
                parse_mode=ParseMode.HTML)
        except TelegramBadRequest:
            pass


# ── admin: prize claim handle + admin management ────────────────────────────
@router.message(Command("setclaim"))
async def setclaim_cmd(message: Message):
    if not await db.is_admin(message.from_user.id):
        return await message.answer(R("{e:lock} Admins only."), parse_mode=ParseMode.HTML)
    arg = (message.text or "").split(maxsplit=1)
    if len(arg) != 2 or not arg[1].strip():
        cur = await db.claim_handle()
        return await message.answer(
            R("{e:trophy} Current prize-claim handle: <b>{cur}</b>\n\n"
              "Usage: <code>/setclaim @username</code>").format(cur=cards.esc(cur)),
            parse_mode=ParseMode.HTML)
    val = arg[1].strip()
    if not (val.startswith("@") or val.startswith("https://t.me/")):
        val = "@" + val.lstrip("@")
    await db.set_setting("claim_handle", val)
    await message.answer(
        R("{e:check} Prize-claim contact updated to <b>{v}</b>.").format(v=cards.esc(val)),
        parse_mode=ParseMode.HTML)


@router.message(Command("addadmin"))
async def addadmin_cmd(message: Message):
    if message.from_user.id not in config.OWNER_IDS:
        return await message.answer(R("{e:lock} Only owners can manage admins."),
                                    parse_mode=ParseMode.HTML)
    arg = (message.text or "").split(maxsplit=1)
    target = None
    if len(arg) == 2 and arg[1].strip().isdigit():
        target = int(arg[1].strip())
    elif message.reply_to_message:
        target = message.reply_to_message.from_user.id
    if not target:
        return await message.answer(
            R("{e:thinking} Usage: <code>/addadmin 123456789</code> "
              "or reply to a message with <code>/addadmin</code>."), parse_mode=ParseMode.HTML)
    await db.add_admin(target, message.from_user.id, iso(utcnow()))
    await message.answer(R("{e:crown} <code>{u}</code> is now an admin.").format(u=target),
                         parse_mode=ParseMode.HTML)


@router.message(Command("deladmin"))
async def deladmin_cmd(message: Message):
    if message.from_user.id not in config.OWNER_IDS:
        return await message.answer(R("{e:lock} Only owners can manage admins."),
                                    parse_mode=ParseMode.HTML)
    arg = (message.text or "").split(maxsplit=1)
    if len(arg) != 2 or not arg[1].strip().isdigit():
        return await message.answer(R("{e:thinking} Usage: <code>/deladmin 123456789</code>"),
                                    parse_mode=ParseMode.HTML)
    uid = int(arg[1].strip())
    if uid in config.OWNER_IDS:
        return await message.answer(R("{e:lock} Owners can't be removed from the bot config."),
                                    parse_mode=ParseMode.HTML)
    removed = await db.del_admin(uid)
    await message.answer(R("{e:check} Admin removed.") if removed
                         else R("{e:cross} That user isn't an admin."),
                         parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "admin:admins")
async def admins_panel(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer("Admins only.", show_alert=True)
    rows = await db.list_admins()
    owners = "\n".join(R("{e:owner_tag} <code>{o}</code>").format(o=o) for o in sorted(config.OWNER_IDS))
    extra = "\n".join(R("{e:admin_tag} <code>{u}</code> · {d}").format(
        u=r["user_id"], d=cards.fmt_dt(r["added_at"], "%d %b %Y")) for r in rows) \
        or "<i>no extra admins yet</i>"
    note = "" if callback.from_user.id in config.OWNER_IDS else \
        R("\n\n{e:lock} <i>Only owners can add or remove admins.</i>")
    await callback.message.edit_text(
        R("{e:crown} <b>Admin team</b>\n\n<b>Owners</b>\n{owners}\n\n"
          "<b>Added admins</b>\n{extra}{note}").format(owners=owners, extra=extra, note=note),
        reply_markup=kb.admins_panel(rows), parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data == "admin:addadmin")
async def addadmin_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in config.OWNER_IDS:
        return await callback.answer("Owners only.", show_alert=True)
    await state.set_state(AddAdmin.user_id)
    await callback.message.edit_text(
        R("{e:crown} <b>Add an admin</b>\n\n"
          "Send the <b>user ID</b>, or forward a message from that person."),
        reply_markup=kb.cancel_only(), parse_mode=ParseMode.HTML)
    await callback.answer()


@router.message(AddAdmin.user_id)
async def addadmin_receive(message: Message, state: FSMContext):
    if message.from_user.id not in config.OWNER_IDS:
        return
    text = (message.text or "").strip()
    target = int(text) if text.isdigit() else (
        message.forward_from.id if message.forward_from else None)
    if not target:
        return await message.answer(
            R("{e:cross} Send a numeric user ID, or forward a message from that user."),
            parse_mode=ParseMode.HTML)
    await db.add_admin(target, message.from_user.id, iso(utcnow()))
    await state.clear()
    await message.answer(
        R("{e:crown} <code>{u}</code> is now an admin. They can open /admin right away.")
        .format(u=target), reply_markup=kb.back_home(), parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("admin:rmadmin:"))
async def rmadmin(callback: CallbackQuery):
    if callback.from_user.id not in config.OWNER_IDS:
        return await callback.answer("Owners only.", show_alert=True)
    uid = int(callback.data.rsplit(":", 1)[1])
    await db.del_admin(uid)
    await callback.answer("Admin removed")
    rows = await db.list_admins()
    await callback.message.edit_reply_markup(reply_markup=kb.admins_panel(rows))


# ── background ──────────────────────────────────────────────────────────────
@router.chat_member()
async def member_update(event: ChatMemberUpdated, bot: Bot):
    username = (event.chat.username or "").lower()
    watched = False
    for gate in await required_gates():
        g_id = gate.get("chat_id") or (gate["target"] if isinstance(gate["target"], int) else 0)
        g_uname = (gate.get("username") or (gate["target"] if isinstance(gate["target"], str) else "")).lstrip("@").lower()
        if g_id and g_id == event.chat.id:
            watched = True
            break
        if g_uname and username and g_uname == username:
            watched = True
            break
    if not watched:
        return
    was = event.old_chat_member.status in {ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR,
                                          ChatMemberStatus.MEMBER} or (
        event.old_chat_member.status == ChatMemberStatus.RESTRICTED
        and bool(getattr(event.old_chat_member, "is_member", False)))
    now = event.new_chat_member.status in {ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR,
                                          ChatMemberStatus.MEMBER} or (
        event.new_chat_member.status == ChatMemberStatus.RESTRICTED
        and bool(getattr(event.new_chat_member, "is_member", False)))
    uid = event.new_chat_member.user.id
    if was and not now:
        await db.set_verified(uid, False)
        affected = await db.drop_votes_by_voter(uid)
        for row in affected:
            giveaway = await db.get_giveaway(row["giveaway_id"])
            if giveaway and giveaway["status"] == "active":
                await refresh_card(bot, row["giveaway_id"], row["participant_id"])
        if affected:
            log.info("removed %s votes after %s left %s", len(affected), uid, event.chat.id)
    elif not was and now:
        if await is_channel_member(bot, uid):
            await db.set_verified(uid, True)


async def expiry_worker(bot: Bot):
    while True:
        try:
            for row in await db.due_giveaways(iso(utcnow())):
                await close_giveaway(bot, row["id"])
        except asyncio.CancelledError:
            raise
        except Exception:                          # noqa: BLE001
            log.exception("expiry worker failed")
        await asyncio.sleep(20)


async def main():
    global bot_username
    if not config.BOT_TOKEN or config.BOT_TOKEN in {"PUT_YOUR_BOT_TOKEN_HERE", "mai nhi bataunga"}:
        raise RuntimeError("BOT_TOKEN is missing — set BOT_TOKEN in .env or environment")
    await db.init_db()
    bot = Bot(config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    me = await bot.get_me()
    bot_username = me.username
    log.info("%s running as @%s (hosted by %s)", config.BRAND, bot_username, config.HOST_NAME)

    await bot.set_my_commands([
        BotCommand(command="start", description=f"Open {config.BRAND}"),
        BotCommand(command="help", description="How it works"),
        BotCommand(command="admin", description="Admin control room"),
    ])
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    worker = asyncio.create_task(expiry_worker(bot))
    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query", "chat_member"])
    finally:
        worker.cancel()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
