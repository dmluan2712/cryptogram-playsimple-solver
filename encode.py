import ocr_convert
import letter_assignment
import stitch
import os, sys, time
import mode_select

if __name__ == "__main__":
	try:
		stitch.generate_screenshot()
		ocr_convert.convert("temp/merge.png","temp/convert_text.txt")
		#ocr_convert.convert_fix("temp/convert_text.txt","temp/convert_text.txt")
		input("Please correct the script first before proceeding. Press Enter to continue...")
		letter_assignment.letter_assignment("temp/convert_text.txt", "temp/random-assignment-text.txt")
		
		input("Please correct the random text before proceeding. Press Enter to continue...")
		text=""
		with open('temp/random-assignment-text.txt', 'r', encoding='utf-8') as f:
			text=f.read()

		mode_select.type_manual(text)

	except KeyboardInterrupt:
			print("\nKeyboard Interrupt. Program terminated.")
			sys.exit(0)
