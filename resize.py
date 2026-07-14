import os
from PIL import Image, ExifTags
from datetime import datetime
from io import BytesIO

SOURCE_DIR = r'C:\\Users\\TimMitchell\\Desktop\\photostream\\'
DEST_DIR = r'C:\\Users\\TimMitchell\\Desktop\\photostream2\\'
MAX_SIZE_MB = 15
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

def get_date_taken(path):
    try:
        image = Image.open(path)
        exif = image._getexif()
        if not exif:
            return None
        for tag, value in exif.items():
            decoded = ExifTags.TAGS.get(tag, tag)
            if decoded == "DateTimeOriginal":
                return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return None

def resize_to_target_size(img, target_bytes, min_quality=20, max_quality=95):
    quality = max_quality
    step = 5
    while quality >= min_quality:
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality)
        size = buffer.tell()
        if size <= target_bytes:
            return buffer.getvalue()
        quality -= step
    # If can't reach target, return the smallest possible
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=min_quality)
    return buffer.getvalue()

def main():
    # Create output directory if it doesn't exist
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    # Loop through image files in the source directory
    for filename in os.listdir(SOURCE_DIR):
        if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            src_path = os.path.join(SOURCE_DIR, filename)

            # If file is larger than MAX_SIZE_BYTES, resize it
            if os.path.getsize(src_path) > MAX_SIZE_BYTES:
                img = Image.open(src_path)

                # Use the date taken from EXIF data for renaming. If EXIF data is not available, fallback to file modified time.
                date_taken = get_date_taken(src_path)
                if not date_taken:
                    # fallback to file modified time
                    date_taken = datetime.fromtimestamp(os.path.getmtime(src_path))

                # Output format: YYYY_MM_DD_HHMMSS.jpg
                new_name = date_taken.strftime('%Y_%m_%d_%H%M%S') + '.jpg'
                dest_path = os.path.join(DEST_DIR, new_name)
                img_bytes = resize_to_target_size(img, MAX_SIZE_BYTES)
                with open(dest_path, 'wb') as f:
                    f.write(img_bytes)

            else:
                # Still rename and copy if under size
                date_taken = get_date_taken(src_path)
                if not date_taken:
                    date_taken = datetime.fromtimestamp(os.path.getmtime(src_path))
                new_name = date_taken.strftime('%Y_%m_%d_%H%M%S') + '.jpg'
                dest_path = os.path.join(DEST_DIR, new_name)
                with open(src_path, 'rb') as src_file, open(dest_path, 'wb') as dst_file:
                    dst_file.write(src_file.read())

if __name__ == '__main__':
    main()