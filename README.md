# Cryptogram (PlaySimple) Solver

A simple Python CLI tool designed to automate solving levels 1 through 3000 in the Android game **Cryptogram** by **PlaySimple**. Tested and optimized for the **Samsung S25** ($1080 \times 2340$ resolution).

The program retrieves solutions sourced from [GameAnswer.net](https://www.gameanswer.net/) and inputs them directly onto your device via ADB.

---

## Features

* **Offline & Online Modes**:
  * `type_answer.py`: Uses local data to input answers offline.
  * `type_answer_online.py`: Fetches answers directly online if connected to the internet.
* **Level Selection**: Choose your current level or paste an answer directly.
* **Smart Keyboard Shortcuts**:
  * `→` **(Right Arrow)**: Automatically types the next correct letter on your device.
  * `←` **(Left Arrow)**: Skips a letter if it is already filled in or revealed.
  * `↑` **(Up Arrow)**: Defers/bypasses a blocked letter to solve later once other letters are revealed.

---

## Prerequisites

* **Samsung S25** (or any device with a $1080 \times 2340$ screen resolution)
* **Python 3.x**
* **ADB (Android Debug Bridge)** installed and added to system PATH
* **USB Debugging** enabled on your phone

