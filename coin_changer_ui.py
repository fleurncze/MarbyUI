"""800 x 480 Tkinter peso changer demo. No extra packages required.

Run fullscreen:  python coin_changer_ui.py
Run in a window: python coin_changer_ui.py --windowed

Exchange totals: PHP 5, 10, 20, 50 and 100.
Note inputs: PHP 20, 50 and 100. Coin inputs: PHP 1, 5, 10 and 20.
All payouts use PHP 1, 5, 10 and/or 20 coins; bills are never dispensed.
Coin inputs accumulate, so two PHP 5 coins can become one PHP 10 coin.
Customers can choose preset payouts or build their own exact combination.
Back keeps credit and draft selections. Dispensing needs explicit confirmation.
Currency pictures are embedded PNG thumbnails from the BSP's official site.
The app runs offline; no image folder or extra package is needed.

Insertion controls and dispensing are simulated, as in the original file.
Real acceptor, hopper and inventory handling must be connected separately.
"""

import math
import os
import subprocess
import sys
import time
import tkinter as tk
from collections import Counter
from dataclasses import dataclass, field
from tkinter import messagebox


CURRENCY = "₱"
BILLS = [20, 50, 100]
COINS = [20, 10, 5, 1]
EXCHANGE_AMOUNTS = [5, 10, 20, 50, 100]
MAX_CREDIT = max(EXCHANGE_AMOUNTS)
MIX_SHARES = {20: 40, 10: 30, 5: 20}  # Percentages; remainder is PHP 1.
FULLSCREEN = "--windowed" not in sys.argv
ALLOW_ESCAPE = True
ADMIN_TAPS = 5
COIN_DELAY_MS = 120
DONE_TIMEOUT_S = 8
WIDTH, HEIGHT = 800, 480

BG = "#EEF2F5"
SURFACE = "#FFFFFF"
TEXT = "#142B3C"
MUTED = "#627381"
BORDER = "#DCE4EB"
ACCENT = "#3D6D32"
ACCENT_DARK = "#2B5426"
TINT = "#F0F7E7"
HEADER = "#111F30"
HEADER_MUTED = "#A9BACA"
CTA = "#D2F263"
GOLD = "#9A691C"
DISABLED = "#E3E9EE"
FONT_FAMILY = "Segoe UI" if sys.platform == "win32" else "DejaVu Sans"

