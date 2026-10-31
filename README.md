# D' MARBY Coin Exchanger

Tkinter kiosk app for an 800 x 480 touchscreen. No extra packages needed to run it.

    python dmarby.py              # fullscreen (kiosk)
    python dmarby.py --windowed   # in a window, for testing

Keep `assets.py` and the `fonts/` folder next to `dmarby.py`. On first run the
app installs Plus Jakarta Sans for the current user so every machine looks the same.

## Demo mode
`DEMO_MODE = True` (top of `dmarby.py`) simulates the hardware:
- On any insert screen, the small pills along the bottom insert coins or bills.
  Keyboard works too: `1` `5` `0` `2` = P1/P5/P10/P20 coins, `q` `w` `e` = P20/P50/P100 bills.
- Tap the top-left corner of the welcome screen 5 times for Kiosk controls:
  refill or empty coins, low P5 stock, low GCash float, reject the next bill or coin,
  jam the next payout, fail the next GCash number, and mark a jam fixed.

## Settings worth changing (top of dmarby.py)
- `CONTACT_NUMBER`: shown on the incident screens.
- `START_STOCK`, `GCASH_START_BALANCE`, `GCASH_FEE_RATE`, `GCASH_MAX`.
- Timeouts: `IDLE_EMPTY_S`, `IDLE_MONEY_S`, `PROMPT_S`, `DONE_S`.
- `ALLOW_ESCAPE = False` for the real kiosk so Esc can't close the app.
- `CEBUANO`: add translations as `"English text": "Cebuano text"`. Missing ones fall back to English.

## Log
Every exchange, GCash cash-in, incident (with reference number) and forfeited
timeout is appended to `transactions.log` (one JSON record per line).

## Hardware
The functions to call from the bill validator, coin acceptor and hoppers are
listed at the top of `dmarby.py`. Set `DEMO_MODE = False` once they're wired.

## Changing layouts
If you change a card's size, regenerate its soft shadow:

    pip install pillow
    python tools/make_assets.py

`python tools/tour.py shots/` walks every screen and saves screenshots
(needs ImageMagick's `import`).
