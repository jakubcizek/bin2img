import sys
import os
from PIL import Image

def images_to_file(first_image_path: str) -> None:
    if not os.path.isfile(first_image_path):
        print(f"'{first_image_path}' does not exist!", file=sys.stderr)
        return

    base_dir, first_name = os.path.split(first_image_path)
    if base_dir == "":
        base_dir = "."

    stem, ext = os.path.splitext(first_name)
    if ext.lower() != ".png":
        print("Warning: The selected file does not have a PNG extension. I'll try anyway", file=sys.stderr)

    if stem.endswith(".binimg"):
        orig_name = stem[:-7] 
        prefix = stem 
    else:
        orig_name = stem
        prefix = stem
        print("Warning: name does not match the pattern *.binimg.png", file=sys.stderr)

    first_full = os.path.join(base_dir, first_name)
    with Image.open(first_full) as img:
        img = img.convert("L")
        pixels = img.tobytes()

    if len(pixels) < 10:
        print("Image does not contain enough data!", file=sys.stderr)
        return

    first_chunk_len = int.from_bytes(pixels[0:8], "big")
    total_parts = int.from_bytes(pixels[8:10], "big")

    if total_parts == 0:
        total_parts = 1

    if len(pixels) < 10 + first_chunk_len:
        print("Corrupted image. Fewer pixels than specified part length!", file=sys.stderr)
        return

    data = bytearray()
    data.extend(pixels[10:10 + first_chunk_len])
    print(f"Loaded: {first_full} (part 1/{total_parts}, {first_chunk_len} bytes)")

    for part_idx in range(1, total_parts):
        name_i = f"{prefix}.{part_idx:02d}{ext}"
        path_i = os.path.join(base_dir, name_i)

        if not os.path.isfile(path_i):
            print(f"Expected image is missing: {path_i}!", file=sys.stderr)
            return

        with Image.open(path_i) as img:
            img = img.convert("L")
            pixels = img.tobytes()

        if len(pixels) < 8:
            print(f"Corrupted image: {path_i}!", file=sys.stderr)
            return

        chunk_len = int.from_bytes(pixels[0:8], "big")

        if len(pixels) < 8 + chunk_len:
            print(f"Corrupted image. Fewer pixels than specified part length: {path_i}!",
                  file=sys.stderr)
            return

        data.extend(pixels[8:8 + chunk_len])
        print(f"Loaded: {path_i} (part {part_idx + 1}/{total_parts}, {chunk_len} bytes)")

    out_path = os.path.join(base_dir, orig_name)
    if os.path.exists(out_path):
        out_path = out_path + ".restored"

    with open(out_path, "wb") as f:
        f.write(data)

    print(f"File saved: {out_path} ({len(data)} bytes).")


def main():
    if len(sys.argv) != 2:
        print(f"Use: {sys.argv[0]} PATH_TO_FIRST_IMAGE", file=sys.stderr)
        sys.exit(1)

    images_to_file(sys.argv[1])


if __name__ == "__main__":
    main()