# BEGIN EMBEDDED CURRENCY PICTURES
# Official source: Bangko Sentral ng Pilipinas (BSP).
# https://www.bsp.gov.ph/Coins%20and%20Notes/Coins/NGCCS/NGCCoins.png
# https://www.bsp.gov.ph/SitePages/CoinsAndNotes/NewGenerationCurrencyBanknotes.aspx
# These are low-resolution display thumbnails, embedded for offline use.
CURRENCY_PICTURES = {
    "coin_20_84": (
        "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"
    ),
    "coin_20_64": (
        "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"
    ),
    "coin_20_44": (
        "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"
    ),
    "coin_20_32": (
        "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"
    ),
    "coin_10_84": (
        "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"
    ),
    "coin_10_64": (
        "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"
    ),
    "coin_10_44": (
        "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"
    ),
    "coin_10_32": (
        "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"
        "7px7FMb/Alv0yMggwxAyAAAAAElFTkSuQmCC"
    ),
    "coin_5_84": (
        "iVBORw0KGgoAAAANSUhEUgAAAFQAAABUCAYAAAAcaxDBAAA2KElEQVR42u29aZBk13Xn97v37blWZmVWVXdX71gb"
        "aDSJjZRAsEFxhqKoZTwjNWw5KM1E+IPDYYdnwmE5wnY4mtCMvIwj/MnSTHgsx0zIsoJoS0NSJEFSIgmQQ0EkSIAg"
        "gALQjV6rq2vNfXn7vf5wX2YXQIgSKTI0M+FCJKprf3neuef8z//8z0nB3/ybPHv2rHz22WdzIYTe9/l2peK2j62e"
        "qJdqtUC6rkym03h9fX20u7u7A2wBavbNZ8+etZ944gn11FNPqb/JJyP+pv7uuXPn5Llz53jyySfz2ScPHTp05pFH"
        "Hvk7rVb7w43F5vFmo9kolUqB67qWkJI8z0niOBwOB4Nup7s+GPSfv3Tp0me/8Y1vfAOYAmitxZNPPikvXLig9xv8"
        "30eDvqsRgSM/8zM/85Ejx459fPXQoQ/ce+99VrlawbFsNBqljE2klFpKS9i2jW1bACRJwltvXeLK5SuXtra3fv/F"
        "b3/7s2+88cZ3Zr/46aefti5cuMCFCxcUoP99Mag8e/asfO6557J9nyufPn36ww+cOfMrKysrv3DnXXc32u02Ukqy"
        "LMuVUkJKaYxnWUJKiZASIQSALoysbdtWnudZlmWJ0XDEq6++km9vb31t7bXXnv7KV77yhTiOr72LcfN/Fw0qzp07"
        "J59++mm1Py4eOXLksfc8+OCvHD92/BcPHzl88sjho1i2RZ6rPMsypBTSc12hNUzDkPFkTBTFZFmGEALbtimXS9Rr"
        "NWq1Gp7nkaYpWmvleZ52Xc+SUnDr1i0uvvnm4PqNq5976Tsvfer5559/BhjPruPcuXPWqVOn9E8i3oqfgBG1EGJ+"
        "oYvVxbtPP3T6l++9775fWllZed/xYycolUvkea7SJNUIpOd6QghBGIVsbm3T7/fxgwBLShzXwXVcpJSkaUqeGweL"
        "opBqtcaJ48eo1+tYlk2eZ1oIoTzPx/NcK0szrly5zNWr1y6/+spLf/ytb337Dy9evPhvZtemtZZPPvmk+HGGhB+L"
        "Qc+dO2e94ygdeP9j7/+lE8dO/sqxo8ceO3LsWNBsNslzRZ5lmUZL27alZVlEUUx/0GdzcwshJfVajaWlNo2FBSzL"
        "QgoJUiCFxLLE/JKnkym3trYYDAckccLh1VUOHjxArVYHNHmea9u2le/7wnVdORqNuHTxIpcuXXrhpRdf+tSXvvSF"
        "T8ZxfPkHPIe/EYOK8+fPi+LoiHvvvffD733ovf/psWMnzi4tLbXb7SWkyc5ZluXSti1pWzZREjMcDNja3sGyrOIY"
        "12m1FnEcB5UrcqUQAoSUSCFuvxcSIQWObeO6Lhrodrt0Ol0GgwFZlnHXXXfRbrUol0torclzpRzH0Z7nWY5js7Oz"
        "w7Vr1yavvvrK17/27LO/+/zzz38KyM6fPy+feuop/dfx1r+OQaXWWgsh9L333vu3HnzooU888MCZxw6urmJbFmma"
        "5XmeIaWUjuOILM3oDQb0uj2GoxELjTqLzSYLCwv4nodSan6cpbSQUgLMvdKyLERhUCnNZc+M7LguruOglGLj1i32"
        "9vYYjyeUy2VOHD9Gq9Um8H1ypdA6V47rac/zLbTm2tUrfO1rX3/hc5/91+e/+91XngHg/HnJjxhff1SDygLjWR/+"
        "8If/x0cefd9/c/qB0+S50mmaKSGQruMK0AxHY/r9Pt1+H9/3WFleobFQJwgC8lyhVI5SGikFtu2gtUJKiUZjW/bc"
        "wKCNdwpRJCgLpRS2bc8Na9sOWZays7vL1StX6Pf7eL4PCO66805WDqzQbrUKNJFrrbUKAl84jitfeOGbfPrTn/7n"
        "f/D7v/8bwLjw1h/aqNYP+wPnz5+Xzz33nAIWf+mX/oOnP/YLv/APjh8/oaIoVEop6fu+jONYbG5vcXPjFrt7e9Rq"
        "VRabDTzXwfM89vb22N7eJgojxpMxlrRIkpiNmzfRwGQ8xrJstra2yLKMbreDEIIkjk18VDk7Ozs0Gg12d3dJkoQb"
        "6+vEcYRl2YRhSK/fx7JdVlZWSOKYbrfL9175Hts7u4DA9z1Rq9VkksQiiiJ1/Phx/eCDDz5SLlc+9OfPP//F5557"
        "bnDu3DlrbW1N/yQNKp977jl18ODBwx/72Mc+/7Ff+IUPViqVLAxD6bqeVLni8pUr3NrcQkqLw6urHDm8ymJzkdFw"
        "wObWFnEUk+U54/GYJEm5tbFBu71EliXc2tgkzVOm05Bqtcru7i79fh/HdWkttrhy9QpSSvwgYP3GDaS0mEzGbG5t"
        "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"
    ),
    "coin_5_64": (
        "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAiW0lEQVR42u2baZCl11nff+e8292X3rfZR9KMRtLI"
        "ixa8zcgGAxEmOFYPNlQSTFyhSKCgioIvKTIWISGfqCSVuCiqnGAWQ3oM2IZ4k2VrtBmhkYWsmZY0S0/3zPTet+9+"
        "77udc/Lhfe+dkTGxZEzxJV3qqVHXdPd7nvM8/+f//z/PK/iH+xDz8/Nyfn6eU6dOqcEXy+XygbvuuuvInj17pguF"
        "QgkpZej73dXV1Y0rr7zy6vLa2muDf2uMkSc//nF59tFHFWD+QR7y+/0DT58+LY8dOyZuPTQw8aMPP/xPjx458sjE"
        "5OQDlUq1XCqVcF0XKSVaa/q9Pq1Ws7u7Wzt/6fLlzz3/3HOfeeWVVy4NfsDCwoJ15swZzpw5o7+fwRDfr0MD8tFH"
        "H41v+XLu5MmTD91+5MhH5mbn/sn+/fur5UoVy5IARghhhBBGSoklpZCWJWzbFlJKer0eK8vLwbVrK08tXbnyR5/+"
        "9Ke/BGzc8vtsQD/66KP6HzMAYn5+Xi4sLBghxPBBjh8/fv/xe+/9yb179/747Ozc4fGJCSzLAlBKKbrdruz1+qLv"
        "91FKI6TAsW0KhQKlYtFUyhWTy+e0lNKWlkVjd5crV6/uXFu++oVzLz7/v7/6pa9+DfDTEhEf//jHrUf/HiUivteD"
        "nzlzZpjiU1NTR9994sSPzc3t+cm5ubm3TU9P43kexhgdK2V835etZkt0uh2MgWq1ius4wxJQSqGNptFoYoBqpcz4"
        "2JipVqvadV1s27aMMWxubLC0tHTxyuUrf/6lxx/7s8WXXvrrW0vk1KlTb7o8xPcQsMEvqHzwgx98ZP/BQ49UK5WH"
        "9u7b5+ZyOTCgtY77fl+2Wm3Z7fUQAhzHYWJ8nEKhgCUthBQIIRBSYkkLy5IIIfD9gK3tbfx+HwSMjY0xPTVl8vm8"
        "dhxXOI4twyji8qVLbG5sPHv+5W995hOf+MSngc1BOb6Z0njDAZifn7fSW7cefvjhX37LW9/2SwcOHNiTLxQA0Nqo"
        "KAxEs9WW3V6XMIwoFouUSyWKxQK27WCMRmuNkBIpJJYlkVIAEimTv9u2jet5WFLSbDZZXV2j1W5TLBbYMzfH+Pi4"
        "zufzWkpp245Dp93h/Msvb379a1//L5/85O/+NhDe8qzfnwDc8gOn/9XHPvZ7Dzzw4PsLxSJaaxXHMb1eT9YbDRFF"
        "McYYxsdGyeXy2LaFZVkYA8ZopJTYtj38tVIKpJS4rps8jBBpoAxhGFAqlel02pw/f4Fuv4clLQr5PFPTU+zdu9eM"
        "VKvGdT1t2Zbd7XT44he++Mxv/aff/BfNZnPpjQbBeiMI/4lPfELv2bPn2M989KNfftd7TtxnWVYcRZGo1Xbl6tqa"
        "9INAFAoFpqenCP0+vW6XeqPO1tYW6+vr5HJZmo0ma2trBEGAlJLl5WXCMMJxHDY3N8jmctxYXUVKweraKoHv0263"
        "kVLS6XQpl0pMjI/hZjwuXLhAbacmrl2/IRzHlrlc1ji2q47fe3z/bYdv+9Clixcfe/LJJzfn5+etxcVF8/cJgDx7"
        "9qyuVqt7P/yRjzz+wA/8wIE4CuMoiu3llWsijmPm5maZnJggn8sjpaBWqxFFMblcHiEEuVwey7Lo+32U1kRhiOd5"
        "tNttqtUqURjR6XSH2RAEAVEUMTY2Rr3ewHFser0uaabhOC5CQhCGGK25dv069XpDTE1NSq11fMeRo5Xp2dkP/M2L"
        "3/zsN77xjd3Tp0/Ls2fP/p1BkN8F7QXgfPCffeiP7n/gwb1hEMZBENmXL19hdKTK4YMH8VyXKIpRKiYIAnLZHNVq"
        "BSkFmUyGvfv2EscxrutRLBSYmJig2+0xMjJKoVAkVjGzs7M4jksum2VmZpapqSlqtRqVSplsNotBYNsWxWKROI6I"
        "oxitNKVyiWqlzPXr13nssa/S6XbtbrcTv/eh9+75xV/6pT8F8seOHRP/r1K3vlvdv//97/+37/+RH/k5KWUchqG9"
        "dPUqe/fsoVqtEEZhguQCLMtiZ2cHy7LRWhPHMZlMBsd1wQikJXFdBwHEKsayLKrVCsVikVqtxvj4OFtb21SrFfr9"
        "PrbjYDsOWmsCPyBWMTLtGv1+H8dxcB2HOFYIKfD7fVZWrrFv3z6JMfHBg4dmpZDur/3ar345ZZHmzWSAWFhY0MDY"
        "vW9567/L5/Naa21dv3GD6ekpSsUiURQhxOu/XQhBu9NO0tMYjDFIITDCoLWi1WoRRhFGa4yBnZ0aOzs7yDR4URTR"
        "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"
        "SUVORK5CYII="
    ),
    "coin_5_44": (
        "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"
    ),
    "coin_5_32": (
        "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"
        "Et/H2iN9hOkAAAAASUVORK5CYII="
    ),
    "coin_1_84": (
        "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"
        "TkSuQmCC"
    ),
    "coin_1_64": (
        "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"
    ),
    "coin_1_44": (
        "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"
    ),
    "coin_1_32": (
        "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"
        "0xTdbg/1RgNKjb1CSmEwGGA4GKKctGmlNYTH7gcR0izD1tYWer0eBoMBvPdIRyNkaYrBYCCkiLIsu/rcs8/+VK2u"
        "rq4PhoN/rcSx5HkeFBGMMWhvbUEphc3NTbzxxhtgZlSrVdxx5AgOHTqEO+64Y1InCIpoDL5tt4cApdR1UOd5DhZB"
        "HMcYjYbB2UgGg/6/rK6uvq0A4NLFNx7zwVOWZqSNwdWNq0jTFMlUgn379iHPc1y4cAFra2t48623EELA+sYG3nzz"
        "LSSNxjimEw+wCLTWqNfH84IignMOURShPxhAa0NFWdDPL/z3VwHALC0tqZWVladvuXX/v83v3fextYsXg7FGz8zM"
        "AgCyLMOePXvAwmhvtXHp0qWJ6w2mphK0Ox3EUQQXRYAPYGZElSoIAlIW1jmICBQpiEiI41hfWlv73te/9rUfi4gy"
        "586dIwB8/rVXPz0zM7saxTE16nXJ85ycsyAirK2tYXp6Gs1mE3GlAgDo9Xrj3mAMhqMRhqMRqtXqJBMYAF0vQESE"
        "vMwlhIBur5c/v/rcAyJCy8vL0OfOnZNWq6UfeuihK7+wsH94++0Hj2d57gHooignc55Fv99HlucoigIhBGRZBmst"
        "AMDasZV5nsMHD+cigIAxJhWYWUajka/XG+aFF5//sye++c2njh49qk+ePMlqwnjC0tKSeewrX3nkpbMvPpY06jaE"
        "UAKQwWAIbQxcFMF7PyYNMq6bxlqACMwBURSjWqvBuWg8hikFpRTKspThcBiazWn78stn/+bx06cfXVpaMttsSW+P"
        "x88884y0Wi196oEHnjywcNvO+b17P8TCFEIIIqKqlQqGwyHKskSWFyiKAoTJlFSUkyGEQQC6vR7KsgAE3geva7W6"
        "evnls4888td/9eetVkufPHmSb0RMtmdE/tP777//9oOHH55qNiu9bleYOdRqNb3VblO324U1BswCpTWMNXDWQWmN"
        "KHJy7drbwTmnb56fp06nM3jt1VcffPz0lx6fDMDvomj0frzw+PHjxz78sd/8/M6dO3+nWq2iLEtstdvI0izMzc2h"
        "9B5pmsIagyiKUXqvtdGo1RtIRyNsbl799tNPf+8vfvT97796I5J6I3L6Lla7uPgHHz149Mg9U0njt5xzt0RxvA2u"
        "MdhAEBmX3CL4C71O77vnXzv7d60nnvjp/8WQ6f3o+dLSklpeXsaE2QJAcuJP7v+luBL9ioJaiONoBkTIyuLtEMLP"
        "s2H6H3/71dMvAOhPKJhaXl7GysoK30jG/wDIM/cCurQi7gAAAABJRU5ErkJggg=="
    ),
    "note_20_146": (
        "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"
        "B3Zlj1eIER2EAAAAAElFTkSuQmCC"
    ),
    "note_20_96": (
        "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"
    ),
    "note_50_146": (
        "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"
        "2QAAAABJRU5ErkJggg=="
    ),
    "note_50_96": (
        "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"
        "RK5CYII="
    ),
    "note_100_146": (
        "iVBORw0KGgoAAAANSUhEUgAAAJIAAABGCAYAAAAn1M23AABUsUlEQVR42u39Z5BtWXbfB/62Oe76mz7zZT5v6r16"
        "5au9RXcTrkGAhABChEDNUApAA81ovmiG1MyEJIbICI1CUsREcIYSR4aMAAWCAglRBNFAN8H2rrrLdLlXz7t876XP"
        "vP4et/eeD/tkVlWjge4CNN9wI15lZl1zzj1n7bXX+q//+i/hnHP8+ePPH3/GhwZHWRhM6e1JCMAJHA6cQ+D/RgDC"
        "gbOAASERCIRQYAVOOJxw5KMpQiuUVDhrcdYihAAhcGisc0glwIIE/1kAAn/Mwz8OzwVRvb966sjsnX+BO/yf4ug5"
        "hyMIApxwWOf8U85VbxHV9/HfzQHSvwRnf9ia+iMncXiScHgcIfyrTPWhEmx1bdzhmQpQUqGkxhiDNCCc8t9fOpyg"
        "er2rvv87Dmf9x1pZ3RJ7eHiHc9bfMymYTFKQCiElzlqkhCIvyYsMUxqctYRBTKfTAVXiEFBaUAFBFLzrmD+iIQnK"
        "ouTWW9uABSvRUuOwOGdxziFFdc+kQasY5wTSWaSWCOm/gFIB0mmyXo/J1j4ysygRIHRYXSCN1BqpvGFY69Ay8Ndf"
        "KZSSWGcQShzdYGdBa40RYJxDAlIInLGVBXjDsM7h7DsupJCEYUjSqCOUxFpbLQzp14EQSCkojTm6YOId9iEOjQ6B"
        "cxZbvcAbocNY619f/f1OgzJlicMc2bkVDpTAOv8eIfDvV1Cr1wjCAKsNlqI6d7+IhVXV68XRcWy1VpyzOGORTlI6"
        "h78y/jpkZUatFvHyS1e4v/6I5dVlikKQTgpeeukVrDWcO3uGLJ1STyI+8WMfxYgCJcGVJc3ZmJWTi4j36pEmoxH7"
        "OwcEKsE5g3PSn5bz3sc6vCEhEA4oFUKAlAIlKmtXoAgAQbS4RLc1S77TZ3QwwhiI4hhjHc5CqEN/ZOn/I6XEWIGQ"
        "AiVAKYUpDWEQEOiQcZqCFISBButwxqKVRgiBsQYp/UoWWmJMiar8nDWWbJITxSGB1jgH1gFCeuM1ggBZ3Tx/StbZ"
        "ypBAHnk4+bYhIXAIlKoMuTJmZ713s5UnBOs9Ifbw4oGUCGO9j1H+WHZqKfMSVVPoMMBikE4inEA65Q/gvEeyzqEE"
        "GOkQaKw1YEEhcEpTFiXCgiaAAs6dPs9XvvRt2q0OQVTjzq279A9GdLotuu0Z8niKxCIMaBGCNSinUU4fOfr3Ykw6"
        "nU4Z9gdEqgYl3sP4WwNCIp13g0oFKKn9duWMv5nOorTCGotUDhlIcltCrEhWl5DzKb3tHVwqiWuhv/FKYAFjDUoI"
        "AikJEDhh/cUWgiCJGE0mDCYjrHDUm02kdP6mSb9AhXBopxBK4nCY0ngvUxZEUYTC///c5ORlgdIBWoV+L3AGh6y2"
        "A3/JVOWlnLHea+Cg2o6kkH67d34BWee3EiklQoJxButtlNLkWOsQqjLO8tDLCqy11RbsDU0oKEyOzQxJPSaIAgId"
        "YKwF5Y3v6F44vxCFA2csSklKDFJKEBZb7c/aQqBDHj26z+LSHPVGDWsla2vL7O/vcfbMSV5//VVmZtq0WzWU9v5f"
        "OEEg/XUQ7968fzRDEtJvtsZkKBcghcVWrtQhiKMQUxQg/BZRb9ZwlKRZSqD8Flhv1zDGkk4zotCvyCklqhtw7vwZ"
        "Hl15gO1ZwiigtAalFRKJENLfJOHI8xKkRmuJEXAw7dNstWjV60fbK4CSgTdC6T1QaUsfR2i/DdrMgHYYYxBCIKQG"
        "B3mZY5xDBw4VHm6P6mhxUHkVqQ/jQarv7LwHswIp5Ntxi/SxmLM+JgGL864MoYQ3MgHS+ef8yYNxFiWl9yT4bVNZ"
        "QTHxBkUCQRxiBViBf68QCOsNRgBI4W+0qoyyioGEkEg0hS3Y6+1z/rELpNmULMuYmW3z+OWzgGJxeZEoCji2tkgY"
        "RxR5SqgkIjdHJvRetzbpvb0kijRhFKDDAB0odCCxlNy994D93gihLM1Ogzfeuspb12/R7DZxUhIkEd944WVu3b1H"
        "o9PAYRFSEIQl7W6A01OWnlgg6ASkaUoYhcRRRBCGxPUEFwlsJNGNBN1IINEYDTLSxPWYRzubJPXk7S2i8kBCgwol"
        "YaRRgUIGGqkVMvD/VKhQoUZqENoRJhKnMgw5RZnhlMNJw3AyQCgQmsoL8I5g13snKSpPLb2xCCUQWoDi6HepJVIJ"
        "dCAJAoVS/nz9QvW/a60JAu1/av9TK00QhARBhECTTXLGvQkUFi0FWimU8N5GKO+RnfRBudQSqb1RSyV8PCi8eWqt"
        "UEr5mMs6wsiHFFmWsrS0SBzHBEFU/QyOzFpIv2O8V4+k/ubf+L/+rclgTBTWEUIjKhcZRhGbW4/4L/7Lv88Xv/gK"
        "//avfYb/z9/9Tf7R//TP+PJXXmD34ICf/Isf5j/6G/8VX/j8N/jc732ZZivh2ecukec5jW5CVAuwRiFFQH22yXC7"
        "T5mXoDVRVEOFCpRDSoUMNUjB3v4eWZ4ThAEoSb1RY2PjEfOzs0jp3XachOR5SpJESKUwxqIqL6AUSCVRSiGFwAqo"
        "NRp+yUiHU1U8heOf/+7/CgKOHz9OXhQopfzqF/6mCOnjFJ/5OJSUVbZ4GF9LED5gd7bKtpzzwf3Rz9LHZ9Z672Z9"
        "QlCWJaa0VZIAxjicETgnwDjyNKdwOc45wihC4LdSpDdcISSi8oCH2ZB1BidAB5o8K7n21k2OLa+QxAnbm1vcv/uA"
        "M2fP88brb9KdmeGll17my1/+Ks8//zRxHCCAsBERNUJclTG7dxjVn+SlJHgrV1oglL/QKpSUZca5c2f4T//W3wCh"
        "ePhgyG//0y/w3/6D/5K/99/9bf7gc9/in/zWv+KlV+7yO7//d/lP/rP/C3/v//2PyYoMHfhsx98UhXBQZCVKQRho"
        "xqMRk8kYW1q0DpBKIaWkLHPiKObEieMsLC4iJeR5hnUG4wxBGHEw2OMb3/wWM8sdvvfaK+zsbtNs1RFSIBSoypuq"
        "QKKjEBB841vfYHN3i6Ae8e3vfot2p8nXvv5larWIZ599BmMKtBbVSgeUD5SFBCWlTywCidAgg8oTSVEtOgFKIkOF"
        "0pIgVIRRQBQHxLEmjmPCMCAMQ3SgiaKIMAwJw5AoDEnihDiOiWJNUBOEdUnYCggaPm0os4x0MkFIKi9TbZkKlJYI"
        "5eM2qaUPGbQgCCUryyv0egOKzOAsjIZj8rzk6rVrnDx1kiRJmE5yXn/tKoPBgCQJkFriqu1T/rFm4/4IAgKgnRMI"
        "tN/KpEWrAIfASoHSimk2IKlLrr31kKXl48zMzIAtuXDuBF/6wst84INPMp1mrKzViKOIjUe7zMzVydMSFymEcERK"
        "g01JccydmSUcZ4wfjjg4OADlaLXbBCpkMpnSaNQpyhRnDXMzM4zHY8q8QCpNTsG3Xn0R6xT3dzb59qtv8tefeYLd"
        "0R61KCEIJZPxmDAMEAZKJ6g1E6JazLU71zlIB6ydOM2d2/eYjMf89M/+NEIZDnb36bS6FGV5hEcFSuFsiUBSJXtV"
        "rOMDZ/9TVp4BjCmqsEp6DxloHIJhf0C9nqCVoixLytzHblL44NuWHhiywr6NeQHGGJRSlMYxmYzRwZSkmVBr1DhK"
        "LZ3PHoUEJQQFJUkUcPvWPb76xddIopgrV65iSu8FbWnp7e4zHY3JSsvBYEwU15HVFigl6LAKHYxDIirP9E7bsW/H"
        "bU4dwR66ymtxmGqXdIDyX0pagkihAzx2JGNqiSIbGQZ7PdqdOfo7+8QigMIwHIxRQYDSMYPpAVaXOCeZbcwiSkkS"
        "S9pzCtFuIQfSp7wK8qJAa00UJrQ7LcIITAmB0ighKPOCVqfOK2++yskzZ3nj6jX2hj0WTpzgxatXuX71NovLi+TT"
        "jDLPyacZRZby45/6COfmjxHogvGgz56U3HuwRdjQPPH803z1pVfY3Nyk1U7YebTNybUT7G7ssrqwzMc/8iGskwgr"
        "EFUK7oE9WeEIh4CmoYqqfdaGQcQhe70hb755gxvXr/HMU5e4fPkCOomwpqjgE4V0h0ioD6yNO/xcQSC8McUyqDK+"
        "kiIrGZRD6rWYKAqx0sc0roIwnFPEYcArr7zGlWu3aHVbDMdjjAVTKkxRYEpDOtlhkqXkpkRbU4UFFazjJErIo4RD"
        "iO8DApzy/95pXaJCtpE+U3DOIfAfogOBThQ6VGSZ5eKl42xtr3Pn6jrNOOLn/+JP0ZmZZXf/gL2NXUxq+PVf/Wu4"
        "3DDY7VNmGW5QUjjJhoIgd0z2Sl7+gzfY3d3npW9+DycgLQvCKMZSMp1MmZlpYW0OTlXXWLBzsE89bNIJm3zkw+8n"
        "eDTBdsaEWxlb6/c43l6hd71HFEXUgjrWxCjd5d5rm/Qfjti4uU+sY9gzLIoObuJY//Y9lI6JBzHPXXyKYWsfEQoW"
        "W3McO7bCMJ1WrgHvebyfRlhbZXwWKcC5skKWjbd+4WOz6c4Oxxo5s5eWiNSY8fY9Ws02lCUGbzgWkFpVh3E4UWWG"
        "FbyAgFKICkSVHnjFMh2PiJOw8g/2CFg3RcHoQHH62Bo8lRBq7aEIJEIonARLWW3NmjJ31EJNHCTs7x6As4wejen3"
        "eodOpwJc5ds4mq2yVecI45CF47MgJNo5h1aKzmy7Cvw8fmJLSxAHJLWQ8XTEuceX+ORnLvEH//Rf8dd+5ef46Iee"
        "QKgQKc8w7g2oqZDP/oXnGY7HFBOHdCHTiUQ4MDKjMBBHDSQJVx/c43O//3lUGOCEX+BRGDEaDSmFwBqIoxAlIM9T"
        "GmGDuWSZ4wtr9E/3WJs7yf76lJlwFh0FYKHdWvCX1QLa585lz7C5t08nnMEYA8YQiTrOhj5gRdCZbbN5o8fa6RWO"
        "nZrFKcMwSymcR/alkCicj6OUq0BbB8YhtENJj6uVRQHG+PDUwnK7hpJNEAqnFIWFIk2xVfBunMNgEVb6NF9JkNIH"
        "3UclIv/ZSO2xL+eDfaEEk9G4wrFkhYX5YHw6Tjm5uMrZhVO+HCVCH/MoH4gfZr8SD0EUSIbplDTPq4VrKdMSYyyB"
        "iHClASeReJC0kAarCkwBSVsghPMb/vb2tuv3+5w9e5aj+q3jKFieTFL2dgccX5vnzp0HZI8yVubmmBYZUvgSh1QC"
        "gaE0/mRdFT8oPF5kcT6jkI5avc69Ow/4z//Of8Hedp8wjlBaU+YF83PzICVFYZhORmTjnEa7xkIxgzSC5mqdj3/8"
        "Y5SFI1CKsvCuXUmJsaVPufExizXGr3CtKAsfb4RBgDEOYyWlswglfLrvHONpwOyy5PLTx2gvzmECRz4tCLRGOl8+"
        "KGxJoKpyhPULrihSpLAoHyhhhSMUCls6xuMh9VoTozyIiRSoIGQymRAEmnocU2Q5QvjzKWxJpBOU0jhnMbYgCDRp"
        "VuKEQzoIVMi0yKjHMaPxmNKW1OIaAsdwOMIZcKUvdUkp30aoKyNyVQympKCqYYBWHgOrbr+sIAtTmqNaq6zup8Xg"
        "tMGUEEYhM2cTnNTod5Uk31l4ct7SG42ERqMG1qG0L0vcvrLhcRfwF/TQyVofJxwCjc69XRh1zlWljoj1Bw8RVjM/"
        "v8BgPGQ8GLG0tMTKwrIP8ozANmHY64PVJFEN5yyijFBCecTZ+SxGSl9e0SLEWkMQ+kxJKUlpHEUpyJUvVE7T0tfq"
        "hCWOYkprKoBQ02qEbNzb46tffpVnP3iJZCZj7dQcvX4fYUO67Sb1boPB3gGDfh8VBCS1JvNLs4z2RhTDjDiENCmQ"
        "Q41wktWnV7n6zau0jy1AabFFyt2bt3nux97HYHvAF//gG5x5+jRpP6fZajC/3OWt69fpr4+IOhHdhTaPNnY5c+4E"
        "02xEJGN2t/qcvnScf/E7X+EDn77MzLEu699dZ3S/hw60X8LCVw487uQzSyli7w2V8p7pEMmvnIf3g+4wkffQhhNI"
        "5QvLh7C6j+8ktnA0WiGds2sIJ99tSN9vVIeGZW31AVqw/XCX0ZspURz6KnJ1ElEQorXGOUdRFJWnkpWFQ1EayrIk"
        "DBWP9jZ4sL5JHIeoUINztJstXJXFmELRqc/Qilvsbh1grSPNchLbIJAhTpVUDhWtJUIKjLG0mx2f4r55m71+n9wW"
        "9Pt9hsM+NjNY6ciLHIfj5MnTfOxjnyAONFmaESchk/UxD+8/JJ8W7O7s8hd/8QPsDHaQoQf4PvETH+fKG+sMej2k"
        "VNTaET95+lPcfvMOd65s8ujRFr/6f/9F/uX/8AXCpuTsJx/jreu3ya9cpdtewKiStbV5EIpbN+/z3a/f4ObmJmas"
        "uPTkWRZOzPCvP/8KKnUclGNOnTrOzWt3+PIffpv3Pfcc48EBb129wc/WfporV67zmV/6IM24yc6VB2y9tkncaCMr"
        "doNQfos/BBkh8Fto5ZWUVFhrqnsmKhhGUhSZ3+BsidYBReYhB+f3FZzzlQlbGJIVzcnPrCIcf7whvQtsqizXOouW"
        "GhUHEAlMAKFWBFHI1Xu3uHr1KgcHPYq8AFeQhBEzzSVOrJ1i7dgq9WbiPVaoEM4RhiHgUFGMQDBJp8QyYbG7hLPQ"
        "Hx4QhAGmgu6n2ZjCWkpn0crjJtZZaklCFIa89r3X+PYLLzFJc7pzc9RbCSKExlyLWlQjjAKcsQwGI+7eX+fhb/02"
        "zz//fp56+glKY5FKUqvHNOoJaS9h61rJm7d2+Xf+Tz/N7t4e3/vWVYSJ0SqitCX9gxFXr9xgMBpTUjC7OMt3v/oG"
        "UgccHAzZvtpneeUkjzbu8/DhBsdOrvKVL7/GzsaEIIo5e+kCH/7M0/z2P/5dHq7vc/2tTaKwRl70+Lf/rV/gq1/7"
        "DmunF8nHkhe+9T3WVlYwRYItJd3FFp//F1/nZ3/pL4By6JomSJTPwJXEOluBsgEW/IITGusgCAKsdZTWUpQFjVaD"
        "za1tRoMhjz/2GDeu3eP++h0uPn6Jzkyb0uQo4Tzi4A4L7aCURuChA/2jQuBOVKmpkeC864wROAX/39/6B3zvyuuE"
        "YY049phJDcFye4lcCW5cvcPtm/d44okLnDp/EiEkjaSOLQ21KKbb6mKnfvsTcUgqc4o8xxoIohBnC5yAuBYT6JAg"
        "DjG2JAw0tUadvb19tvZ2uHLnOmEn5MTKCRDOY1LWooOIgpI4jJAWOjNd2u0OOzu7fPVrX2Yw2uejH/8kq8fXiBtN"
        "ijSnmSRYUXD5sXPcfmWPvJxwMDrgQx/7IOsbDyhcQVwPeON7t1lZOMaxtTN02h1u3V3n9OVnGUwmvHVzj0I2OHXq"
        "WXrdPlla4oo2rdYq40mfy09dor9nePLJp3lw/4A3v9Pn9OmTRIGkzBWzsyewLmN5YZnbt2+wNLfIs+9/P6+/fIMw"
        "nOfMqQs8utPDjATahWAKwiRiYgxCaUorUEoThQHjcZ8iL6nVGrx19QbnL1xk49EGWzvbnL1wnr2dHqIU3L15l2Ev"
        "49knn+PGrevMLcyQZYXfoXCeDyU9LKLQR1y1dxmSq/gwfxIOboTByRLjDDO1Bv/9b/8mX/nui3RbTSbpgHpT00wS"
        "VqJFWmIGMwWkxTnBq6+8SqtTI1SaUjriKKTdaRMISSeZIVY1Xzpwlsxk6EhhbMGkTJGBr6kFcUBhU7RSSK345re/"
        "yf31dWQUUl+cYWW2zRNPnmFr6yFpWpCnDh2G6CBga2sTW0IgNc35hM7CCVZPLHDj+lXW//EDPvPjP8nu7gZxFFNv"
        "1yiLnL3eJnu7WzSiiDAyvP6t77J04hhBvc54OmK1u0bhs37u3XtAqxazeW+dOInZ39kDBPcP+swvdHE2YvXYCm+8"
        "fs0D4mITJSWNVky320SqkiwTHOz1WX/4CCdCglBwZzAhVAGDwZCNrU2iWDGdpKRpykz3JHdjSR4bXOS4dvsmy8vH"
        "6O336Xa6ZFmKlAFZWTLNctTggLiTsL55jzTPOH/xLLfv3mJ5aZV2q83N628RJ20anQQjcozLkQEVSYYKkjCUWKwO"
        "K0xJ/NGs7Y8zJIfj7r27lLslTVdHBZKt7X3+/V//jyhdRHM24Ff/vV/iqScu0rvVoxwptJHY0tDv97l96w6bm9ss"
        "Lixw9vFz/P3/9beQRcFzzzzFyuoKc50ZFILSlZRAfzCgXmtQTAq+9+Jr7G3tsXZ8mc/81KcwtqDZaPP5L/wrbty6"
        "waXHL5J0GoxNysWnLnHuwhpJTR3RNYx1CBQP1h+xubnLbHeena1dNh9sIEpLrCPe/N5NjHH80l/9JUoLzjhMUSJw"
        "PgsqMihzTFEgtebYhRMsnz+GqClcmWGMX1xWWGrNJnmRUxqLCkKKoiQKQ5CQZznOCrTUWOs/PxAKiaAszVHhNa7V"
        "GI2nWANhrHGuQBlQTnjGgoPCGIqioJgUOCxxKPnc7/0eTz75FK+++hrLi4uevZGVJEGb0pQ4YZnmE+a7c4z7I8aT"
        "KXOzcwyGQ/I85eTp49y9ewfrLGEQ8aEPfJBpNqmYCwYjHU46rIEoDlk4Nwfa/ehb2yFzMKnXiKKAWhJxff02k3RK"
        "koT8p3/nP+TDH3qC/e0e+WZGaQxaeA7PwuISy8sNvvD732Q8yihGU+qFZKGzzPGVNWaPLYC0QIHIBYHRhFqjJFBT"
        "nL10nOMnF8iKDBE65roL3L+3zn5vj8efuISONMO0z6Vnz3Lh0jGk8oVLUdWgwGFNyWOPn+DM+VVGgzHdmRpRFHL3"
        "+g1G04wzF85y7coNvvfyi3z6Jz7NYDRCuBhnoMwzzNQgSoGIQ8w05dV/8SXuz9ZpPnWc+NgMKEcUBaRZxqNXXmGm"
        "08HkJfkkJ1AJWgcYkyMkNOot9vZ6zMx2maQT0izFWsvc3Cyj6ZQkiTk46FOrN3DWMUiHhDpElRZbFERJwnAw5My5"
        "MywvL1LGIVJLjMv49C/+JKPBlI+ufZoo0EwGfVRFuR0MB6ydOMZrb77GyvkFsnGbzc0tLj1xgfX1h/R7e5x8ZpXG"
        "WsTdO3d54onLWF2gbQBCoT1vGIXwW1voi0XG2R/dkATCQwLaQaIwgaA1P8M0m3D6xBnOn7vINMupNRICDUYalI5x"
        "RiBEwt7uNkJoTOlxopXWPLUo5sYb1xFZyfLpBWxLU4gSZQJkHJCaDCkEJSUyURxbXeT8k6fY2Rry6uuv012YIYgD"
        "xpMxF597jIuXz1CKknqtSRgGHFJkwKKVp8GCJYwDpAw4dWaVRk1z58Y9th72Oba6zN7uDrt7W8zMzZPnOabwlMYk"
        "aFKmEyhKzFTQadVxE8P2l68SL7ToXjpOdG6ZEAhtiMwkzgiUChDCsztrQURpCrQSIAx5nqGUotlokheG0giU0MRB"
        "5OGCLKXZalBm2vOpcZSiIJQxURAjtCBMFGbiPY1UgmbUYqY9izWFLy3VE0pToLRgYblLaQwfeN/zTKdT4iRhdnGO"
        "8XTE4uo8y8cXGE7GtOZm+MDaMSaTMYWzCOkQwiPvwnkU3jpLoEIQEZ4F9V48Er7qHAYRxsDps6f4hX/jL2F6mt/7"
        "zT/k+Q+eZ/Fk1++mQlKWlnSScevRHW7duEmt3mZrY0B3dp5OexalJVkxZffBDvkoZeWxkyTNOuNxn7JIieKIPM2o"
        "1RKmaYYRoBuaL//ON8jKgu5sG+cs88sLrKwugdQksaZerxOGAXlpMK5ECYVwAUoalHJYM8VpQxAJmp06p86eRNgt"
        "RgdjxsM+e7u7rJ06hhsZwkjhigBZeLBVhiXogPn5JtrlaGuZpimTjW2ilmbmmbNceHINhOd4laXBidLjataj8MbC"
        "49EFX+iVvgSjnKIs377WT77/NKbqi1DKA8QidDhXku89pCgm6BBckFJv1SiyArTBOihsARhE4AmhoVSerYCgVvGS"
        "GrWmp7lYS5LEmNJDL2EQIxHkWUaogyOcSUr5dpOGcxhKpJJHodB7MiScQ4YSFSlcYdCB4t//m/8u/+N//Y+589o6"
        "W3cf0Zqv07/fh1SiI401JUI4Go0m127c5JmnP8DM3Kyn3TqJsY5ap4MOA269eYOFtWUWjy3QqbfoD3ukRYFznpXQ"
        "nG3zaHuLna1dujMzZOmEJInRUURQC47AMlFRVIXwFWzrrC8+VvSLMAooytIT2pREBYr5pQ7ZNCNpNdjvH+C0Q0US"
        "6apUGoUtPCWmlIZJWZCUJYN0F31xlebJcyS2j52+yE5xgrKURFIxPz+HKRyZquiwzoI12FLRu79FPsqwxuEiwcqF"
        "k77UIhzZ1JeuANLMEGrB7Vf+JS9efYPf+NYIlw1YCeb4lY9rLj3/ARbO/ByjtEQKhzKOQwhbSUEQxFUjg6ev4XzM"
        "6wsfyjcTANYaTGkRQqKDoCpxmLcbHw6Lt65iPsgKEX+vhuTwsHjciI8IWYunZvjl//PP8fu/8a/Z399DFBGysJSl"
        "odS+rJ3nJXv72zz9vqf4ub/8Ge7dvk+jHXvjiJq0ZjrESYgYCh6u32dnd5Nmq06jXqNeqzNOM8IkJEoSrIBmvY6W"
        "EhEnKOF5R047rCsQIqIoC4QKsc5grSeWFWUVOLtqdTlfyY/jiMkoI6qHWF0yzsYMpjVG6YTpcIpwgmyYUQxTyCyu"
        "VGTjgmLqUGbK8ke6nP7IEzSSmGG6z2gEi3NLBCLmwb0NtkZ9ji0u4SYlNgCrFM74cs0L33mdvWsPUFITHG9w+qnz"
        "5BXA6m/VYbKc8tV/+V8xO7nK+u4aV3vz/Oxjy/yzF4f8VAG3X/iHbBzs8uyH/vdkNkPaqKK62CNvcmhIQhymTiCq"
        "TMw6U1UiFKakAnorQxL2Xc0yvgQl3i6A8KcxpCOyvP8UKQVFaThxfpX/w9/+a7z60ss8fPmA+3sPGJopaGi2EtaO"
        "n+LsY6eZX54hKw4QYcE0nyCQdGqzZHlKFGuSesxSskh/2Kc36IMThPUYK2A46jNDm/FoQhSERxmmdYZpOqK0BY4Q"
        "Zy1lmWNt4akRsmJOVivHOl/KieKYshx5b6V8+t7tdlm/s+GLnVIiAqAQhGGAVQUoz3SMQoU0KW4f6slxwvRL7A2O"
        "M3YtukHBzkZOM3iDjov4zu8+Qn/8cRbPH0cB1pRHnLAbb11j+4XbhFFIUi4cMQ2F8AmCMxalNS9/8Z+QPXqJ1fd9"
        "mPXXJ5ydN/zG1wp+7LkWrz0c8wt/+QP8y8/9Lotz51g593GMMwgrKjbB2zigqChD4rD3rjK3wwjHOQHat23xjlao"
        "70/k39Vnx59ia7NUvUnVNuesQ2nJcJpy46tXuX9/AzMMkDVJQ4UQKr/laI0TkJVZRXktmVtoooOEaWqQgSWuBygZ"
        "UbgcGQmSep3RKGUwHGGUoTvXIWkkKK3Isox6rY5Qgmk6QrrcF8iFQyoPnFoHzpQIK4/ow28T9SWyahZAec6NkoIg"
        "jBBCkGUTijJHSYmOIooyQ2vlmwCcgaJAxQorDP1HO4w/dondqWL+4PcI+1eIGj+DEefBZYjv3eD69XV2P/AYZz72"
        "NPFCi7LqF2w12rRnjmGVJG02jm6eL3MY0JIi2+DL3/4yf/UDF4jiea5t3idLC379sxH/yzd6dM+dQDZiltaW+L3P"
        "/w6/dvZ5hI2OKMOeAVL9/kd6jOQP2HPsOzyRrNq3fgi++J5jpHcalXNIKRhsDvntv/c5+re3qLfbqDDkYGcfW1pE"
        "rFlurmCl5N7DDdbCZU6fWkOiOXHuJONRzqyKKMscQ8ni0jL1dr1iEVgm+YjSGIwQpFlKu9MgK3LyIiMxNZwraTTr"
        "XH7uEt1uFyUVcVIjjkNfzBUSVzhK4/nUZVlgrSOIA3CGUPumzCLLSaKEVrOJkpdIagnd2Sb5tMQax3Q6ppSWqiGF"
        "1kwHXQuRzT5feTDh3/rPr/ErH27zn1wu6U0C4niJ/HdeYby9SZzEJLrN9Jv3+O7VLVY/+hTHnz+LqAvOXX6McdzA"
        "4AjOzL5d4zzii0k2Nu7z8kaDXwklggm/9gvnmTOaT324zsmZHS49dhJT7NBdfga30cOke8hozbM3+D7jea+tIe/h"
        "9X9qQxJCgJX84T/8Ort390hmIvKyT7uzzKI8TilyTj1xklock6YpRZFz/8EG9VbM7PwMF565zKDfYzIe+kp9aeks"
        "NlCRxsgAlKMmAsI49AZRgkoCNra2KU2ODkKGWY/5uQ7Lq4uESYgUkkjH5GmBKUuKoiAIA+pJzXOAyvIo5ZZCsrfX"
        "ZzgcUavXiXREIBWD/SFx0iCOI38rleds7xb7kBmQoOoaXQuJOhG9rQE39zX/4Ltj/vozn2XlkqP34gB9/zaz3Tpb"
        "NMhGkmhmhlg4el+7wfjuNvPPn+TZz36UUoHNC7T0DQlH2ZHzZLJiPOEbdyRfuVXwi0sTfv7ycayYYzpV/Lsf66Bq"
        "KRSSO5M2eaMNmUAkDmcMUqjDJsC32+Hdnxy6/Bl6//90DyklOw/3eXRvk3qjSdwVfPZ/91mWTywxvJcSiBCpFZPB"
        "mDzNuX7lGtffuM1gd5dP/cRH6c52iBoB02mIVhIpAxqNJmiBUY6szJEy8i0+SnqsIg6YNR0WlxfY3+5Rm9Esn1ii"
        "pCRwEdNRyuuvvMXm5jbCSuqNCBVYjh8/zuz8zFGRsigM167e5MG9h6yuHqeW5EgGdJptNjZ3GY8fsHZuhdxkKKsJ"
        "45Bmt8ZwZ0yZVdoIuaUsSiaB4Xg+RhwIfvm/eZn//v1nWLj1daKVHDNpM9OdZ/Ngm3KqcEoikwizM+LOF77H/u1N"
        "Vp9/jGS5caRB8P3941HsODUX8v/8gkTZPT77gQllPSdRMa73Jvs7U/7Rqym/+1bOszOGLPgAMRbhBAiLqzQaXCXh"
        "IN0PNyBXhS1HRv3/T0MCGI8HZDYjSiQ//6s/zdzqAibLmOYjcjQhIZmZorTj9Pk1Hly/z/69bdbvr7N6NqbIy6oi"
        "7Wkqxlmk0BhXetykagnPTFn1d4VEQcjZC6d5Yf97tNttujMdjPVNh1mWksSKj374ObqdFsPhiPUHj9jZ2kUqyczc"
        "LEVecOvODZwt+Es//1miIMKUhptXb3D37j3COEAFvoo+HU5BCOIg8VRVII5DwkCjQ01zqcPcWBBe/wp/ZbjNP5k+"
        "wfCNdU6entDf2qKeHqNxbpEOgsnmyOsfqABX10RaMHk45OrgTeaeOMHqmVlUPXi7/afiiM8unuFTp8f83rUGf/vz"
        "bXql5mc+nJKE2/zGC4/4e18s2J7GnG1tsLCmCWrHMKVAi0NWufiR2oneGTwLJX5oTPS/qSG1Oy0KCuqmhbZhxWKP"
        "aM3MUZa+RFKzglhpXnjrBQplcCJARjFxFGHyDIREhR4DEso3NwpT+p5851BKUCJxQpFOM3r7Ay48fhYjSoxxWIwX"
        "oKi6LpbmjrH1cJdvfuUl+v0+7dkmURIQJjErK8cosoLNR1ucPHma9fuP2Hq0ye1bdzh94gRJrcZokFFv1MA4Ah2C"
        "cIxGA0zqkArydII1MVEUEzRrPPlwQL27xD/N5xm3ukQ1TXQzwL4xJr0QUh6v0WquMH70FkJElMaiSyiwuCggQJHd"
        "67NvoHaiSb1b88E2AutKksYJPvn087x160v0Z5dYOlPSmCsRk5KPXND8t98OuTBTciZ/wM/95L+HENLrAqjDDg9x"
        "1Dsr32FN7/RC7zQaj7+925B+FKPS7zX68toSviW6M9fl3BOn+NJvfp2////Y4H0//jRzJ1eoNxq0ag2yEva2elx5"
        "9Qab+4+YqXXYHOwR1WI2NjeoJwlRHHsCe5WCOywIi5J+ZRzGDTrQlIUly3NsMWBxeYGDYZ+iLHxflxIUWcaLL7yI"
        "EJIoSJhmI84tnWI0GrG4uEgYhQSZrjKzjG5nhqIoWV5eYjKdElnfTTw7P4MMJHEcUxYlShVY4VFo380rKaYZe7M1"
        "9CL8Z6fm+Vqp2RlPmQrHfneNrcWI6VyHkysd3MO7mFCipU/Js7JABiFK+qbEpBmjgoD+7oDecMjCwixhGHgmojF8"
        "9Kd+nnsPbvDPXr3JYLTE1kZBsfOQg4MxZ1pjegdb/NIvfYyzj3+KSTklkiHW6SOpnXfgyT/UKH6o0bjv2wrle07/"
        "DYgCrQJPbZX+rT/zV36c619+k42be3x+6+u0FrrMLnR57OlzEPqO0qlJScIWN167w0d+4v1EscIgGAwP0FNFvdMg"
        "CmNkpBAKdKF8Ta86SVH1uutAkzRqxGHC3Tt3K3J81X8voN1tcOmpCywdW8GYkgv7pxBoVuQiSgmm0ynWOOr1Gmtr"
        "K7RabaLoPHmes7uzRzZNwQrC2DczptMMi/NMQVF6Il0Q4qTEBZrRg33iZpf6+zr8O2GCmpZENeh3NPq5AjuaMry6"
        "S23qCGcT8u0xMqjhZIAwjrD6blEcILVAWsizksk49R42hEAHOD3Dv/nr/0eWvvZ1Nm5P+frOkO9cucXDB3ucu7zA"
        "3/jlv8JTH/4JUpMQSosVBoGptADE27Yk+LM/xLuNzbgc3hOxzfmu2FdefJNsewzGcPz8MS5cushP/+xP8qXPfQsR"
        "KKwUDPYnPLjzkIXVLlYbWguS+29t8+RHLvLcc89x6/VrnP3oWVxaMBqPGI0nDCcjlo8teZUTJSv8x4OeVCwCpIcd"
        "ptMJe3s7zMzOHMnbhGFAIAVnzp0hzXImaYbUAWVesLi4zHiaUZQl9Xqd2dk50jSl2WqiA0Ve4nvyVY2dnQMWtMQ4"
        "S2ntkSiWQPk+vyDwx3SW8CAju3ufMi9Iy5xgrcPc+SX0Vkr2natED/u4y6ewx2dotVv0dsc4LbBC0EjqvPnGmxQy"
        "5wyXCGdqLK6toIREOYkxUKaGnJI4itHqOJ/++C9j3rfLoH/Ahz76BO3YMn/sAgSLpOUEJQ57iOT3iYL92S3oEEva"
        "fbDLi198BSkltbka7//x55DvxZBAkecF84stkuUlRAFhPaZQkkY74MPvewaVaNJGxmAyxIiC+eOzdLpt2p0WP/Pz"
        "HcaDKQe3+yyeW6DX76GdIHGKuNVmYjJGwwGdmS5aa/KieJfIlFKe7RdozaA/8LUiJSmKHOG8HpJWAaW1SK1pd9oU"
        "tRpKCBrNFoXrY61BBYqZ2Q6T8YRx1dKjpKTZamCdZXevTxBptFKEke+tmxY5OogoyxQoPddZhgglKJwlHGdMJiPS"
        "YZ+ZwlBIB9OcrMio7w+QyzOEUUIZB5iyREpFECm+9u2vEMQBLpGoVsLC6jGck7ijpjewxqEST/AzWUmQzNFN5ugu"
        "nQVKChcg8pJQaUwFOh6JqSDe5Ym8rE5VMqm8ymG1Qoi3GwF+0PbmSyyOuBlz+smTSCG9MEXVIqXfi08LdMTdjfvY"
        "XYkwgoWTCxxsDnjtq1fo3T+g0a5hyFleWeLxDzxORkY5tmwe7DLYHBEkIbW5gE6nzXDQZ/3OPRq1JippkDRqhEKw"
        "tbVFa6ZLlMSUtkBISah9XBPqCK0OW6VAV80Fh71kQkl0oJBorDEEtYBAa9IiY3d3m3q9jqnXCaOQ8WhMmqbMz88T"
        "RRH9fp+9/V3K0tBoJswuNskfDUlHBYIA41K0lpUQmSAMQko3QQOiFpJPLePxkLhWo3ClvzlaMekNqGUlQaNBfXaG"
        "g/0ecRiR5RnzC7McP3GCRq3GwXDiG/wC6bWbjI8NDY6vf+VljIFPfOY5jCl87IREi8CLZYX+NkpzKC0ojxTjvv9R"
        "liVa6/eU2r8zCJ+MJty8csvTX9ptVs6sgizfAx9JCPI85/n3v4/uTMdLpPRS/l+/9t/w1suPKCdjLIYTp+fRMuDR"
        "577GsBjRaDbZ29phdDDm4ofPcf79j3GhHRG0E7qrC+zcXCfOUuTiDEG7wcLyIoPRiCzPmVuc8ZX8slL3wBBU8cTF"
        "S48x6A8oihxT4UNHbcZSHCW+29vbbG/vMNOdpd3uUqsnjIchQaDJsimD4ZDZIMA6y3Q4Js9TwkSjE8Wx48sM9sds"
        "PNjH2JKisJg0JwhCrLEYaxinKTU0Dx5tESea/miIDBVZlpNPJqRlgdjZZV6H1KKIPpYyn2Jdwfnz5wliRdobMy1S"
        "UOodXkMRas3tBzfp9bc4ceIMGw93WDk+j7OW4X6fWzducfHxizhXEoQBUZL4uMUe8sfcu6ogQoiK+G9/pLLHDwrC"
        "F44t8NO//JOHNTOM8VjVe8ralFIYU74jfC8JpKaWaDITk5kUJ2rsD3NECFkOOiiZDB0PX++xe+8F1td3ufjcRcoi"
        "pb00i5YaM8ioJQkqCYmikPk4pt8fsLW1TZLE1OIaOtAUtiSpx7S7TTrtLtY59vf2MMZ3v5rSEAS+UGudZTIZcfvG"
        "DbQOGQUxg8GIMFCYsvRinThgQBSG5GmOKzQWgwgUh5yTzkKHqK7Y2xpCEVJMU2pJ7LWNZgKClTa93X1mZyydZoNp"
        "N/bJgT7FanfOe856TDDbJEahTs1irSMME/bjFDeasPPmQwYyRbea2PHoSB8iywoGBxOWlpe5fvUuX//Ka3z6J9/H"
        "2fNrXH/jJndu3+Hgfo+th5vkouDCU4/z2KWzdBc7RwnIDzIGedSd+6eLlQ4THCW8Aov94VlbBaw7xyGxocxL0kmG"
        "tX4FWyExJucjH7tId2GWzlybNEtZfeoUsh3RaEbc++4t7szeZ2F1iZX3nyIvSpJQM+mP2XjrFnPnTlNoQYCPOWRp"
        "qccJUS1kOByyP96n0agT12KSekJ/OODatbfIp4YwjI7s2jiLKQyqEjm4e+8ey6vH0Cri2pUbhGHC3u4e1llOnDhe"
        "MQRy+oM++dR3rjTqNWqNerWyDXmWYwpHd7aFcAJjQ4JQI8OAqAhpmSbbr2/yiY/+GKawZJMpq8fmGU+9sK1y+Dby"
        "GpgcOmaBaZaRNCKKR2+RbW5x8/otapdPEDViysnUszCtICtyVpZWcSbg3MlL3Ll3m067Cwg+8Mnn+cAnnz/SmSxK"
        "Q5pOUVpRmMI3ZAvfMv+DYu33CjgeWYR1ZKnXbVIIoiQG9SOk/9aWKOmAEII6t1+9zbR3nTQvaOqYhdlZ7qobnH36"
        "JEk9odFsEiYBC4+t4OrCi1BsztB2DWRXsbAWolwOJOhI0380pBb1SC7MUxQFxho21x8yNzuLChWdVhecI8tSBsMB"
        "NVNjtttl2O9jbYYxrpLk86ulLEoC5+gP+uBgdXWNPM947vnLOATr9xNAUkvqYA3T6YRskjMZjxkPx3QXOyRRRJYX"
        "ZGnm5YelquQDC9/hkhbsrT/AZSEb93bI8oIr/VuUxrC4ssid8Q6P7m1QpgVCaXLpcMLwxOXH0QrS0QAzCtBpQW+g"
        "Gew7OBiQ7U+Y9CdEsoVxJcPJlMWFRW7deMSt6w9YXp0hT3MOdvfp7Y8YDcYksaLeiEBDMtNgNpnDUFTSgu/I3d4R"
        "SL8LgDzstHV/FIj8QVnb/k6PF770PZQUtDo1Pvzp9/8oOJJAyYA8LzCDITrPmFnuIGYVxjjEpKD7wRqTYY+w0WZq"
        "cx5tbWCkYUkMqTVD5pcXOdgfMdqdonsh5WTK0nOrRCfrGGvRImTryn1ErWT+3AnQkE1Tv+n0hjSdIKnFJEmCtj7r"
        "iWsRF5+4xPU37rCzuUdRlB6YVF7fGwTOCubnFymKgjzPPdorJPV6Qi1pkKUFeVl6jyagyAumWcqp2RMATCYTnBGE"
        "Wh3JKgsZop1FK8VMC25ff8jW1i6nTh6ndzCkOzOHkpp+f8juzh7ltETkJRSWoB6RL0+Q7ZjJeOI1nJxm8+GQgC7Z"
        "zoS9W1sUpaG3MyEtSqZZytaDIXEU4MqcB+ubrBzvEEU1MFBMDcWkJE+9ElyrCCgOtryGpRJ0Z7teZONH2K5+VI8V"
        "RgHHTi6g0dSSCIdPLPSf+OECtq894voXXyXvjZjEkvbKLEGjhSsE7ZUaK+dP8svPnePNb73JlVffYOgKVlYXOdgV"
        "XL+xwyc+/glasx16m0PopexMcuaeWiN3hmKcUaSOmePLrJ49idWS0kGIgtwShzFaaJRW9Pp9ojii3qgfqaaEkY+H"
        "nH07tXU4n81IRVk6trf20YGiSDOctczNzNM/GNHb7xHFEcYY2p0mw9GQaTlhcW2Boii9QQpR9f95cFSUUBaWMiup"
        "Jy3arQELc132d/bJ0gwFmDKlVasjyhKbpzgpOP7YaRpxTL9/QNSYIdKSSCds3nvEGy9+mZlghqVTj7E+6lFOUtZW"
        "VwmNZHNrj6tXbnP+wioqNMwvzZDUvM4nekR7oY4xljI3SBShDNjd2iVMAowxtNptdPSDjeYw3bfWvieoqSwNvb2h"
        "r23mEafsSa8m98MKeLv3HnHpx55lsL3HwE6J6zEX3nfZn1TuGOwPCGsBJz90hmA54NTqGtlkysGgz8zcHI/ubdCu"
        "Nzj1+BppnqFCRXdpjlotZnvnHpPehPk5w3inR22hiwgkUgiCKGRraxspFUnTSwdLpekdDAlCTTsOCWOJcwXWKpwx"
        "Rxraxhga9TqPHm2wv39AGEaMh2MwlivjG4yGI0ajIQuLi5w+cxqtQ4JIc/L8cdozLUbjSdXCIxDWk+RM7piMJkeZ"
        "SjrKaTfaJKdqDAdjsjRFS0mjXsfkJSeXl5mOJiTtDoiAwfoucycWMEWKzUrCOGa8kyH7BWkyohnVOXNiFecsrZk2"
        "gZMUZcHF8xdozEiW1zoEiTxS3Z2Zb3q5m++zgJWzi+/mqX2/TlZlSF7T0r7tfX5I+eTwuZn5Dp/8mQ+9k5j2Rztt"
        "f9AbL/34+0gxdB+b48Gt2zS6M1hjKQtDNkpRSmBcTnshJGqu0KhFtEWC3FGsRU0mgynj3pDBwYDW8hyRsezdekB2"
        "0CYuNDMLMwxGQ8Y3hlzudojqXubG6zGGbG1uYaRlmk5oddpEUYwxBa60NJqtSsLYYIzvbw+UREpQWnHq5CpnTq8y"
        "Gk0oS0MgA+7d3WY4mLC3u0uoI7K0IAxjsI7jx1c9Xqa0L35WwuvCCfI0YzpOKfMS4STNRpPxaMKgNwYLWgRgHToK"
        "abea7A8zCiMoxxNiWWf8aJtGJ0JFLZxx5NmYrXyf4598llaSsDfYZH5unp3tXfq9IfloirMF1kwpC8HBASRFSFwL"
        "vTyPsAhRVFLNshLWr0S5jjp+xA8Ek46yNyHfYQ9eGPVwmsKPRLd2h3xwfrCszTv3TGsdgXMIrSmMxBRebEE5R5pN"
        "iVRIOTZs3d9hdnGG1AocBXEcoyNNImvMLMyRZRnlOIXUsH7/Abdvr1PXMa2ZFloJSjlhOpnSaCUsnVxBCU2e53Rn"
        "utTihF7vgDzNfKkm1FX3rPDoqhTs7fWo1xOCICAMA5SSNJp1rDUIociylLsb6xRTyNKMZqtJEGiKouDRgw2GwwEz"
        "M5coixKHo8gy3yVhIc8yiqLEWYEpLGGo0SpgNJp6EdW8ZNT3BDmrJXtbB9x54zrtTpvm8hw76zu0F2dodmIG9/YQ"
        "jYBjJ1awkyFf/PoXaQvBsx99P6N0yJ0792h3u2TjnEFvTLfTJWwF5GVOejBmLpghLwvCSPuZIdWNlEfhiE/Nj7bl"
        "PwYCOKThHv5uS4+Laal/qGf6Qc9rz3T0CvXGGoSTvpPFVvM4ZKV47yymeFtNTEpFd77Lra/e4f7X1rHFlFvkLD52"
        "krgZEyUBjU4dGSvcrMBgoC5ozLZYa5+g0+9gUkNoE+7fuk+gDbev3yHY2+LE2rKvic3PVJ5JY0xBo17DCi9NUxQx"
        "RVFCNbYhm065c+ce3W6HVrNBFAbIqq1GSU2z2aDbvUiWZuzv9dnd2ffSLEnM1vYWi8c6hJFmOp2itF9fRV7grCBQ"
        "AYUrKYucKAoRRrG3tYcrSqbjjPnZBWwhKLOMg9tbjB5sYUYp4ewCg41txjtTVn/sabpnZ3nry39AUKsRySaPNy7Q"
        "+nCT9uoil567QL2pCcKS3t4eSdCg1WgymWTURjC/2CRpdTno7VFvNbBWY43XbP8jOb74YZn423HRDyuN/Mh8JCkE"
        "xhj2d6aUhUVKU82+oOLFVG1IaPo7faJadNRJ4Pqw9eYm88fnECZld++AjkrYuLuFV0r04xPiVp2knhC0Q5ozTVrt"
        "Bs1GAzUboqIGeqlJEmi2tndQgWA8nlDkBSoIUUGAVZbF1SUIPJqlhZ8u8OYbVwhljTAIOHlyFakcezu75NMprVYb"
        "UESxJYpD6rUaxhjGpVdLS6KIqUnp9w4IY8XFy4+RlyUIQZHnR8pvQkuG/RHpOEUJiALBYJhj8oKAkMHQUagRKlQI"
        "GSL7U8r9MUtzC7haRP/2QzrdWW5/6yrpwQni1hwuHfPw+jrzi2fRzRku/IWnmek2GO4OuXD+LKNhyv7uPo1azN3b"
        "B+C62LJkNBgSBAHNZpMsyyv0+t1tHT/MGFyl8S2lRCv9dmqPFyz70xqTPoK6c4uwGnEkAVr1O8kK1HIKSn1k7NZa"
        "1q89JEBRJBZNyFxzERs52gsNrDFQOGxhKHo5g80BhohtuYcThlqzRr1TI2rF1OfqjGLNzOw8eZ4Sa4mlYDqZgrVk"
        "VhBHUcU/djSSBq+89AqutMwvz5FlKXQiZue75FnG7s4eo8GYTmdKs9MhqUUMB0OshSzNSccpRWbJ0wLrDB/51AcI"
        "o5CyyHHGYs3hRKgKhC0M2dSQ6Brj/pjtRymyKAmEZdIT7OxvUZvrUl+YZTotmV05RnbQR4UBK89dRuwN2f1XV3nw"
        "cMjY5cytdSjLgo0Huywc69KoB9y8f8vL/DQSFhdmWTu5wGSQYl2BEorB/oikEzCzOOu1to9ai76P3/8DirHvIgNV"
        "BECl1I+0Zf3IhuQOjcR5lS5rSw5765yrlCeqiroQb7NbbFbQ294jnUyIdyxKKHLryJiAkBhRIrVvtIvqIfV2G1Np"
        "Uts0p5xmjB/s0TMlhH5cRWemRW2uzX7oOH7pOP2DPjYvmOkuMt4fYCNFu93i5rXbrN99wKlTp5hfnOPevfsgJVEc"
        "0Z3toqRm6+E29+6tE27u0KjXSGoxQRgikeRZycH+AQf7B4wmIz74ieeRzpFnGaAreUGBFIqytLQaTdKhZX9nzLDf"
        "h7JGOjAkbY2WE+IgZrozoCwFOtJMh2NCJCq3JGstpAr8uLBIYgY5VlsW1tZ4eGsH5JTezg4LC7MURcp4lLG/02dx"
        "qYsQjjNnPLeqlrQ859w4IixSKkb9jGY7Rr6HQtehqt6fpWPkj/FI8sjdOSuB0rPEbTUuQfr5YkY4irLEWSimluF2"
        "ThLXmKg9ir0hEycoTInQglqtTpjE5GlOVhZoWzXZJZoCQxwm6CTB5BndRtdr7pQZBzt7bG7s0Dm+wGQyxVnLZDhl"
        "IQgZD0bMHV9h/f4jrl+5TqvZZtAf0uwmzEw6TCcT6vUGSb3hR1RZRXTQZ29vj83+CGt9+5TvTxOUhUEohVYx//Q3"
        "P8ePf/YjrKwukRee1C+V3/Kt8ZOhwkCys71BpztD5CLWH/Q4d/oEUbzHcG/EOC8I9vu0kjrlwYikXmfjyi0eX5sl"
        "DwMm0lCLNXKvZHFlkTLWhDKAvmX3rR3mn46ZX56nSLdIp4abb21Rq0UURYlxHjgdpim9gyGzC12KtKTTbfr+QvdO"
        "oY9300dspQ1+mOIfVvH/uAD86LnvJ3q7w6Dqj5uOVGkml0WBJuQoDpO+7cCUDomiyEuMdUwGUwZRgcsCTCm8sEMY"
        "4izIQDOZjHBRTtLoovIA6Sxbm9tgDBw4ao062+MeeVmwduIE3/jmCxRlwQff9zxXr95kXKScco5ksUlpJhw/dowy"
        "NaSjlKuvX2Vza4tm0qCW1DgY9Ojt91lZXeDhww2yMqdWjzFlSXumSb1eo9vtMhqM6PX6ZFlWdelKbGxxGC6ce4w3"
        "3rjBl77wHU6eWeLi4+cJowhT+CK1cNDb7XmdxUiRlzlJrYZ1Gbfv3mVleYb+aEQShDhjORj2qHdqDKcp80+fxTUj"
        "8q0DgkQzs9ChNxgwGU9RYUL7eJfG8Tq620Q3Ah5ubVCLYnRpMWHJrdt3WJxZwlrJ9oNd4obm/vouB/cNa6cWCBZc"
        "JYL1x6f4h0MWZSWLLP4E1yP+JA/1fcZXZiVZmpM0E79AnXAYV/q018m3h+DZEmc81mAwhKEfzGdzh7QOGQiSdg2R"
        "hF4WODUUxiAKS70eEsyHLHaP8ejeQ3av7NCoNbl5/Ranzp5imA6YXZ7jUe8haVZQi+q8/O03CJs1nvj0szy8tU0r"
        "bqJbLYJWnftX7yNUiEszGnGdMIrROiQMA3a3d+jMt1lammdra5M0zQgiLyeTK0kQa2YXuzR26wx7oyoTs/T7PS48"
        "dgFrIQih2eqyt9Pj5vXbLCwvsrS4hHN476QD6o2E0+dPsbO3jxOOE6eXGI+GRO0mSsBk1Gf+2AK9fMjKxdOM9wZ0"
        "Tq1ipcVmOc2VFs1nFrFizGijTyAUj33yHLWzXUxm2Xu4yeqpZV750hW6jTbNRcXa+UUObg7Y35/SaddZWlgiDQe0"
        "khzhpuzsFcz6ZmE/8rWa91AogTKOMgCXl7RnOkwmU2z1GlWNs/AkLklRTqk3WyhjGeRTpAtICLAup5Re6F2VflaM"
        "Vp4LPtofoYX28+CwaCc8IcwWXmzy7emHlZuUDmsNhXPkeYFwXm1ZKklciyjSHBy88J3v8tTTT/PN117ms+d/nEwP"
        "GRYZtlFSZBM2BiMeu3SR+xvrXHjiPGvn1nj92uvMzsySBHU29tZZuXiMSx95jO9963XW1la5s3Obu9+5wuqZFcYH"
        "Y6IwpFavk009itxpdRj1R7jSogLFwtISu9s7DPv+S/ohMAFBEKIChZOCMAnY292h2Wlw4eJZXnzxFaJEE0WK7swx"
        "Go2YTrt9tC1YP+WPyWRMnma06i3mZ2e5v3edg/0eO/0eJ86tUgsDdm/d58xjp9CRYjjs0bs6pigLRjcfsnTmJOn6"
        "Hp2FBTb6W9jhlBtvXuXGb9/m7KkTxMt1Vs6s8ZFPPcfYpAR1Qz4uefDGJkHY5OTqccYHAyhqXH/9Pse2Myb7fd4a"
        "jryYulR+Hp3WGDEimK2RHF/A9qbMzi9w/7UHviRSWE58dJnNW30GWxnH379C79E2q8ePc++NhyQLGqkF5qAkqgkK"
        "GxDV69x8/TrHTi9z7rFTBC2JNIogiqq5fhYtncAZQAQIofywXimPpiX6nrGgmrgY4GyILc3RTLBIh1DmNGp1RsMh"
        "YZLQK1MaUYCW3nMVzjE7N8v9+3e5/MQT7B30+Ed/97f5mX/jp/lO7ztsjLZ4/hNPkXYP+P0vfI6ZbpfhsI/LIbE1"
        "gkRy8NYuqh2w1F2hyHNKa0mzFCkE/f0+ncUuOoClYyvUkiF72/teSk8qDvb7DHoDBDAYDphdmuXy4xfJTcZwPCEI"
        "QubnZ6nVInQoUVJX+uECqRxZOmVyUCOfOHJ61IKQZLbGqlzjyjdvYE84astNov0m2SRjkKVE3Rah0uysP+D0MxcJ"
        "kzoH1x6x/mCd4c6E0x98nN/9xud4659/g53HH0edmqUcCqJOjc6ZLh2Z0Gl3eOKD59h5lLGz3UcGGZsP+3Rnl7C5"
        "pdgbYXNDLgSGHKkVWlsEmnS7ZHmxSUbAW199i3rQwimJs4rBRkk8jUknBdmuYXXhFHdeu0/aLyrKbok0CoxmOshg"
        "UfLEhy5x7NQxhHB+5Kuqwp9KpLbqZs+xTCjKxO+nxng3KL0USonXNixNiaP0aKqzFEVGPhiDKzl54jTgeO70RRaP"
        "rdI+1UHvGJqzTW4tXmW+Oc9cdwYlLaefOkEy36a92mV1bZnAJCRRnSc+cJZRlrMV7mBdiTSaRtJmbmaODf3IT/Eu"
        "fIxSFAXDwZA4DNnZ3KG96EW3JJJWt0mz3mT/oMfmw232dnsIJxj0BiyuzfP8h55mPBp68S4L9WadJI78hC38rLcs"
        "L5AKrw1ZKPr7fbbXd4nrsLTQptFNMOWUxQvHiEJBc2mGRqPO3tY2tVaNfHeIUoqgFtM+Pk99ZZHt3gixO2DmwjxZ"
        "VuByQzdqMNlPub15gzCbJUwi4lpC2FA8/cFTTNIRAxdw69X7SJWztNLl3p271CLJ9q2bKCtpdNrs93vUa3XKsiSK"
        "IhYX5rn7yk2QkiSu+6Hf0hEmmkdvParqmTGTuxP2R3sMhn1WTi4yPhgThAkqCHn0YIdnPn6B7rkmKggpp6ZSoZGH"
        "fUmVIYF21lKa1OMRIgXt3obcq4CpMIYwCrGyDzRxsvRGpSzxfB2Rl8T1gOl0iKw3CKTk5OIyO6aHdJr5eguTptTm"
        "Z5hmKQuLDX7sY0/y4M5DwrqkriWZGyGjiNl2lwejRwgUhZmQjlOmkwZRqKCmyU1Os94ktCGlK8izjL2DA+b6A7rt"
        "zlHflQgFs0sdavUaUq9z59Y9zlw6weXnLlDkhZ91m5dYaZhbWSJ3OYFUzM3N+TkkshoiowOmRcbFp5cZ7O9QTgXG"
        "OQb9PoPhgCc/+SRmOGLr2jrD7R0/VqKvGb11l9PPXGb+xDE27z7CXt9EFdBcmudgZ4BuBSy35xk2WlhheOzyGZ79"
        "+DP0h7sE9YgsLxnbMZc+8hTf/vpVus0uUSPn2NIKYbBHqxazGMb0dw6YFAXNetODrtYwHI/Iy5J6u0FZFVWtszjh"
        "tcx/7w8/z/feusHf/PX/gOnA8fd/4zeIYk2nMcuv/tpf5Y2X1vnyV1+m3ZH0tnf46//xv8l+OjjiyFvh3iFm49t7"
        "dBTFLCwc84IDuGqO6tvKN65KL1UAnX6LSEV+vrAT1Dotjn3kEtpApxVz9cYVOo0likFOOc1pLzYYPuwjpzlZAfNz"
        "8/QnIzZfuo/dH3PsfWeZPnmBnReu0ejUcXGEdZLV06sIrWgsN6m3IwajCboWc+LkKfqDIfVanV6/TytpY2t+ImR/"
        "Y0K33vGD65TElX7FJJHk+NoSOxs9Lj93AVc6AhdQF00m413mm226rRb9wZCl5WXipEae5V5TWgYEStLsGIajKQvH"
        "umjlKAs/tn71ZIvuTJ1BYNGiJNAtFme6TCcTOo+fpj3T4e6dB0SiRSQC6vUGDx5u0Qws5AXnPvgkNghZOrbA5eef"
        "5ZWvvMKZz5zkuU9c5vf/p29w594O3aURjAxBaBDOsrDQpt2N2d3cIbN+0pGyklocEyexn8YdhaAVeWkOZzH7n0ag"
        "pONXfv6vcv+//oeYsuR/+f0/5Ln3P84v/qW/xH/8f/sfuHnjAS+/9h3+g7/zl/ngp5/gP/yJv8XV165z5qlTpJMS"
        "qRwC4/UPhDiaNKkbzQaNVvOHKrUJwOaWgxt97rx2HxFK1k6sUg9DrHHspRNkvY4rIZ+U3Lp5h9Z8BzMsGI5HlFZy"
        "5/49mvNduotzzK7MUxpLc6VFfmGZpKkxhWUyGLH8/nkm0ww50sSzdfZu7fPo3oD+9jUcsDg3R57nTLOMg0GP0hmM"
        "KTm4eYCThjjyqm3ZdEq72WZ/b8Dnf/eL9O7ucOrUKtNRzqg/Js8Kiqxk89oBQRiSPvBoepzUkEJhKwJ9GMfoEAIH"
        "nVYXXQspiowoVBzs7XJwcECn3WK2O0c5Ncw129hpxv7NBxxr1zHNGusPH4J1PHHxBKPjJfdfvc6Z5WWeeuYyjU6N"
        "e3fuce7yCZaW5ti/t8XZxy6wuHCMuhU8ef4k2doUnCFPp0ynU2pRDZcURIFGyMDDNgZkoLyuUll6DlW1Cymtsfi2"
        "8ziISOKQoiyYjIdcvvRhwmjCs09f5sprVxHCEivB3Wv7tE+0ePHLV6nFEaN+iVQW67wQRzQXc2n5jB9q7Y7Aph8u"
        "+5djGJsMNzLIEMppjpWGN1+7QhEqJg8nTPaGLM4tEquQ++ubdMMGzZUZovkZNg/2iYM6ZTdir0gZXtkBURCciGi1"
        "5thb32UwnnDz5oiL5y7Q1E12Hu7Q3x5jx5bcFhhT8GDygHqjRhiGzDRbDIYjtvb2uNObsrq6xn4+QCpBoDXTIufB"
        "zQ1aYYP1t7YYbIyZTiYIocnygnargwHSfMi961tkWcmJ4yep1eoUZYmWglpN0moLWt0QO07JJym2yMkpycucGoqX"
        "//VXOLYwg0tL8jRHSYuWIbuRZnt3l2mWc/HSJd7cvo6sNemuNHnt2y+zdvIEDzfXmV9dIzfwrX/+LRYW5jhx/Czp"
        "IOXVq6/RrjUIwpjdvW0WF+d49OghB/tDzhw7TRiHWOcL7yKQRxO4VaSraaAeQ/JK4w5HgQwEUjhcKDEqpJ7M0+nM"
        "kSSK/kFOPZhBDAW6PqUcw3CQkaYpZlJQSjBYytKi8+JI4US/p/rKoRtTCisseZoxGPU4eeY49dmYYXvKuEwJg4iz"
        "7z/JeDjBZAXl4iKb9zd5/tITtOY6lKnl9s27SCvp9wfU63V2ersoHXDwYAdywUu3XiJNMz8XzUakkyn1ZsK5C2eY"
        "pGN0oL1IqJTUazWWF5bJc0OZFn5+rFZ+wE7mONjrMTc/S683ZCmuc+bMGUbjKUqHaBUQRBFFaf2wYicoCoNzhlAJ"
        "6rWIZj1Eq5x0MPFMfusQroSyRBlLVjp6d7dY0TEbN+/Q7/VZWJ7l3r0NFhYXyEvLuQsX+N5XXmQwmpC0u6z0Z3jj"
        "xVeJXchbb7zJ3sMee70BTz7zJOPdCb1wh+2dHR7cfcCWjAh0jSiSPMof4lzJudPnufrmNZ577iJpVqAD7VFrqdBK"
        "Y6qhP0dotKumQQo/P9g6x9zCPPVag97ehLm5RTY3b/DkM2d56cXbjCYDTjZX6O0MeN8n5nAolCwwSqCVRirfyi6k"
        "8ob0HlsI0MI3IY7LMUZAe37BDwGuKfJWTqDatLsd7l/foB42ySY5o4MJw+2UrVvXEEKztzXgK1/8BjOdWWr1Gnfu"
        "3OHUqdPoKGZrd4vZ+Rm0UgyHPh7KywwjDKtrK7zv/c+gtaYoMpxzpFO/WpRUxKGvGZZZgS28fK81jpMnjqN1iD4X"
        "VsNdoJbEPpPBUpoca/Et2tLzRgOl/eDiSOFcRlkWCOugLP3kyLJAlL7oK5xkeXGO7770XbqtNqoWsr27z8kTp7hz"
        "5y5zi0vs7PSZpgX1RptpUXDt+j1OnDrDzTv3uHDhMlevXaM7M8vu5hYPtx6ysDRHXqREtZAL589z+9Zt2rMzXL32"
        "FsePH2dje5u5lWVkHCPxWpOHLeZCVpPYpPC1NeEqbNDhpCSMI5weoQLBL/zlz/I//4//jPVbt0mLAT/+Ux9Hq4Tf"
        "+gf/nIWFOVrzistPnGKSZYhAEwSe8Oecr6UK/Ngy4d5Dg9O9+3cY3JygJyGFyIniCB14h1mWljSbkoQ1XA4Hmz3G"
        "vTHSeCxKOosrLaGK2Nsd8MILL6FVhHWOuF4nK3KvwSpLjM2xhaNeb3qulIDCGmqNkE985hmclVhb+IF+WmFKg1R+"
        "+mIYBJVEspeXss4daV92Z2dJkgRTlmR5gcVfaGOtn95YDecz1qGlQkmJLXMUDu0c0lqohiArZ3F5isaPJd3a2KCZ"
        "RNR1QKQC9nd36bQ6pGnBuCwwTlBr1omShMxaRianOzvP1tauV/ivRobtHRwQxjGNVoM8L5DSj7GfTqf0+z1WVpYY"
        "DEaMRiOOHVvDYSjLHCk9R8xhEYTVKHeJlI7SGqRWVNAYgQ7Y2d2h2WrRmZnj7p11Hj7c4PHHz9FMamiluX79Ngd7"
        "uzzz9CW0Dsit9ecYKH/tS0M8G3P+g2ewwXs0pPv37zK8PUGPtR8C56yXufGTBTxCVe3Xzlr6+wNGB0OKrKAR1nGF"
        "I5AR+7sDvvjFr6JUWDUiCvKqFUmHHor30619BV4oTZrnzM61+Ymf+pDfeqrMQQiO+DVH4uGBxtmK2C5ENfqzxApH"
        "o91iZrZLUquRlyVCeOlkqXxaa/xRkTaoRNYtAovGoazFGa9lTVmgnEM6C7Yk1BqKHJsNwVRey+ToIMaoGKE1aZ76"
        "DSfQuECT5iVBFJIbi4winHFoHVFayLPiSETDOIvSEiUDityr9UotKIochcaaaiabFDgMghBVvQ/hcFKAkF7GsCKb"
        "BaGkKDOMtSSNhCAMmI4m2NIhhdfiFCgm/WElMaRxws9/s9ZfN9mQnP3AWQjfwwgJV6mdltqia5qjlkkH0vnpg04I"
        "7wGEQzjFSnOJYnmBrUc9+gcDpPHjGCZlSW88ol7vgHOYsmA06NGs1xn2M8IwprQlppp9QlmAKcjHY8gjKLNK1MDb"
        "oXKqmiXmWZ2HWtGVZK3HlZxGYtlPe+zs7bGwtMDSyqKPFCMfMSqpCD1ci3QKZ/wqEULinKfgahQ6zdGRqoxMgZXV"
        "eAqH1OHRiHcIyZ2itBq0hqhe3UhfTK3VIyyWMAo8N1wJ372sNEEjwAo/TlUL7zWts+h6eAQGah0inCf6iUoxxiL8"
        "4GUFopqY7Q7BnIqPLaSvNsgwRCOwhSDLSoQK0bG/XtM882FxXfv3K3kkJafQfhfQGimF9+zvrV1XEkQKEfrAzVYe"
        "SeLAFQhx2MJjkVZhTEFQkxyfnWV7zzLYHhEEknanzpP2cYQIfBDoLM6WKKDIS5SuyjXCSzILIXCU1OoxYtn6my0O"
        "C8w+RT+kBB9O1K1GRB8hYtYacJqaSLBCMM5H7IwkyyuLOJlSViitEL5z1TnnKc2umlUp/Dj7vMyxscNIqiKoB3eF"
        "lUgXUZbKb6VKYCsEWDp/bvZQk8B5KWcnwEmN8UMfPSvTyaOp3tpVs71FNRvtsOnRvXNk7Nu6kH5CuqSQ7xj/ag3C"
        "VR3TlRE5eTTN9u3GyHdKYH8f9dYBVphDuXav7FtvEDcT/x28ut572Nru3mfUH1fUhbd7y101zByk70wVzh9YGD8o"
        "rlKSP5xsoJUmCMJqLHnhcQ6lqlHgAluNnbfW+BM/kl0xlGVRcWr8CPJDjs27cIrq70N1mMObJ6ui9OHM1rwoj0jw"
        "ztjKx/rL5fBTLkWF4vrZwdWFle7dPOfDDo4jlepK/rMSBJUcirQf6u2LI5HQw2MK57dWe6TK78/3SP/f+QVanQjC"
        "VaYgqnGwwg8dOhor71xVHxWVWLs9GlOKFV6kTLhKtFS9gzkijlqz30lMOhKxFw7rSk6fPUMQRb7HULwXQ3LVrLGq"
        "IeD7MabDmRTyUF+iuijevHw29c77ba31pyxtdVMkwlVuuWpKlNiqJugvjxCHx3bVwLk/AfSqbqoV77wplfLc27cK"
        "hMAqU5WNBNL5rcBWX0QdTZ8WlScQR0Of36U2XGXa9mgkWfUP5+O5d5LvpZeuEZUo3TsO4TOi6lOlk297H8AKixW2"
        "Cin8c0aa6vWyOkeq61ZdU+SRALu/04e+yHIkwnQkyfxHr+EPmLUGzviuZh1UUwp4bx7pzx9//vhj5bL//BL8+eN/"
        "i8f/D9Id2+Sr1Y2mAAAAAElFTkSuQmCC"
    ),
    "note_100_96": (
        "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"
        "RU5ErkJggg=="
    ),
}
# END EMBEDDED CURRENCY PICTURES


