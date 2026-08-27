from snapshot import capture_direct_android_snapshot, detect_logo
from keybind import send_tap
import time, sys

def open_level():			
	# click the play button if it is there	
	capture_direct_android_snapshot("temp/test-logo.png", 290, 1240, 500, 160) # catch if main logo is there to click the play/ continue button
	
	if detect_logo("temp/test-logo.png", "templates/logo.png") or detect_logo("temp/test-logo.png", "templates/logo-light.png"):
		# Load next level: check if the start button is there to tap
		send_tap(540,1845) # next level begin button	


def start_level():			
	# click the play button if it is there	
	capture_direct_android_snapshot("temp/test-logo.png", 290, 1240, 500, 160) # catch if main logo is there to click the play/ continue button
	
	while True:
		try:			
			# the next button can move around :(	
			capture_direct_android_snapshot("temp/test-next-one.png", 420, 1960, 265, 90) # catch if the next button is at position one				
			capture_direct_android_snapshot("temp/test-next-two.png", 420, 1870, 265, 90) # catch if the next button is at position two					
			capture_direct_android_snapshot("temp/test-back.png", 50, 173, 60, 70) # catch if the back button from the info page is there								

			capture_direct_android_snapshot("temp/test-race.png", 440, 1560, 200, 90) # catch if the play button from the boat race is there
			capture_direct_android_snapshot("temp/test-collect.png", 390, 2030, 300, 80) # catch if the collect button from the boat race is there								
			capture_direct_android_snapshot("temp/test-continue.png", 380, 2030, 320, 80) # catch if the collect button from the boat race is there					
			capture_direct_android_snapshot("temp/test-result.png", 395, 1590, 290, 90) # catch if the collect button from the boat race is there				

			if detect_logo("temp/test-next-one.png", "templates/next.png"): 
				send_tap(540,2000) # level-finish screen proceed button		
				time.sleep(1)

			
			elif detect_logo("temp/test-next-two.png", "templates/next-two.png"):
				send_tap(540,1930) # level-finish screen proceed button
				time.sleep(1) 

			elif detect_logo("temp/test-race.png", "templates/race.png") or detect_logo("temp/test-result.png", "templates/result.png"):	
				send_tap(540,1600) # tap the race play/result button on the boat rate page
				time.sleep(1) 
	
			elif detect_logo("temp/test-collect.png", "templates/collect.png") or detect_logo("temp/test-continue.png", "templates/continue.png"):	
				send_tap(540,2050) # tap the collect/continue button on the boat rate result page
				time.sleep(1) 

			elif detect_logo("temp/test-back.png", "templates/back.png"):	
				send_tap(70,210) # tap the back button on the info page
				time.sleep(1) 

			else:
				open_level()
				
		except KeyboardInterrupt:
			sys.exit(0)

