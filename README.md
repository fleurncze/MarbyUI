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