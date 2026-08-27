import cv2
import easyocr
import numpy as np
import os
import glob

# 1. Initialize EasyOCR globally
try:
	reader = easyocr.Reader(['en'], gpu=True)
	print("🚀 EasyOCR initialized on NVIDIA GPU.")
except Exception as e:
	print("⚠️ GPU failed, using CPU.", e)
	reader = easyocr.Reader(['en'], gpu=False)

def load_templates(template_dir="symbols"):
	"""Loads all reference letter images from the templates folder."""
	templates = {}
	template_paths = glob.glob(os.path.join(template_dir, "*.png"))
	
	for path in template_paths:
		# Extract the letter character from the filename (e.g., "A.png" -> "A")
		letter = os.path.splitext(os.path.basename(path))[0]
		template_img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
		# cv2.imwrite(f"temp/{letter}.png",template_img) ### uncomment to debug
		if template_img is not None:
			templates[letter] = template_img
			
	return templates

def easy_ocr(image_file, ISOLATION_PADDING = 10, ISOLATION_TARGET_HEIGHT = 150): # using easy_ocr to read the letter in the reference square
	try:
		# A. Convert image to matrix
		gray = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)		
	
		# B. Add extensive white padding (forces model to see isolated glyph)
		p = ISOLATION_PADDING
		padded_char = cv2.copyMakeBorder(gray, p, p, p, p, cv2.BORDER_CONSTANT, value=[255, 255, 255])
		
		# C. Upscale to fixed 150px high target
		h_pad, w_pad = padded_char.shape
		scale_factor = ISOLATION_TARGET_HEIGHT / h_pad
		new_width = int(w_pad * scale_factor)
		
		# Upscale and apply slight sharpening for cleaner edges
		final_isolated_img = cv2.resize(padded_char, (new_width, ISOLATION_TARGET_HEIGHT), interpolation=cv2.INTER_LANCZOS4)
		
		# cv2.imwrite("temp/temp_char_3.png",final_isolated_img) ### uncomment to debug
	
		# Run GPU EasyOCR
		ocr_result = reader.readtext(
				final_isolated_img,
				allowlist='0123456789',
				text_threshold = 0.7,
				low_text = 0.3,
				#mag_ratio=2.0, # upscale by 2
				detail=0, # Detail=0 means just return the raw text list
			)
		
		if ocr_result:
			detected_letter = ocr_result[0].strip()
		else:
			detected_letter =""
					
	except Exception as e:
		print(f"Error during EasyOCR fallback on {image_file}: {e}")
		detected_letter = ""

	return detected_letter