def font(px, bold=False):
    return (FONT_FAMILY, -px, "bold" if bold else "normal")


def money(value):
    return f"{CURRENCY}{value:,}"


def _positive_integer(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def plan_single(amount, coin):
    """Return an exact payout without rounding away the customer's money."""
    if not _positive_integer(amount) or not _positive_integer(coin):
        raise ValueError("Amount and denomination must be positive whole pesos.")
    if coin not in COINS or amount % coin:
        raise ValueError("This denomination cannot return the exact amount.")
    return {coin: amount // coin}


def plan_mixed(amount):
    if not _positive_integer(amount):
        raise ValueError("Amount must be positive whole pesos.")
    plan = {}
    left = amount
    for coin, percent in MIX_SHARES.items():
        count = (amount * percent // 100) // coin
        if count:
            plan[coin] = count
            left -= count * coin
    if left:
        plan[1] = left
    if len(plan) < 2:
        # Small totals need a deliberate mix: PHP 10 can be one PHP 5
        # plus five PHP 1 coins, rather than another all-PHP-1 preset.
        plan = {}
        left = amount
        for coin in COINS:
            if 1 < coin < amount and left > coin:
                plan[coin] = 1
                left -= coin
        if left:
            plan[1] = left
    return plan


def valid_plan(amount, plan):
    return (
        _positive_integer(amount)
        and isinstance(plan, dict)
        and bool(plan)
        and all(_positive_integer(c) and c in COINS
                and _positive_integer(n) for c, n in plan.items())
        and sum(c * n for c, n in plan.items()) == amount
    )


def describe(plan):
    return " + ".join(
        f"{n} × {money(c)}" for c, n in sorted(plan.items(), reverse=True)
    )


@dataclass
class PayoutOption:
    title: str
    detail: str
    plan: dict


@dataclass
class CoinCombination:
    """An editable payout whose selected value can never exceed its budget."""
    amount: int = 0
    counts: Counter = field(default_factory=Counter)

    @property
    def plan(self):
        return {coin: count for coin, count in self.counts.items() if count}

    @property
    def total(self):
        return sum(coin * count for coin, count in self.counts.items())

    @property
    def remaining(self):
        return self.amount - self.total

    @property
    def ready(self):
        return valid_plan(self.amount, self.plan)

    def set_amount(self, amount):
        if (not _positive_integer(amount) or amount not in EXCHANGE_AMOUNTS
                or amount < self.total):
            raise ValueError("The combination must fit the inserted amount.")
        self.amount = amount

    def adjust(self, coin, delta):
        if (not _positive_integer(coin) or coin not in COINS
                or not isinstance(delta, int) or isinstance(delta, bool)
                or delta not in (-1, 1) or self.amount not in EXCHANGE_AMOUNTS):
            return False
        count = self.counts.get(coin, 0) + delta
        if count < 0 or self.total + coin * delta > self.amount:
            return False
        if count:
            self.counts[coin] = count
        else:
            self.counts.pop(coin, None)
        return True

    def clear(self):
        self.counts.clear()

    def fill_remaining(self):
        if self.remaining <= 0:
            return False
        self.counts[1] += self.remaining
        return True


def payout_options(amount, inserted_coins=None):
    """Offer exact, distinct, coin-only payouts that change the input."""
    if not _positive_integer(amount) or amount not in EXCHANGE_AMOUNTS:
        return []
    options = []
    seen = set()
    deposited = dict(inserted_coins or {})

    def add(title, plan, kind=""):
        key = tuple(sorted(plan.items()))
        if key in seen or (deposited and plan == deposited):
            return
        seen.add(key)
        count = sum(plan.values())
        detail = f"{count} coin{'s' if count != 1 else ''}"
        if kind:
            detail += f" · {kind}"
        options.append(PayoutOption(title, detail, plan))

    for coin in COINS:
        if amount % coin:
            continue
        kind = ""
        if deposited:
            if coin > max(deposited):
                kind = "Larger coins"
            elif coin < min(deposited):
                kind = "Smaller coins"
        add(f"{money(coin)} coins", plan_single(amount, coin), kind)
    # PHP 50 can use two PHP 20 coins plus one PHP 10 coin. A remainder
    # must be returned rather than discarded or hidden behind rounding.
    remaining = amount
    fewest = {}
    for coin in COINS:
        count, remaining = divmod(remaining, coin)
        if count:
            fewest[coin] = count
    add("Fewest coins", fewest, "Mixed values")
    add("Mixed coins", plan_mixed(amount), "Mixed values")
    return options


@dataclass
class ExchangeSession:
    source: str = ""
    amount: int = 0
    inserted_coins: Counter = field(default_factory=Counter)

    @property
    def ready(self):
        return self.amount in EXCHANGE_AMOUNTS

    def begin(self, source):
        if self.amount:
            raise ValueError("Finish the current exchange first.")
        if source not in ("bill", "coin"):
            raise ValueError("Select a bill or coin exchange.")
        self.source = source
        self.inserted_coins.clear()

    def accept_bill(self, value):
        if self.source != "bill" or not _positive_integer(value) or value not in BILLS:
            raise ValueError("Accepted notes are PHP 20, 50 and 100.")
        if self.amount:
            raise ValueError("Only one note is accepted per exchange.")
        self.amount = value

    def accept_coin(self, value):
        if self.source != "coin" or not _positive_integer(value) or value not in COINS:
            raise ValueError("Accepted coins are PHP 1, 5, 10 and 20.")
        if self.amount + value > MAX_CREDIT:
            raise ValueError("The maximum exchange total is PHP 100.")
        self.amount += value
        self.inserted_coins[value] += 1

    def options(self):
        deposited = self.inserted_coins if self.source == "coin" else None
        return payout_options(self.amount, deposited)

    def reset(self):
        self.source = ""
        self.amount = 0
        self.inserted_coins.clear()


class App:
    def __init__(self, root):
        self.root = root
        self.session = ExchangeSession()
        self.screen = "idle"
        self.options = []
        self.selected = 0
        self.custom = CoinCombination()
        self.pending_plan = {}
        self.review_origin = "choose"
        self.plan = {}
        self.total_coins = 0
        self.dropped = 0
        self.dispensed_value = 0
        self.coin_queue = []
        self.completed_amount = 0
        self.completed_plan = {}
        self.done_deadline = 0.0
        self.taps = []
        self.actions = []
        self.focus_index = -1
        self.focus_ring = None
        self.hover_index = -1
        self.keyboard_focus = False
        self.done_timer_item = None
        self.tick_job = None
        self.drop_job = None
        self.done_job = None
        self.closed = False

        root.title("Peso Exchange | Coin changer")
        root.configure(bg=BG)
        root.minsize(WIDTH, HEIGHT)
        if FULLSCREEN:
            root.attributes("-fullscreen", True)
            root.config(cursor="none")
        else:
            root.geometry(f"{WIDTH}x{HEIGHT}")
        root.protocol("WM_DELETE_WINDOW", self.close)
        if ALLOW_ESCAPE:
            root.bind("<Escape>", lambda event: self.close())

        # Keep every PhotoImage alive for the lifetime of the application.
        self.currency_images = {
            key: tk.PhotoImage(master=root, data=data, format="png")
            for key, data in CURRENCY_PICTURES.items()
        }

        self.canvas = tk.Canvas(
            root, width=WIDTH, height=HEIGHT, bg=BG,
            bd=0, highlightthickness=0, takefocus=True,
        )
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Leave>", lambda event: self.clear_hover())
        root.bind("<Tab>", lambda event: self.move_focus(1))
        root.bind("<Shift-Tab>", lambda event: self.move_focus(-1))
        root.bind("<ISO_Left_Tab>", lambda event: self.move_focus(-1))
        root.bind("<Return>", self.activate_focus)
        root.bind("<space>", self.activate_focus)
        self.show("idle")
        self.tick()

    @property
    def amount(self):
        return self.session.amount

    def text(self, x, y, text, size=16, bold=False, color=TEXT,
             anchor="nw", width=None):
        options = dict(
            text=text, font=font(size, bold), fill=color,
            anchor=anchor, justify="left" if anchor == "nw" else "center",
        )
        if width is not None:
            options["width"] = width
        return self.canvas.create_text(x, y, **options)

    def rounded(self, x1, y1, x2, y2, fill=SURFACE, outline="", radius=14,
                line_width=1):
        r = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        return self.canvas.create_polygon(
            points, smooth=True, splinesteps=24, fill=fill,
            outline=outline, width=line_width,
        )

    def coin_icon(self, x, y, value="₱", radius=19):
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                fill=TINT, outline="")
        self.canvas.create_oval(x - radius + 5, y - radius + 5,
                                x + radius - 5, y + radius - 5,
                                outline=ACCENT, width=1.5)
        self.text(x, y, value, 18, True, ACCENT, "center")

    def check_icon(self, x, y, radius=11):
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                fill=ACCENT, outline="")
        self.canvas.create_line(x - 5, y, x - 1, y + 4, x + 6, y - 4,
                                fill=SURFACE, width=2.5,
                                capstyle="round", joinstyle="round")

    def currency_picture(self, kind, value, x, y, size):
        return self.canvas.create_image(
            x, y, image=self.currency_images[f"{kind}_{value}_{size}"],
            anchor="center",
        )

    def payout_pictures(self, plan, x, y, size=32, gap=27):
        coins = sorted(plan, reverse=True)
        for i, coin in enumerate(coins):
            self.currency_picture("coin", coin, x + (i - (len(coins) - 1) / 2) * gap,
                                  y, size)

    def action(self, rect, command, shape, outline="", line_width=1):
        self.actions.append(dict(
            rect=rect, command=command, shape=shape,
            outline=outline, line_width=line_width,
        ))

    def button(self, rect, title, command, primary=True, enabled=True, size=16):
        x1, y1, x2, y2 = rect
        fill = (CTA if primary else SURFACE) if enabled else DISABLED
        foreground = TEXT if enabled else MUTED
        outline = "" if primary or not enabled else BORDER
        shape = self.rounded(*rect, fill=fill, outline=outline, radius=10)
        self.text((x1 + x2) / 2, (y1 + y2) / 2, title,
                  size, True, foreground, "center")
        if enabled:
            self.action(rect, command, shape, outline)

    def common(self):
        self.canvas.create_rectangle(0, 0, WIDTH, 80, fill=HEADER, outline="")
        self.canvas.create_rectangle(0, 77, WIDTH, 80, fill=CTA, outline="")
        self.rounded(23, 19, 65, 61, fill="#26384B", radius=12)
        self.currency_picture("coin", 20, 44, 40, 32)
        self.text(76, 21, "PESO EXCHANGE", 18, True, SURFACE)
        self.text(76, 47, "COIN EXCHANGE STATION", 10, color=HEADER_MUTED)
        can_go_back = self.screen in ("deposit", "choose", "custom", "review", "admin")
        badge_left = 516 if can_go_back else 648
        self.rounded(badge_left, 24, badge_left + 124, 56, fill="#26384B", radius=16)
        self.canvas.create_oval(badge_left + 14, 37, badge_left + 20, 43,
                                fill=CTA, outline="")
        self.text(badge_left + 33, 40, "Demo mode", 12, True, CTA, "w")
        if can_go_back:
            self.button((656, 18, 772, 62), "‹ Back", self.go_back,
                        primary=False, size=16)
        self.canvas.create_rectangle(0, 448, WIDTH, HEIGHT,
                                     fill=HEADER, outline="")
        self.canvas.create_line(0, 448, WIDTH, 448, fill="#314256")
        self.text(28, 464, "ALL PAYOUTS IN COINS", 10, True, CTA, "w")
        self.text(772, 464, "Demo · No hardware connected", 11,
                  color=HEADER_MUTED, anchor="e")

    def steps(self, current):
        for i, (x, title) in enumerate(((28, "Insert money"), (222, "Choose coins"),
                                        (416, "Review"), (610, "Collect"))):
            colour = ACCENT if i <= current else MUTED
            fill = ACCENT if i <= current else DISABLED
            self.canvas.create_oval(x, 96, x + 20, 116, fill=fill, outline="")
            if i < current:
                self.text(x + 10, 106, "✓", 12, True, SURFACE, "center")
            else:
                self.text(x + 10, 106, str(i + 1), 11, True,
                          SURFACE if i == current else MUTED, "center")
            self.text(x + 29, 106, title, 12, i == current, colour, "w")
            if i < 3:
                self.canvas.create_line(x + 146, 106, x + 178, 106, fill=BORDER)

    def show(self, screen):
        if self.closed:
            return
        same_screen = screen == self.screen
        focused_rect = (self.actions[self.focus_index]["rect"]
                        if self.keyboard_focus and 0 <= self.focus_index < len(self.actions)
                        else None)
        self.screen = screen
        self.canvas.delete("all")
        self.canvas.configure(cursor="none" if FULLSCREEN else "")
        self.actions = []
        self.focus_index = -1
        self.focus_ring = None
        self.hover_index = -1
        self.done_timer_item = None
        self.common()
        builders = {
            "idle": self.build_idle, "deposit": self.build_deposit,
            "choose": self.build_choose, "custom": self.build_custom,
            "review": self.build_review, "dispensing": self.build_dispensing,
            "done": self.build_done, "admin": self.build_admin,
        }
        builders[screen]()
        if self.keyboard_focus and self.actions:
            self.focus_index = (next((i for i, action in enumerate(self.actions)
                                     if action["rect"] == focused_rect), -1)
                                if same_screen else 0)
            self.draw_focus()

    def build_idle(self):
        if self.amount:
            self.build_resume()
            return
        self.rounded(28, 96, 772, 165, fill=HEADER)
        self.text(48, 108, "CHOOSE BILLS OR COINS BELOW", 10, True, CTA)
        self.text(48, 130, "Tap a picture to get started", 26, True, SURFACE)
        for rect, title, mode in [
            ((28, 182, 391, 437), "Bill to coins", "bill"),
            ((409, 182, 772, 437), "Coin to coins", "coin"),
        ]:
            x1, y1, x2, y2 = rect
            shape = self.rounded(*rect, outline=BORDER)
            self.text(x1 + 22, 202, title, 24, True)
            hint = ("Insert a note and choose the coins you need." if mode == "bill"
                    else "₱5 / ₱10 to smaller coins, or combine coins.")
            self.text(x1 + 22, 240, hint, 12, color=MUTED)
            if mode == "bill":
                for i, value in enumerate(BILLS):
                    x = x1 + 70 + i * 111
                    self.currency_picture("note", value, x, 301, 96)
                    self.text(x, 356, money(value), 15, True, anchor="center")
            else:
                for i, value in enumerate(sorted(COINS)):
                    x = x1 + 50 + i * 88
                    self.currency_picture("coin", value, x, 301, 64)
                    self.text(x, 356, money(value), 15, True, anchor="center")
            # The picture, label and green prompt share one large touch target.
            self.rounded(x1 + 18, 383, x2 - 18, 427, fill=CTA, radius=10)
            prompt = "Tap to change bills" if mode == "bill" else "Tap to change coins"
            self.text((x1 + x2) / 2, 405, prompt, 17, True, anchor="center")
            self.action(rect, lambda m=mode: self.begin(m), shape, BORDER)

    def accepted_totals(self):
        self.rounded(28, 392, 772, 431, fill=SURFACE, radius=10)
        self.text(46, 412, "Exchange amounts", 12, True, MUTED, "w")
        for x, value in zip((258, 363, 468, 573, 693), EXCHANGE_AMOUNTS):
            self.text(x, 412, money(value), 16, True, TEXT, "center")

    def build_resume(self):
        self.text(28, 101, "Continue your exchange", 29, True)
        self.text(28, 145, "Your inserted money is saved. Continue where you left off.",
                  14, color=MUTED)
        self.rounded(28, 191, 772, 374, outline=BORDER)
        self.text(50, 215, "YOUR INSERTED AMOUNT", 11, True, MUTED)
        self.text(47, 243, money(self.amount), 54, True)
        caption = "Coin exchange" if self.session.source == "coin" else "Bill exchange"
        self.text(50, 331, caption, 14, color=MUTED)
        self.button((441, 279, 746, 339), "Continue exchange",
                    lambda: self.begin(self.session.source), size=19)
        self.accepted_totals()

    def begin(self, mode):
        if self.screen != "idle":
            return
        if self.amount:
            if mode == self.session.source:
                self.show("deposit")
            return
        self.session.begin(mode)
        self.custom = CoinCombination()
        self.pending_plan = {}
        self.options = []
        self.selected = 0
        self.show("deposit")

    def build_deposit(self):
        self.steps(0)
        is_coin = self.session.source == "coin"
        self.text(28, 135, "Insert coins" if is_coin else "Insert a note", 28, True)
        self.text(28, 177, "Tap a coin picture to insert it." if is_coin
                  else "Tap a bill picture to insert it.", 13, color=MUTED)
        self.rounded(552, 132, 772, 361, fill=HEADER)
        self.text(570, 152, "INSERTED CREDIT", 10, True, HEADER_MUTED)
        self.text(567, 177, money(self.amount), 44, True, SURFACE)
        count = sum(self.session.inserted_coins.values())
        caption = (f"{count} coin{'s' if count != 1 else ''} inserted" if is_coin
                   else "Note accepted" if self.amount else "Waiting for a note")
        self.text(570, 238, caption, 12, color=HEADER_MUTED)
        self.canvas.create_line(570, 269, 754, 269, fill="#34465A")
        if self.session.ready:
            hint = ("Ready. Choose your coins,\nor keep adding coins." if is_coin
                    else "Ready to choose your coins.")
            colour = CTA
        else:
            target = next(v for v in EXCHANGE_AMOUNTS if v > self.amount)
            hint, colour = f"Add {money(target - self.amount)} to reach {money(target)}.", SURFACE
        if not is_coin and not self.amount:
            hint = "Insert a ₱20, ₱50 or ₱100 note."
        if self.amount == MAX_CREDIT:
            hint = "Maximum total reached.\nChoose your coins to continue."
        self.text(570, 289, hint, 13, color=colour, width=180)
        values = sorted(COINS) if is_coin else BILLS
        gap = 12
        card_width = (504 - gap * (len(values) - 1)) / len(values)
        for index, value in enumerate(values):
            left = 28 + index * (card_width + gap)
            rect = (left, 203, left + card_width, 405)
            enabled = (self.amount + value <= MAX_CREDIT if is_coin
                       else self.amount == 0)
            callback = self.insert_coin if is_coin else self.insert_bill
            shape = self.rounded(*rect, outline=BORDER)
            self.currency_picture("coin" if is_coin else "note", value,
                                  left + card_width / 2, 264, 84 if is_coin else 146)
            self.text(left + card_width / 2, 335, money(value), 23, True,
                      color=TEXT if enabled else MUTED, anchor="center")
            self.rounded(left + 10, 353, left + card_width - 10, 397,
                         fill=CTA if enabled else DISABLED, radius=8)
            self.text(left + card_width / 2, 375, "Tap to insert" if enabled else "Accepted" if not is_coin else "Full",
                      13, True, TEXT if enabled else MUTED, "center")
            if enabled:
                self.action(rect, lambda v=value, cb=callback: cb(v), shape, BORDER)
        help_text = ("Examples: ₱5 → 5 × ₱1   ·   ₱10 → 2 × ₱5" if is_coin
                     else "Choose coins when your credit is ₱20, ₱50 or ₱100.")
        self.text(28, 418, help_text, 12, color=MUTED)
        self.button((552, 377, 772, 433), "Choose coins", self.open_choose,
                    enabled=self.session.ready, size=18)

    def insert_bill(self, value):
        """Acceptor entry point; invoke on the Tk main thread after acceptance."""
        if self.screen != "deposit" or self.session.source != "bill":
            return False
        try:
            self.session.accept_bill(value)
        except ValueError:
            return False
        self.open_choose()
        return True

    def insert_coin(self, value):
        """Coin input accumulates until the customer selects Choose coins."""
        if self.screen != "deposit" or self.session.source != "coin":
            return False
        try:
            self.session.accept_coin(value)
        except ValueError:
            return False
        self.show("deposit")
        return True

    def open_choose(self):
        if self.screen != "deposit" or not self.session.ready:
            return
        previous_plan = (self.options[self.selected].plan
                         if 0 <= self.selected < len(self.options) else None)
        self.options = self.session.options()
        if not self.options:
            return
        self.selected = next((i for i, option in enumerate(self.options)
                              if option.plan == previous_plan), 0)
        self.custom.set_amount(self.amount)
        self.show("choose")

    def choice_heading(self, title):
        self.steps(1)
        self.text(28, 131, title, 26, True)
        self.rounded(590, 130, 772, 177, fill=TEXT, radius=10)
        self.text(604, 154, "INSERTED", 10, True, "#BDD0DC", "w")
        self.text(757, 154, money(self.amount), 27, True, SURFACE, "e")

    def choice_tabs(self):
        for rect, title, screen in [
            ((28, 196, 394, 240), "Quick combinations", "choose"),
            ((406, 196, 772, 240), "Choose each coin", "custom"),
        ]:
            chosen = self.screen == screen
            shape = self.rounded(*rect, fill=ACCENT if chosen else SURFACE,
                                 outline=ACCENT if chosen else BORDER, radius=10)
            self.text((rect[0] + rect[2]) / 2, 218, title, 16, True,
                      SURFACE if chosen else ACCENT, "center")
            if not chosen:
                callback = self.open_custom if screen == "custom" else self.back_to_choices
                self.action(rect, callback, shape, BORDER)

    def build_choose(self):
        self.choice_heading("Choose your coins")
        self.text(28, 168, "Tap a coin picture to pick a combination, or choose each coin.",
                  13, color=MUTED)
        self.choice_tabs()

        for i, option in enumerate(self.options):
            x, y = 28 + (i % 3) * 252, 244 + (i // 3) * 76
            chosen = i == self.selected
            outline = ACCENT if chosen else BORDER
            shape = self.rounded(x, y, x + 240, y + 68,
                                 fill=TINT if chosen else SURFACE,
                                 outline=outline, line_width=2 if chosen else 1)
            self.payout_pictures(option.plan, x + 38, y + 34,
                                 size=44 if len(option.plan) == 1 else 32, gap=12)
            self.text(x + 77, y + 12, option.title, 18, True,
                      ACCENT_DARK if chosen else TEXT)
            self.text(x + 77, y + 43, option.detail, 11, color=MUTED)
            if chosen:
                self.check_icon(x + 226, y + 12, radius=7)
            self.action((x, y, x + 240, y + 68),
                        lambda index=i: self.select_option(index), shape,
                        outline, 2 if chosen else 1)

        self.text(28, 396, "YOUR COMBINATION", 10, True, MUTED)
        self.text(28, 416, describe(self.options[self.selected].plan), 12,
                  bold=True, width=490)
        self.button((548, 396, 772, 440), "Review exchange",
                    self.confirm_payout, size=17)

    def select_option(self, index):
        if self.screen != "choose" or not 0 <= index < len(self.options):
            return
        self.selected = index
        self.show("choose")

    def open_custom(self):
        if self.screen != "choose" or not self.session.ready:
            return
        self.custom.set_amount(self.amount)
        self.show("custom")

    def build_custom(self):
        self.choice_heading("Build your coin mix")
        self.text(28, 169, "Tap a coin picture to add one, or use the + and − buttons.",
                  13, color=MUTED)
        for i, coin in enumerate(COINS):
            x, y = 28 + (i % 2) * 258, 202 + (i // 2) * 120
            count = self.custom.counts.get(coin, 0)
            outline = ACCENT if count else BORDER
            shape = self.rounded(x, y, x + 246, y + 114,
                         fill=TINT if count else SURFACE,
                         outline=outline, radius=12)
            self.currency_picture("coin", coin, x + 43, y + 53, 64)
            self.text(x + 90, y + 17, money(coin), 21, True)
            self.text(x + 90, y + 47, f"Subtotal {money(coin * count)}", 11,
                      color=ACCENT if count else MUTED)
            can_add = self.custom.remaining >= coin
            picture_hint = ("Tap +1" if can_add else "Complete" if not self.custom.remaining
                            else "Use smaller")
            self.text(x + 43, y + 101, picture_hint, 10 if can_add else 9, True,
                      ACCENT if can_add else MUTED, "center")
            if can_add:
                self.action((x + 8, y + 12, x + 80, y + 108),
                            lambda c=coin: self.adjust_custom(c, 1), shape, outline)
            self.button((x + 88, y + 66, x + 132, y + 110), "−",
                        lambda c=coin: self.adjust_custom(c, -1), primary=False,
                        enabled=count > 0, size=25)
            self.text(x + 161, y + 88, str(count), 22, True, anchor="center")
            self.button((x + 190, y + 66, x + 234, y + 110), "+",
                        lambda c=coin: self.adjust_custom(c, 1),
                        enabled=can_add, size=24)

        self.rounded(552, 202, 772, 305, fill=HEADER)
        self.text(570, 219, "SELECTED / INSERTED", 10, True, HEADER_MUTED)
        self.text(570, 242, f"{money(self.custom.total)} / {money(self.amount)}", 26,
                  True, CTA if self.custom.ready else SURFACE)
        count = sum(self.custom.counts.values())
        self.text(570, 281, f"{count} coin{'s' if count != 1 else ''} selected",
                  12, color=HEADER_MUTED)
        self.button((552, 315, 655, 359), "Clear", self.clear_custom,
                    primary=False, enabled=bool(count), size=14)
        self.button((665, 315, 772, 359), "Fill with ₱1", self.fill_custom,
                    primary=False, enabled=self.custom.remaining > 0, size=11)
        status = ("Your total matches." if self.custom.ready
                  else f"Add {money(self.custom.remaining)} more.")
        self.text(552, 369, status, 14, True,
                  ACCENT if self.custom.ready else GOLD)
        self.button((552, 392, 772, 436), "Review exchange", self.confirm_payout,
                    enabled=self.custom.ready, size=17)

    def adjust_custom(self, coin, delta):
        if self.screen != "custom" or not self.custom.adjust(coin, delta):
            return False
        self.show("custom")
        return True

    def clear_custom(self):
        if self.screen == "custom":
            self.custom.clear()
            self.show("custom")

    def fill_custom(self):
        if self.screen == "custom" and self.custom.fill_remaining():
            self.show("custom")

    def back_to_choices(self):
        if self.screen == "custom":
            self.show("choose")

    def go_back(self):
        if self.screen in ("deposit", "admin"):
            self.go_home()
        elif self.screen == "choose":
            self.back_to_deposit()
        elif self.screen == "custom":
            self.back_to_choices()
        elif self.screen == "review":
            self.pending_plan = {}
            self.show(self.review_origin)

    def back_to_deposit(self):
        if self.screen == "choose":
            self.show("deposit")  # Retains every inserted peso.

    def confirm_payout(self):
        if self.screen == "choose":
            plan = self.options[self.selected].plan
        elif self.screen == "custom":
            plan = self.custom.plan
        else:
            return False
        if not valid_plan(self.amount, plan):
            return False
        self.pending_plan = dict(plan)
        self.review_origin = self.screen
        self.show("review")
        return True

    def build_review(self):
        self.steps(2)
        self.text(28, 139, "Check your coin combination", 27, True)
        self.text(28, 181, "Make sure this is what you want to receive.",
                  13, color=MUTED)
        self.rounded(28, 211, 480, 430, outline=BORDER)
        self.text(50, 233, "COIN", 11, True, MUTED, "w")
        self.text(251, 233, "QUANTITY", 11, True, MUTED, "center")
        self.text(458, 233, "VALUE", 11, True, MUTED, "e")
        self.canvas.create_line(50, 251, 458, 251, fill=BORDER)
        for i, (coin, count) in enumerate(sorted(self.pending_plan.items(), reverse=True)):
            y = 278 + i * 41
            self.currency_picture("coin", coin, 68, y, 32)
            self.text(100, y, money(coin), 21, True, anchor="w")
            self.text(251, y, str(count), 20, True, anchor="center")
            self.text(458, y, money(coin * count), 20, True, anchor="e")
        self.rounded(504, 211, 772, 365, outline=BORDER)
        self.text(524, 232, "AMOUNT INSERTED", 11, True, MUTED)
        self.text(521, 253, money(self.amount), 36, True)
        count = sum(self.pending_plan.values())
        self.text(524, 308, f"{count} coin{'s' if count != 1 else ''} in total",
                  15, color=MUTED)
        self.text(524, 338, "Full value returned.", 13, True, ACCENT)
        self.button((504, 382, 772, 434), "Confirm & dispense",
                    lambda: self.start_dispense(self.pending_plan), size=17)

    def start_dispense(self, plan):
        if self.screen != "review" or not self.session.ready:
            return False
        if not valid_plan(self.amount, plan):
            return False
        if plan != self.pending_plan:
            return False
        self.plan = dict(plan)
        self.coin_queue = [coin for coin, count in sorted(plan.items(), reverse=True)
                           for _ in range(count)]
        self.total_coins = len(self.coin_queue)
        self.dropped = 0
        self.dispensed_value = 0
        self.show("dispensing")
        self.drop_job = self.root.after(COIN_DELAY_MS, self.drop_coin)
        return True

    def build_dispensing(self):
        self.steps(3)
        self.rounded(28, 140, 772, 429, fill=HEADER)
        self.text(400, 164, "PAYOUT IN PROGRESS", 10, True, CTA, "center")
        self.text(400, 202, f"Dispensing {money(self.amount)}", 34, True, SURFACE,
                  anchor="center")
        self.text(400, 240, describe(self.plan), 13, color=HEADER_MUTED, anchor="center")
        self.rounded(103, 271, 697, 361, fill="#08121D", outline="#34465A", radius=12)
        self.canvas.create_line(125, 280, 675, 280, fill=CTA, width=3)
        self.payout_pictures(self.plan, 400, 323, size=64, gap=84)
        self.rounded(94, 382, 706, 392, fill="#34465A", radius=5)
        if self.dropped:
            right = 94 + 612 * self.dropped / self.total_coins
            self.rounded(94, 382, right, 392, fill=CTA, radius=5)
        self.text(400, 412, f"{self.dropped} of {self.total_coins} coins dispensed · Please wait",
                  13, True, SURFACE, anchor="center")

    def drop_coin(self):
        self.drop_job = None
        if self.closed or self.screen != "dispensing":
            return
        # Real hardware must advance on confirmed hopper pulses, not a timer.
        if self.dropped >= self.total_coins:
            return
        self.dispensed_value += self.coin_queue[self.dropped]
        self.dropped += 1
        self.show("dispensing")
        if self.dropped < self.total_coins:
            self.drop_job = self.root.after(COIN_DELAY_MS, self.drop_coin)
        else:
            self.drop_job = self.root.after(600, self.finish)

    def finish(self):
        self.drop_job = None
        if (self.closed or self.screen != "dispensing"
                or self.dropped != self.total_coins
                or self.dispensed_value != self.amount):
            return
        self.completed_amount = self.amount
        self.completed_plan = dict(self.plan)
        self.session.reset()
        self.done_deadline = time.monotonic() + DONE_TIMEOUT_S
        self.show("done")
        self.done_job = self.root.after(DONE_TIMEOUT_S * 1000, self.back_to_idle)

    def build_done(self):
        self.rounded(28, 102, 772, 433, outline=BORDER)
        self.payout_pictures(self.completed_plan, 400, 154, size=64, gap=78)
        self.text(400, 222, "Collect your coins", 31, True, anchor="center")
        count = sum(self.completed_plan.values())
        self.text(400, 267, f"{money(self.completed_amount)} exchanged · "
                  f"{count} coin{'s' if count != 1 else ''}", 18,
                  color=ACCENT, anchor="center")
        self.text(400, 300, describe(self.completed_plan), 14,
                  color=MUTED, anchor="center")
        self.button((239, 342, 561, 394), "Start another exchange",
                    self.back_to_idle, size=17)
        self.done_timer_item = self.text(400, 415, "", 11,
                                         color=MUTED, anchor="center")
        self.update_done_timer()

    def go_home(self):
        if self.screen not in ("deposit", "admin"):
            return
        if not self.amount:
            self.session.reset()
        self.show("idle")

    def back_to_idle(self):
        if self.screen != "done":
            return
        if self.done_job is not None:
            self.root.after_cancel(self.done_job)
            self.done_job = None
        self.plan = {}
        self.pending_plan = {}
        self.custom = CoinCombination()
        self.options = []
        self.show("idle")

    def build_admin(self):
        self.text(28, 109, "Kiosk controls", 29, True)
        self.text(28, 153, "Device controls are available while no exchange is active.",
                  14, color=MUTED)
        items = [
            ("Exit to desktop", self.close),
            ("Restart device", lambda: self.power("reboot")),
            ("Shut down", lambda: self.power("poweroff")),
            ("Back to exchange", self.go_home),
        ]
        for i, (title, callback) in enumerate(items):
            x, y = 28 + i % 2 * 378, 208 + i // 2 * 110
            self.button((x, y, x + 366, y + 90), title, callback,
                        primary=i == 3, size=20)

    def power(self, command):
        if self.screen != "admin" or self.amount or command not in ("reboot", "poweroff"):
            return
        if not os.path.exists("/proc/device-tree/model"):
            messagebox.showinfo("Device controls",
                                "Power controls are available on the Raspberry Pi kiosk.",
                                parent=self.root)
            return
        title = "Restart device" if command == "reboot" else "Shut down"
        if messagebox.askyesno(title, f"{title} now?", parent=self.root):
            try:
                subprocess.Popen(["sudo", "-n", command])
            except OSError as error:
                messagebox.showerror(title, str(error), parent=self.root)
                return
            self.close()

    def on_tap(self, event):
        # Do not allow admin navigation to interrupt an active exchange.
        if self.screen != "idle" or self.amount or event.x > 100 or event.y > 80:
            self.taps = []
            return False
        now = time.monotonic()
        self.taps = [stamp for stamp in self.taps if now - stamp < 3] + [now]
        if len(self.taps) >= ADMIN_TAPS:
            self.taps = []
            self.show("admin")
            return True
        return False

    def on_click(self, event):
        self.canvas.focus_set()
        self.keyboard_focus = False
        if self.on_tap(event):
            return
        for action in reversed(self.actions):
            x1, y1, x2, y2 = action["rect"]
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                action["command"]()
                break

    def clear_hover(self):
        if 0 <= self.hover_index < len(self.actions):
            old = self.actions[self.hover_index]
            self.canvas.itemconfigure(old["shape"], outline=old["outline"],
                                      width=old["line_width"])
        self.hover_index = -1
        self.canvas.configure(cursor="none" if FULLSCREEN else "")

    def on_motion(self, event):
        hit = -1
        for i, action in enumerate(self.actions):
            x1, y1, x2, y2 = action["rect"]
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                hit = i
                break
        if hit == self.hover_index:
            return
        self.clear_hover()
        self.hover_index = hit
        if hit >= 0:
            self.canvas.itemconfigure(self.actions[hit]["shape"], outline=ACCENT,
                                      width=2)
            if not FULLSCREEN:
                self.canvas.configure(cursor="hand2")

    def move_focus(self, direction):
        if self.actions:
            self.keyboard_focus = True
            self.focus_index = ((self.focus_index + direction) % len(self.actions)
                                if self.focus_index >= 0
                                else 0 if direction > 0 else len(self.actions) - 1)
            self.draw_focus()
        return "break"

    def draw_focus(self):
        if self.focus_ring is not None:
            self.canvas.delete(self.focus_ring)
        if 0 <= self.focus_index < len(self.actions):
            x1, y1, x2, y2 = self.actions[self.focus_index]["rect"]
            self.focus_ring = self.canvas.create_rectangle(
                x1 + 4, y1 + 4, x2 - 4, y2 - 4, outline=GOLD, width=2, dash=(3, 3)
            )

    def activate_focus(self, event=None):
        if self.keyboard_focus and 0 <= self.focus_index < len(self.actions):
            self.actions[self.focus_index]["command"]()
        return "break"

    def update_done_timer(self):
        left = max(0, math.ceil(self.done_deadline - time.monotonic()))
        if self.done_timer_item is not None:
            self.canvas.itemconfigure(self.done_timer_item,
                                      text=f"Returning to the start in {left}s")

    def tick(self):
        self.tick_job = None
        if self.closed:
            return
        if self.screen == "done":
            self.update_done_timer()
        self.tick_job = self.root.after(200, self.tick)

    def close(self):
        if self.closed:
            return
        self.closed = True
        for job in (self.tick_job, self.drop_job, self.done_job):
            if job is not None:
                self.root.after_cancel(job)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
