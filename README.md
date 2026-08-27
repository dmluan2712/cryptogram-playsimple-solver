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

## OCR & Image Processing Tools

This repository also contains experimental scripts for automated screen processing:

* **`ocr-convert.py`**: Scans the screen to detect numbers representing letters. Assigns a random letter to each unique number set to generate a substituted cipher text. This text can be pasted into 3rd-party cryptogram solvers like [quipqiup.com](https://www.quipqiup.com).
* **`stitch.py`**: Uses computer vision / ML to take two screenshots of equal width, detect their overlapping region, and vertically glue them seamlessly (required to capture long puzzle screens for `ocr-convert.py`).
* **`symbol.py`**: A custom modification of `ocr-convert.py` designed for symbol-based levels. Uses OpenCV template matching against a handmade template set to map recurring symbols to consistent random letter assignments.

---

## Credits & Initial Prompts

The scripts `ocr-convert.py` and `stitch.py` were originally drafted using Google Gemini. Below are the initial prompts used to kick off their development:

### 1. Initial Prompt for `ocr-convert.py`
> *"Write a Python script using OCR to read numbers off an Android screenshot. It should find every unique number, map each unique number to a random letter of the alphabet, and output a substituted cipher string so I can paste it into quipqiup to solve."*

### 2. Initial Prompt for `stitch.py`
> *"Write a Python program using OpenCV to vertically stitch two screenshots together. The images have the exact same width. The script should automatically detect the overlapping area between the bottom of the first image and the top of the second image, trim the overlap, and glue them seamlessly into a single image."*

*(Note: The final versions of these scripts evolved through subsequent iterative prompts and manual adjustments.)*

---

## Prerequisites

* **Samsung S25** (or any device with a $1080 \times 2340$ screen resolution)
* **Python 3.x**
* **ADB (Android Debug Bridge)** installed and added to system PATH
* **USB Debugging** enabled on your phone
