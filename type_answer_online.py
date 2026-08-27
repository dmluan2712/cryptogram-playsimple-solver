import time, sys
import pyautogui
from keybind import send_tap, nav_listener_process # global moving up and down function
from mode_select import enter_answer
import os
from snapshot import capture_direct_android_snapshot, detect_logo

import multiprocessing
from next_action import start_level


def type_answer(level):
	confirm = ""
	
	# start parallel processes
	while True:
		try:			
			if not confirm.lower() in ["", "reload", "r"]:
				print("Program terminated.")
				break			

			while confirm.lower() in ["", "reload", "r"]:
				# Define FRESH processes that need to be run in parallel: detect buttons, navigations
				p_nav = multiprocessing.Process(target=nav_listener_process, daemon=True) # turn on the navigation at all time
				p_start_level = multiprocessing.Process(target=start_level, daemon=True) # turn on the detect start/continue button at all time
				
				# start the parallel processes
				p_nav.start() 
				p_start_level.start()
				
				if confirm == "":
					enter_answer(level)
					input(pyautogui.press("enter")) #flush keystrokes from last round		

					# terminate the processes
					p_nav.kill() 
					p_start_level.kill()
		
					# Properly clean up the system resources (preventing "zombie" processes).
					p_nav.join() 
					p_start_level.join()						

					level += 1
					os.system('clear')
					confirm = input(f"\nNext level [{level}]? Press Enter for Yes, or type 'Reload' or 'r' to reload level, or type something else to quit: ").strip()
	
				else: # confirm.lower()  in ["reload", "r"]:	
					capture_direct_android_snapshot("temp/test-restart.png", 400, 1110, 280, 80) # catch if the restart button is there and click it (spend 50 gold)
					if detect_logo("temp/test-restart.png", "templates/restart.png"):
						send_tap(540,1120) # press the restart button
					
					print(f"Retry level {level-1}...")
					enter_answer(level-1)
					input(pyautogui.press("enter")) #flush keystrokes from last round					
					
					# terminate the processes
					p_nav.kill() 
					p_start_level.kill()
					
					# Properly clean up the system resources (preventing "zombie" processes).
					p_nav.join() 
					p_start_level.join()					
					
					os.system('clear')
					confirm = input(f"\nNext level [{level}]? Press Enter for Yes, or type 'Reload' or 'r' to reload level, or type something else to quit: ").strip()						

				
		except KeyboardInterrupt:
			print("\nKeyboard Interrupt. Program terminated.")
			sys.exit(0)
	
if __name__ == "__main__":
	level = int(input("Please enter level (cycle repeats after 1193 levels): "))
	shift = input("Do you want to shift level down by 1193? Press Enter for yes and type something else for no.").strip()
	if shift == "": 
		level -= 1193 # cycle repeats after 1193 levels
		print(f"New level is {level}.")
	type_answer(level)
	

	
