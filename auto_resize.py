import os
from PIL import Image
from send2trash import send2trash
import ctypes
from ctypes import wintypes

# Constants for Windows file attributes
FILE_ATTRIBUTE_REPARSE_POINT = 0x0400
FILE_ATTRIBUTE_OFFLINE = 0x1000

def is_file_local(filepath):
    attrs = ctypes.windll.kernel32.GetFileAttributesW(wintypes.LPCWSTR(filepath))
    if attrs == -1:
        return False
    return not (attrs & FILE_ATTRIBUTE_OFFLINE or attrs & FILE_ATTRIBUTE_REPARSE_POINT)

# Directory to scan
target_dir = r"ENTER YOUR FILEPATH HERE"
TARGET_ASPECT_RATIO = 16 / 9
TOLERANCE = 0.01
image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp"}
all_images_ok = True

def crop_to_aspect_ratio(img, target_ratio=16/9):
    width, height = img.size
    current_ratio = width / height

    if current_ratio > target_ratio:
        # Image is too wide — crop the sides
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        right = left + new_width
        top = 0
        bottom = height
    else:
        # Image is too tall — crop the top and bottom
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        bottom = top + new_height
        left = 0
        right = width

    return img.crop((left, top, right, bottom))


def get_aspect_ratio_decimal(width, height):
    return width / height

with open("DIL.txt", "w") as f:
    f.write("Delete Images List:\n\n")

    for filename in os.listdir(target_dir):
        file_path = os.path.join(target_dir, filename)
        ext = os.path.splitext(filename)[1].lower()

        if ext in image_extensions:
            try:
                if not is_file_local(file_path):
                    print(f"Skipping {filename}: Not available locally.")
                    continue

                with Image.open(file_path) as img:
                    width, height = img.size
                    ratio = get_aspect_ratio_decimal(width, height)

                    if abs(ratio - TARGET_ASPECT_RATIO) > TOLERANCE:
                        all_images_ok = False
                        print(f"Trying to resize: {filename} (Aspect ratio {ratio:.2f} ≠ 16:9)")

                        try:
                            resized_image = crop_to_aspect_ratio(img)
                            resized_image.save(file_path)  # Overwrite with resized image
                            print(f"✔  resized and saved: {filename}")
                        except Exception as resize_error:
                            print(f"❌ failed to resize: {filename} — {resize_error}")
                            f.write(f"{filename}\n\n")
                    else:
                        print(f"Keeping: {filename} (Aspect ratio {ratio:.2f} ≈ 16:9)")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

if all_images_ok:
    print("All images passed the check!")
