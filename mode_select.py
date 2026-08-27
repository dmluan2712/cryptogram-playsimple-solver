import time
import pyautogui
import pynput
from get_answer import get_text 
import keybind
import os
from keybind import hidden_terminal_input

import multiprocessing

def transform_string(text: str) -> str:
	main_chars = []
	bracket_chars = []
	
	paren_depth = 0
	bracket_depth = 0
	
	for char in text.lower():
		if char == '(':
			paren_depth += 1
		elif char == ')':
			if paren_depth > 0:
				paren_depth -= 1
		elif char == '[':
			bracket_depth += 1
		elif char == ']':
			if bracket_depth > 0:
				bracket_depth -= 1
		elif char.isalpha():
			# Only process letters
			if paren_depth > 0:
				# Letters inside parentheses are discarded
				continue
			elif bracket_depth > 0:
				# Letters inside brackets are saved for the end
				bracket_chars.append(char)
			else:
				# Regular letters stay in place
				main_chars.append(char)
				
	return "".join(main_chars) + "".join(bracket_chars)
	
def type_auto(text, delay=0.00):
	"""
	Reads a text file and types only lowercase English letters (a-z),
	skipping all other characters.
	"""	
	text = transform_string(text)

	def on_press(key):
		try:
			# type the answer, or quit
			if key == pynput.keyboard.Key.enter:
				print ("The anwer will be typed in 3 seconds...")
				time.sleep(3)
				for char in text.lower():
					if char.isalpha():	
						pyautogui.write(char)
						x, y = keybind.TAP_MAP[char]
						keybind.send_tap(x, y)
						#time.sleep(delay)
				print ("Finish.")							
				input(pynput.keyboard.Key.enter) #flush the text after typing 	
				return False # stop keyboard listerner		

			elif key == pynput.keyboard.Key.esc:
				print("Stopped.")
				return False # stop keyboard listerner 
			
		except Exception as e:
			print(e)

	with pynput.keyboard.Listener(on_press=on_press) as listener:
		listener.join()

def type_manual(text):
	"""
	Manual typing mode.

	Space  -> type the current letter and move to the next letter.
	Right  -> skip the current letter and move to the next letter.
	Esc	-> quit.
	"""	

	# Keep only lowercase English letters
	text = "".join(c for c in text.lower() if 'a' <= c <= 'z')

	print(f"{len(text)} letters loaded.")
	print("RIGHT = type letter")
	print("LEFT = skip letter, not saving")
	print("UP = skip letter, saving and printing it out later")	
	print("DOWN = swipe to see more things below")
	print("ESC = quit")

	index = 0
	length = len(text)
	
	def on_press(key):
		nonlocal index
		nonlocal length
		nonlocal text			
	
		if index >= length:
			print("\nFinished!")
			return False  # Stop listener

		try:
			# Check if the pressed character exists in our map
			if key.char in keybind.TAP_MAP:
				x, y = keybind.TAP_MAP[key.char]
				#print(f"Key {key.char} pressed!\n")
				keybind.send_tap(x, y)		
	
		except AttributeError: # handling special keys for manual typing
			if key == pynput.keyboard.Key.right:
				x, y = keybind.TAP_MAP[text[index]]
				keybind.send_tap(x, y)
				index += 1

			elif key == pynput.keyboard.Key.space:
				text += text[index]				
				#print(text[index], end = ' ') # turn on to debug							
				index += 1
				length += 1
			
			elif key == pynput.keyboard.Key.left:		
				index += 1	
	
			elif key == pynput.keyboard.Key.esc:
				print("Stopped.")
				return False

		except Exception as e:
			print(e)

	with hidden_terminal_input():
		print("Listening... Press ESC to exit.")
		with pynput.keyboard.Listener(on_press=on_press) as listener:
			listener.join()

def enter_answer(level):
	text = get_text(level)
	while True:
		try:			
			mode = input("Choose your mode, [a]uto [1] or manual [0] (default): ")
			if str(mode).lower() in ["1", "auto", "a", "0", "manual", "m", ""]:
				break		
			else:
				print ("Invalid mode.", end = " ")
		except ValueError:
			print("Invalid input!", end = " ")
	if str(mode).lower() in ["1", "auto", "a"]:
		print("Press Enter and switch to the target window to continue; the answer will be typed in 3 seconds after you press Enter.\nOr, press Escape to quit.")
		type_auto(text)
	else:
		type_manual(text)	

def enter_answer_offline(text):
	while True:
		try:
			mode = input("Choose your mode, [a]uto [1] or manual [0] (default): ")
			if str(mode).lower() in ["1", "auto", "a", "0", "manual", "m", ""]:
				break		
			else:
				print ("Invalid mode.", end = " ")
		except ValueError:
			print("Invalid input!", end = " ")
	if str(mode).lower() in ["1", "auto", "a"]:
		print("Press Enter and switch to the target window to continue; the answer will be typed in 3 seconds after you press Enter.\nOr, press Escape to quit.")
		type_auto(text)
	else:
		type_manual(text)
	

	
