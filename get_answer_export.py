import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}


def extract_between_entities(i, url, output_file="output.txt"):
	try:
		# Download webpage
		response = requests.get(url, timeout=15, headers=headers)
		response.raise_for_status()

		html = response.text

		# Pattern to match text between &#8220; ... &#8221;
		pattern = r'&#8220;(.*?)&#8221;'

		matches = re.findall(pattern, html, flags=re.DOTALL)

		# Clean whitespace
		matches = [m.strip() for m in matches if m.strip()]

		# Save to file
		with open(output_file, "a", encoding="utf-8") as output_text: #"a" stands for append
			for text in enumerate(matches, start=1):
				output_text.write(f"[{i}] {text[1]}\n")

		#print(f"Extracted {len(matches)} text blocks.")
		#print(f"Saved to '{output_file}'.")

	except requests.RequestException as e:
		print(f"Error downloading webpage: {e}")

def replace_html_entities(input_file, output_file):
    # Mapping of HTML entities to Unicode characters
    replacements = {
        "&#8211;": "–",   # en dash
		"&#8211;": "—",   # em dash
        "&#8230;": "…",   # ellipsis
        "&#8216;": "'",   # left single quotation mark
        "&#8217;": "'",   # right single quotation mark
		"&#8220;": '"',   # double quotation mark
    }

    # Read the input file
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    # Perform all replacements
    for entity, char in replacements.items():
        text = text.replace(entity, char)

    # Write the output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Processed file saved as '{output_file}'.")


if __name__ == "__main__":
	i_min = 1
	i_max = 2387
	for i in range (i_min,i_max+1):
		open("output.txt", "a").close()        # clear existing text
		url = "".join(["https://www.gameanswer.net/playsimple-cryptogram-level-",str(i)])
		extract_between_entities(i, url)
	name = str(i_min)+"-"+str(i_max)+".txt"
	replace_html_entities(input_file = "output.txt", output_file = name)	
	print(f"Saved to {name}")
