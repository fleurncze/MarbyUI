<<<<<<< HEAD
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
=======
# D'MARBY System
### Multi-Denomination Automatic Reversal & Banking Yield System

D'MARBY is a self-service automated money-changing kiosk designed to provide convenient access to coin exchange and GCash cash-in services within the University of Science and Technology of Southern Philippines (USTP) campus.

The system aims to address the common problem of students having difficulty obtaining exact change when paying for transportation, cafeteria purchases, and other everyday transactions.

## Project Overview

D'MARBY provides an automated solution that allows users to exchange paper bills for selected coin denominations and perform GCash cash-in transactions through a touchscreen interface.

By integrating a Raspberry Pi, bill acceptor, coin selector, and automated dispensing mechanism, the system reduces the need for manual assistance while making everyday cash transactions more convenient.

## Features

### 1. Automated Bill-to-Coin Exchange
- Accepts ₱20, ₱50, and ₱100 bills.
- Allows users to select their preferred coin denominations.
- Automatically dispenses the corresponding change.

### 2. Flexible Coin Dispensing
Supports the following denominations:
- ₱1
- ₱2
- ₱5
- ₱10
- ₱20

### 3. GCash Cash-In
- Allows users to insert physical cash for GCash cash-in transactions.
- Supports transactions ranging from ₱20 to ₱500.
- Applies a 1% service fee.

### 4. Balance and Denomination Monitoring
- Displays the available coin denominations.
- Shows the corresponding quantities of available coins.
- Allows users to check machine inventory before proceeding with a transaction.

### 5. Touchscreen User Interface
- Provides a self-service transaction interface.
- Includes separate menus for coin exchange, money breakdown, money combination, GCash cash-in, and available balance.
- Allows users to navigate transaction options through a touchscreen display.

## Hardware Components

The system utilizes the following hardware components:

| Component | Purpose |
|---|---|
| Raspberry Pi 4B | Main processing unit |
| 7-inch DSI Touchscreen Display Module | User interface and transaction selection |
| 4-Channel PC817 Optocoupler Module | Signal isolation |
| TB74 Bill Acceptor | Detects and accepts paper bills |
| Universal Coin Slot | Coin input and detection |
| 16-Channel PWM Servo Driver | Controls servo motors |
| 4× MG90 Metal-Gear Servos | Automated coin dispensing mechanism |

## System Operation

The general operation of D'MARBY follows these steps:

1. The user interacts with the system through the touchscreen display.
2. The user selects either coin exchange or GCash cash-in.
3. For coin exchange, the user inserts an accepted bill and selects the desired denominations.
4. The system processes the transaction and activates the dispensing mechanism.
5. For GCash cash-in, the user inserts the desired amount within the supported transaction range.
6. The system processes the selected operation.

## User Interface

The system includes the following graphical user interface (GUI) screens:

- **Main Menu** – Displays the available transaction options.
- **Change Menu** – Provides access to coin exchange functions.
- **Money Breakdown** – Allows users to exchange bills for selected coin denominations.
- **Money Combine** – Provides the money combination interface.
- **GCash Cash-In** – Handles GCash cash-in transactions.
- **Available Balance** – Displays the machine's available coin inventory.

## Technologies and Platforms

- **Raspberry Pi 4B** – Main embedded computing platform.
- **Servo Motor Control** – Used for automated coin dispensing.
- **Touchscreen Interface** – Used for user interaction.
- **Electronic Sensors and Modules** – Used for bill and coin detection.

## Project Information

| Detail | Description |
|---|---|
| Project Name | D'MARBY System |
| Course | CPE 411 |
| Program | Bachelor of Science in Computer Engineering |
| Section | CPE 4A |
| Group | Group 1 |
| Institution | University of Science and Technology of Southern Philippines |

## Project Purpose

D'MARBY aims to make everyday cash transactions more convenient by providing students with accessible coin exchange and GCash cash-in services. Through embedded system integration and automated money handling, the project presents an alternative to traditional manual money-changing methods.

---

**Developed as an academic embedded systems project by CPE 4A - Group 1.**
>>>>>>> ec2e110c98485c7ed57d715a5ef6f91fddb35f4d
