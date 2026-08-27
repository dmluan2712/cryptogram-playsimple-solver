import os
import glob
import cv2
import numpy as np

def load_templates(template_dir="symbols"):
	"""
	Loads templates from the specified directory.
	Assumes filename format like '1.png', '13.png', '24.png'.
	Preprocesses them to grayscale/binary matching target dimensions.
	"""
	templates = {}
	if not os.path.exists(template_dir):
		raise FileNotFoundError(f"Template directory '{template_dir}' not found.")

	for filepath in glob.glob(os.path.join(template_dir, "*.png")):
		filename = os.path.basename(filepath)
		name, _ = os.path.splitext(filename)
		
		# Read template image
		img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
		if img is None:
			continue

		# Ensure uniform binary processing (black symbol on white background)
		_, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY| cv2.THRESH_OTSU)
		templates[name] = thresh
		
	return templates

def match_symbol(cropped_symbol, templates, threshold=0.8):
	"""
	Matches a cropped symbol against all loaded templates using normalized cross-correlation.
	Returns the template name with the highest score >= threshold, or None if no match.
	"""
	best_score = -1.0
	best_name = None
	
	crop_h, crop_w = cropped_symbol.shape[:2]

	for name, template in templates.items():
		templ_h, templ_w = template.shape[:2]
		
		# Skip if dimensions are incompatible with cv2.matchTemplate
		if templ_h > crop_h or templ_w > crop_w:
			# Resize template slightly if width exceeds target crop width
			if templ_h == crop_h and templ_w > crop_w:
				resized_template = cv2.resize(template, (crop_w, crop_h))
			else:
				continue
		else:
			resized_template = template

		res = cv2.matchTemplate(cropped_symbol, resized_template, cv2.TM_CCOEFF_NORMED)
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

		if max_val > best_score:
			best_score = max_val
			best_name = name

	if best_score >= threshold:
		return best_name
	return None

def process_and_convert_symbols(image_path="temp/merge.png", symbol_dir="symbols", output_path="temp/convert_text.txt"):
	# 1. Load Templates
	templates = load_templates(symbol_dir)
	if not templates:
		print("No valid templates found in 'symbols/' folder.")
		return

	# 2. Load and Preprocess Input Image
	img = cv2.imread(image_path)
	if img is None:
		raise FileNotFoundError(f"Could not load image: {image_path}")

	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	_, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
	
	# Noise removal
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
	thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

	# 3. Find Contours
	contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	MAX_CHAR_HEIGHT = 38 
	MIN_CHAR_HEIGHT = 14
	MAX_CHAR_WIDTH = 38
	ISOLATION_TARGET_HEIGHT = 100

	detected_symbols = []

	# 4. Filter contours and match against templates
	for contour in contours:
		x, y, w, h = cv2.boundingRect(contour)

		if MIN_CHAR_HEIGHT < h <= MAX_CHAR_HEIGHT and 2 < w <= MAX_CHAR_WIDTH:
			# Crop symbol with minimal padding
			y_start = max(0, y - 1)
			y_end = min(thresh.shape[0], y + h)
			x_start = max(0, x - 1)
			x_end = min(thresh.shape[1], x + w)
			
			# Crop from inverted threshold image
			char_crop_inv = thresh[y_start:y_end, x_start:x_end]

			# Invert back to dark symbol on white background
			char_crop = cv2.bitwise_not(char_crop_inv)
						
			# Zoom crop to fixed 100px height maintaining aspect ratio
			h_crop, w_crop = char_crop.shape[:2]
			scale_factor = ISOLATION_TARGET_HEIGHT / float(h_crop)
			new_width = max(1, int(w_crop * scale_factor))
			
			# Upscale and apply slight sharpening for cleaner edges
			resized_crop = cv2.resize(char_crop, (new_width, ISOLATION_TARGET_HEIGHT), interpolation=cv2.INTER_LANCZOS4)
			resized_crop  = cv2.GaussianBlur(resized_crop , (0,0), 1)
			resized_crop  = cv2.addWeighted(resized_crop , 1.5, resized_crop , -0.5, 0)
			
			#cv2.imwrite(f"temp/{y_start}-{x_start}.png", resized_crop) ### uncomment to debug or to create template
			
				
			# Match against templates (threshold 0.8)
			matched_name = match_symbol(resized_crop, templates, threshold=0.8)

			if matched_name is not None:
				# Store matched symbol with original bounding box coordinates
				detected_symbols.append({
					'name': matched_name,
					'x': x,
					'y': y,
					'w': w,
					'h': h
				})

	# 5. Structure Symbols into Lines (Line jump distance >= 30px)
	# Sort top-to-bottom first
	detected_symbols.sort(key=lambda item: item['y'])

	lines = []
	for symbol in detected_symbols:
		if not lines:
			lines.append([symbol])
		else:
			# Compare current symbol y with average y of the current line
			current_line_y = np.mean([s['y'] for s in lines[-1]])
			if abs(symbol['y'] - current_line_y) >= 30:
				# Distance >= 30px means a new line
				lines.append([symbol])
			else:
				lines[-1].append(symbol)

	# 6. Format Output String Following Spacing Rules
	final_output_lines = []

	for line in lines:
		# Sort left-to-right within line
		line.sort(key=lambda item: item['x'])

		line_str = ""
		for i in range(len(line)):
			curr = line[i]
			line_str += curr['name']

			if i < len(line) - 1:
				nxt = line[i + 1]
				# Distance between right edge of current symbol and left edge of next
				gap = nxt['x'] - (curr['x'] + curr['w'])

				if gap < 40:
					line_str += "-"
				else:
					line_str += " "

		final_output_lines.append(line_str)

	result_string = "\n".join(final_output_lines)

	# 7. Print and Save Results
	print("--- Extracted Symbol Text ---")
	print(result_string)

	os.makedirs(os.path.dirname(output_path), exist_ok=True)
	with open(output_path, "w", encoding="utf-8") as f:
		f.write(result_string)

if __name__ == "__main__":
	process_and_convert_symbols()
