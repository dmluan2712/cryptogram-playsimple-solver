import torch
import torch.nn.functional as F
from PIL import Image
import torchvision.transforms.functional as TF
import time

import os
import sys
from pynput import keyboard


# Import your predefined function from snapshot.py
from snapshot import capture_direct_android_snapshot

def find_best_vertical_overlap_gpu(img1_tensor, img2_tensor, max_overlap=800, min_overlap=50):
	"""
	Finds the exact pixel overlap between the bottom of img1 and top of img2.
	Uses normalized variance tracking to prevent flat color lines from tricking the tracker.
	"""
	_, h1, w1 = img1_tensor.shape
	_, h2, w2 = img2_tensor.shape
	
	# Restrict overlap check to actual image boundary limits
	actual_max_overlap = min(max_overlap, h1, h2)
	
	best_mse = float('inf')
	best_overlap = 0
	
	# Start loop from min_overlap instead of 1 to ignore deceptive 1-2px border lines
	for overlap in range(min_overlap, actual_max_overlap + 1):
		# Extract the bottom 'overlap' rows of image 1
		slice1 = img1_tensor[:, -overlap:, :]
		# Extract the top 'overlap' rows of image 2
		slice2 = img2_tensor[:, :overlap, :]
		
		# Calculate standard Mean Squared Error
		mse = F.mse_loss(slice1, slice2).item()
		
		# Normalize the MSE against the slice size variance to ensure large complex 
		# graphic matches aren't mathematically penalized over flat colors
		variance = torch.var(slice1).item() + 1e-5
		normalized_score = mse / variance
		
		if normalized_score < best_mse:
			best_mse = normalized_score
			best_overlap = overlap
			
	# Fallback safety: If no good match was found above min_overlap, 
	# check the small window as a last resort.
	if best_overlap == 0:
		for overlap in range(1, min_overlap):
			slice1 = img1_tensor[:, -overlap:, :]
			slice2 = img2_tensor[:, :overlap, :]
			mse = F.mse_loss(slice1, slice2).item()
			if mse < best_mse:
				best_mse = mse
				best_overlap = overlap

	return best_overlap

def stitch_vertical_images(img1_path, img2_path, output_path, max_overlap=800):
	# Set device to GPU if available
	device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
	print(f"Running stitching routine on: {device}")
	
	# Load images with PIL
	img1 = Image.open(img1_path).convert('RGB')
	img2 = Image.open(img2_path).convert('RGB')
	
	# Convert to PyTorch tensors and move to GPU
	t1 = TF.to_tensor(img1).to(device)
	t2 = TF.to_tensor(img2).to(device)
	
	# 1. Find the ideal overlap offset
	t0 = time.time()
	overlap_px = find_best_vertical_overlap_gpu(t1, t2, max_overlap=max_overlap)
	print(f"Found optimal vertical overlap: {overlap_px}px (Calculated in {(time.time() - t0)*1000:.2f}ms)")
	
	# 2. Perform the splitless stitch
	# Keep all of image 1, and grab everything below the overlap zone from image 2
	t2_remaining = t2[:, overlap_px:, :]
	
	# Concat along the height dimension (dim=1 for CxHxW tensors)
	stitched_tensor = torch.cat([t1, t2_remaining], dim=1)
	
	# 3. Bring back to CPU and save
	stitched_img = TF.to_pil_image(stitched_tensor.cpu())
	stitched_img.save(output_path)
	print(f"Successfully stitched and saved to: {output_path}")

# Example usage:
def generate_screenshot(base_file = "temp/merge.png",temp_file = "temp/temp.png"):
	
	if os.path.exists(base_file):
		os.remove(base_file)
		print(f"File {base_file} deleted. Proceeding to next step.")
	else:
		print(f"File {base_file} does not exist. Proceeding to next step.") 
	
	print("====================================================")
	print("Hotkeys initialized (User Mode). Listening...")
	print("  [Spacebar] : Capture snapshot and vertically merge")
	print("  [Esc]	  : Terminate program")
	print("====================================================")

	def on_press(key):
		try:
			# Handle Spacebar
			if key == keyboard.Key.space:
				# Case 1: First snapshot (merge.png doesn't exist yet)
				if not os.path.exists(base_file):
					print("\n[Spacebar] Capturing initial baseline image...")
					capture_direct_android_snapshot(base_file, x=90, y=485, width=900, height=900)
					print(f"Initial image saved to {base_file}.")
					
				# Case 2: Subsequent snapshot (merge with existing merge.png)
				else:
					print("\n[Spacebar] Capturing next section...")
					capture_direct_android_snapshot(temp_file, x=90, y=485, width=900, height=900)
					
					print("Merging images on GPU...")
					# Run your GPU stitching logic (stitch_vertical_images updates merge.png)
					stitch_vertical_images(base_file, temp_file, base_file, max_overlap=800)
					
					# Clean up the temporary file
					if os.path.exists(temp_file):
						os.remove(temp_file)
			
			# Handle Escape key to stop listening
			elif key == keyboard.Key.esc:
				print("\n[Esc] Exiting snapshot program cleanly.")
				return False  # Returning False stops the pynput listener thread
				
		except Exception as e:
			print(f"Error handling keypress: {e}")

	# Collect events until released
	with keyboard.Listener(on_press=on_press) as listener:
		listener.join()
