"""自动化截图区域与锚点配置。"""

from __future__ import annotations


BASE_RESOLUTION = (1920, 1080)

SHOP_ANCHORS = {
    "merchant_menu": (170, 590),
    "purchase_normal_new": (145, 890),
    "purchase_normal_old": (260, 890),
    "purchase_deepnight_new": (375, 890),
    "purchase_deepnight_old": (490, 890),
}

SHOP_REGIONS = {
    "merchant_name": (135, 40, 330, 80),
    "relic_price": (155, 942, 195, 964),
    "currency": (480, 100, 595, 135),
    "shop_affixes": (666, 612, 1300, 786),
}

REPO_ANCHORS = {
    "first_relic": (975, 255),
}

REPO_REGIONS = {
    "ritual_title": (130, 30, 280, 90),
    "filter_title": (180, 55, 240, 99),
    "affixes": (910, 731, 1849, 983),
    "count": (1620, 730, 1675, 760),
}
