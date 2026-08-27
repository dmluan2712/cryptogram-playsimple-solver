import subprocess
import pynput

# the following suppress the escape sequence of special keys in terminal
import sys, time
import contextlib
import multiprocessing

# Context manager to hide the ANSI escape sequences (^[[A, etc.) in the terminal
@contextlib.contextmanager
def hidden_terminal_input():
	if sys.platform == "win32":
		import msvcrt
		yield
		while msvcrt.kbhit():
			msvcrt.getch()
	else:
		import termios
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			new_settings = termios.tcgetattr(fd)
			new_settings[3] = new_settings[3] & ~termios.ECHO & ~termios.ICANON
			termios.tcsetattr(fd, termios.TCSANOW, new_settings)
			yield
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# --- CONFIGURATION ---
ADB_PATH = "adb" 

def send_tap(x, y):
	"""Sends an ADB tap command to the connected Android device."""
	cmd = [ADB_PATH, "shell", "input", "tap", str(x), str(y)]
	try:
		subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		# print(f"Executed Tap: ({x}, {y})")
	except subprocess.CalledProcessError:
		print("Error: Failed to execute ADB command. Is your device connected?")

def send_swipe(x1, y1, x2, y2, duration_ms=500):
	"""Sends an ADB swipe command to the connected Android device."""
	cmd = [ADB_PATH, "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)]
	try:
		subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		#print(f"Executed Swipe: ({x1}, {y1}) -> ({x2}, {y2})\n")
	except subprocess.CalledProcessError:
		print("Error: Failed to execute ADB command. Is your device connected?")

TAP_MAP = {
	'q': (70, 1720),  'w': (175, 1720), 'e': (280, 1720), 'r': (385, 1720),
	't': (490, 1720), 'y': (595, 1720), 'u': (700, 1720), 'i': (805, 1720),
	'o': (910, 1720), 'p': (1015, 1720), 'a': (120, 1855), 's': (225, 1855),
	'd': (330, 1855), 'f': (435, 1855), 'g': (540, 1855), 'h': (645, 1855),
	'j': (750, 1855), 'k': (855, 1855), 'l': (960, 1855), 'z': (225, 1990),
	'x': (330, 1990), 'c': (435, 1990), 'v': (540, 1990), 'b': (645, 1990),
	'n': (750, 1990), 'm': (855, 1990),
}

def on_press(key):
	try:
		# Check if the pressed character exists in our map
		if key.char in TAP_MAP:
			x, y = TAP_MAP[key.char]
			#print(f"Key {key.char} pressed!\n")
			send_tap(x, y)

	except AttributeError:
		# This handles special keys (like Ctrl, Shift, Esc)
		
		if key == pynput.keyboard.Key.esc:
			print("Esc pressed. Exiting...")
			# Returning False stops the listener loop
			return False

def nav_listener_process(): # separate key binding for navigating up and down
	def on_press(key):
		# Only handle arrow keys
		if key == pynput.keyboard.Key.up:
			send_swipe(1000, 500, 1000, 750, 300)
		
		elif key == pynput.keyboard.Key.down:
			send_swipe(1000, 750, 1000, 500, 300)

	with pynput.keyboard.Listener(on_press=on_press) as listener:
		listener.join()

def main():
	# print("==================================================") # uncomment this to debug
	# print("Android Key Remapper Active (pynput - No Root)")
	# print("Press 'Esc' to exit the script.")
	# print("==================================================")

	# Collect events until released
	with pynput.keyboard.Listener(on_press=on_press) as listener:
		listener.join()

if __name__ == "__main__":
	main()
