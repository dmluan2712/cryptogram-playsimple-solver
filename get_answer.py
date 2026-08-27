import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}


def extract_between_entities(url):
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
		
		return matches[0]

	except requests.RequestException as e:
		print(f"Error downloading webpage: {e}")
		
def replace_html_entities(input_text):
	# Mapping of HTML entities to Unicode characters
	replacements = {
		"&#8211;": "–",   # en dash
		"&#8211;": "—",   # em dash
		"&#8230;": "…",   # ellipsis
		"&#8216;": "'",   # left single quotation mark
		"&#8217;": "'",   # right single quotation mark
		"&#8220;": '"',   # double quotation mark
	}
	
	text = input_text	
	
	# Perform all replacements
	for entity, char in replacements.items():
		text = text.replace(entity, char)
	return text

def get_text(level):
	url = "".join(["https://www.gameanswer.net/playsimple-cryptogram-level-",str(level)])
	text = extract_between_entities(url)
	text = replace_html_entities(text)
	return text