# detect the letter in the white reference cell
def detect_single(image_file, confidence_threshold = 0.8, ISOLATION_PADDING = 10, ISOLATION_TARGET_HEIGHT = 150):
	"""
	Template Matching for white cells on grid
	Tries Template Matching first. If confidence is below the threshold,
	falls back to GPU EasyOCR.
	"""
	# Load your template library
	templates = load_templates()
	
	best_match_letter = "?"
	
	# Read snapshot in grayscale for template verification
	img_gray = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
	img_gray = cv2.resize(img_gray, (img_gray.shape[1] * 100 // img_gray.shape[0] , 100))
	_, thresh = cv2.threshold(img_gray, 180, 255, cv2.THRESH_BINARY| cv2.THRESH_OTSU)	
	

	# Crop from inverted threshold image
	char = thresh[:,:]
	# cv2.imwrite("temp/temp_char_2.png", char)	### uncomment to debug
	highest_score = -1.0
	
	# 1. STEP 1: Attempt Template Matching (if templates exist)
	if templates:
		for letter, template in templates.items():
			# Run pixel matrix matching	

			result = cv2.matchTemplate(char, template, cv2.TM_CCOEFF_NORMED)
			_, max_val, _, _ = cv2.minMaxLoc(result)
			
			if max_val > highest_score:
				highest_score = max_val
				if not letter in ["31","32"]:
					best_match_letter = letter

		if highest_score >= confidence_threshold:
			# print(f"[{image_file}] Match Found via Templates folder: '{best_match_letter}' (Confidence: {highest_score:.2f})") ### uncomment this to debug
			detected_letter = best_match_letter 
		
		# 2. STEP 2: Evaluate Result & Fallback if necessary
		else:
			# print('Image does not match any letter in Templates. Attempt to use EasyOCR') ### uncomment for debugging
			detected_letter = easy_ocr(image_file)	

	else:
		print('Templates folder not found. Attempt to use EasyOCR.')
		detected_letter = easy_ocr(image_file)
		
	return detected_letter

def detect_digits_custom_pipeline(image_path):
	"""
	Implements the custom pipeline: Find small boxes, crop with padding, 
	upscale, OCR in isolation, and return raw characters with 
	original (unscaled) coordinates.
	"""

	# 2. Load original image
	img = cv2.imread(image_path)
	if img is None:
		raise FileNotFoundError(f"Could not load image: {image_path}")
	
	# 3. Standard OpenCV preprocessing to find characters
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	# Binary inverse thresholding (makes digits white on black)
	# Using 180 threshold to keep it clean and robust for dark/light images
	_, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
	
	# Optional: Noise removal (useful if image quality varies)
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
	thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

	# 4. Find contours
	contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	
	# --- CONFIGURATION (BEFORE UPSCALE) ---
	MAX_CHAR_HEIGHT = 30 
	MIN_CHAR_HEIGHT = 20
	MAX_CHAR_WIDTH = 30
	# Custom pipeline upscaling config
	ISOLATION_PADDING = 10
	ISOLATION_TARGET_HEIGHT = 150
	# --------------------------------------

	detected_characters = []
	
	# 5. Filter contours and process in isolation
	for contour in contours:
		x, y, w, h = cv2.boundingRect(contour)

		# Apply your filters (ignore noises or full lines)
		if h <= MAX_CHAR_HEIGHT and w <= MAX_CHAR_WIDTH and h > MIN_CHAR_HEIGHT and w > 2:
			
			# --- CUSTOM PIPELINE: Begin Isolation ---
			
			# A. Crop to border with minimal 1px safety margin
			y_start = max(0, y-1)
			y_end = min(thresh.shape[0], y+h+1)
			x_start = max(0, x-1)
			x_end = min(thresh.shape[1], x+w+1)
			
			_, img_bw = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) #convert to black number on white background
			char_crop = img_bw[y_start:y_end, x_start:x_end]
			
			cv2.imwrite(f"temp/temp_char.png",char_crop) ### uncomment to debug			
			# cv2.imwrite(f"temp/temp_char_{y_start}_{x_start}.png",char_crop) ### uncomment to debug
			
	
			# Run OCR on ONLY this isolated, upscaled digit
			digit_results = detect_single(f"temp/temp_char.png")			
			# digit_results = detect_single(f"temp/temp_char_{y_start}_{x_start}.png") ### uncomment to debug
			
			# Store results using ORIGINAL (Pre-upscale) coordinates
			if digit_results:
				raw_text = "".join(digit_results).strip()
				if raw_text:
					detected_characters.append({
						'x_start': x,
						'x_end': x + w,
						'y_mid': y + (h // 2),
						# Use the literal text recognized in isolation
						'text': raw_text[:]
					})
					
			# --- End Custom Pipeline ---
	return detected_characters

def convert(input_image_path, save_file):
	"""
	Uses the custom pipeline and rebuilds the cryptogram logic 
	using thresholds adjusted back to ORIGINAL coordinate space.
	"""
	# 1. Detect characters in isolation (using original coordinates)
	t0 = cv2.getTickCount()
	raw_elements = detect_digits_custom_pipeline(input_image_path)
	if not raw_elements:
		print("⚠️ No characters detected.")
		return
		
	t1 = cv2.getTickCount()
	process_time = (t1 - t0) / cv2.getTickFrequency()
	print(f"✅ Found {len(raw_elements)} characters in {process_time:.2f}s")

	# 2. Adjust thresholds back to ORIGINAL coordinate space (No scaling required in Step 7)
	# Distance between numbers of the SAME word
	SAME_WORD_MIN = 10  
	# Threshold where it becomes a new word (Space)
	SAME_WORD_MAX = 60	
	# Vertical distance to define a single row
	ROW_HEIGHT_THRESHOLD = 15

	# 3. Group into lines vertically (Same as original script)
	raw_elements = sorted(raw_elements, key=lambda e: e['y_mid'])
	rows = []
	current_row = [raw_elements[0]]
	
	for e in raw_elements[1:]:
		if abs(e['y_mid'] - current_row[-1]['y_mid']) < ROW_HEIGHT_THRESHOLD:
			current_row.append(e)
		else:
			rows.append(current_row)
			current_row = [e]
	
	rows.append(current_row)

	# 4. Apply horizontal spacing logic and line generation
	final_lines = []
	for row in rows:
		# Important: Rule (1) 'Internal Digit Merging' is completely REMOVED.
		# Every element in 'row' is already a complete multi-digit number,
		# or a single character forced by isolation.

		row = sorted(row, key=lambda e: e['x_start'])
		row_output = ""
		
		for i, current in enumerate(row):
			if i == 0:
				row_output += current['text']
			else:
				prev = row[i-1]
				gap = current['x_start'] - prev['x_end']
				
				# Apply spacing logic precisely based on visual gaps
				if SAME_WORD_MIN <= gap <= SAME_WORD_MAX:
					row_output += "-" + current['text']  # +'('+str(current['y_mid'])+'-'+str(current['x_start'])+')' ### uncomment to debug
				elif gap > SAME_WORD_MAX:
					row_output += " " + current['text']  # +'('+str(current['y_mid'])+'-'+str(current['x_start'])+')' ### uncomment to debug
				else:
					# Gaps smaller than SAME_WORD_MIN (e.g. 10px in original space)
					# For this game, distinct numbers are separated by symbols, 
					# so a tiny gap usually implies an artifact or an un-detected 
					# hyphen, but we treat it as same word here to be safe.
					row_output += current['text']  # +'('+str(current['y_mid'])+'-'+str(current['x_start'])+')' ### uncomment to debug
		if len(row_output) > 2:			
			final_lines.append(row_output)
		
	# 5. Output results
	output_text = "\n".join(final_lines)
	with open(save_file, 'w', encoding='utf-8') as f:
		f.write(output_text)
		
	print(f"✨ Conversion complete. Saved to: {save_file}")
	print("\nPreview of output:")
	print(output_text)

# Example run
if __name__ == "__main__":
	import tkinter as tk
	from tkinter import filedialog

	# Optional: Simple image selector UI if you have tkinter installed
	root = tk.Tk()
	root.withdraw()
	img_path = filedialog.askopenfilename(title="Select merge.png", filetypes=[("PNG files", "*.png")])
	
	if img_path:
		# Default save path
		output_path = os.path.join(os.path.dirname(img_path), "convert_text.txt")
		convert(img_path, output_path)
