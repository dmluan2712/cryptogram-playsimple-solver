import re
import random
import string

def letter_assignment(input_file_path, output_file_path):
	# 1. Read the parsed cryptogram text file
	try:
		with open(input_file_path, 'r', encoding='utf-8') as f:
			content = f.read()
	except FileNotFoundError:
		print(f"⚠️ Could not find the file: {input_file_path}")
		return

	print("--- Current Cryptogram Contents ---")
	print(content)
	print("-----------------------------------\n")

	# Extract all distinct numbers present in the file
	all_numbers = set(re.findall(r'\b\d+\b', content))
	
	# NEW FEATURE: Find letters that are already hardcoded inside the file
	# Excludes question marks, hyphens, spaces, and numbers
	pre_existing_letters = set(re.findall(r'[A-Za-z]', content)) - {'', ' '}
	# Force uppercase representation for consistency in tracking used keys
	pre_existing_letters = {l.upper() for l in pre_existing_letters}
	
	if pre_existing_letters:
		print(f"ℹ️ Found true/pre-existing letters in the file: {', '.join(sorted(pre_existing_letters))}")
		print("   These letters will be strictly skipped during random assignment.\n")

	# 2. Step 1: Interactive Manual Substitutions (Capital Letters)
	substitution_map = {}
	
	# Initialize our tracked letters pool with the ones already found in the file
	used_letters = set(pre_existing_letters)

	print("Step 1: Enter known letter substitutions.")
	print("Known letters will be CAPITALIZED. Random guesses will be lowercase.")
	print("Format example: '17 R' or '5 E'. Type 'no' or 'No' when finished.\n")

	while True:
		user_input = input("Enter substitution (or 'no' to finish): ").strip()
		if user_input.lower() == 'no':
			break
			
		# Validate format using a regex check
		match = re.match(r'^(\d+)\s+([A-Za-z])$', user_input)
		if match:
			num = match.group(1)
			letter = match.group(2).upper() # Force uppercase for known letters
			#letter = match.group(2).lower() # Force uppercase for known letters			

			if num not in all_numbers:
				print(f"⚠️ Number {num} is not present in the cryptogram. Try again.")
				continue
			if letter in used_letters:
				if letter in pre_existing_letters:
					print(f"⚠️ Letter '{letter}' is already native to the file text. Try again.")
				else:
					print(f"⚠️ Letter '{letter}' has already been manually assigned to another number. Try again.")
				continue
				
			substitution_map[num] = letter
			used_letters.add(letter)
			print(f"✅ Mapped {num} -> {letter}")
		else:
			print("❌ Invalid format. Please enter a number followed by a single letter (e.g., '17 R').")

	# 3. Step 2: Randomly assign remaining unmapped numbers (Lowercase Letters)
	unmapped_numbers = list(all_numbers - substitution_map.keys())
	
	# Available pool completely blocks out manually assigned AND pre-existing text letters
	available_letters = list(set(string.ascii_uppercase) - used_letters)
	
	# Shuffle the pool to ensure random assignment
	random.shuffle(available_letters)

	for num in unmapped_numbers:
		if available_letters:
			random_letter = available_letters.pop().lower() # Force lowercase for guesses
			substitution_map[num] = random_letter
			print(f"🎲 Randomly assigned unmapped number: {num} -> {random_letter}")
		else:
			print(f"⚠️ Out of alphabet letters! Could not map number: {num}")

	# 4. Steps 3 & 4: Process the document formatting
	def replace_token(match):
		token = match.group(0)
		if token.isdigit():
			return substitution_map.get(token, token)
		elif token == '-':
			return '' # Remove all hyphens
		return token # Keeps wildcards '?', native letters, and spaces as they are

	# Match numbers, hyphens, or any other sequence (spaces/wildcards/native letters)
	solved_content = re.sub(r'\d+|-|[^0-9\-]', lambda m: replace_token(m), content)
	solved_content = solved_content.lower()

	# 5. Save the output
	with open(output_file_path, 'w', encoding='utf-8') as f:
		f.write(solved_content)

	print(f"\n🎉 Solved text successfully written to: {output_file_path}")
	print("\n--- Solved Output Preview ---")
	print(solved_content)
	print("-----------------------------")

# --- Example Run Execution ---

if __name__ == "__main__":
	letter_assignment('temp/convert_text.txt', 'temp/random-assignment-text.txt')
