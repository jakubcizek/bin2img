import sys
import os
import math
from PIL import Image

WIDTH = 2048
MAX_HEIGHT = 2048
CAPACITY = WIDTH * MAX_HEIGHT

HEADER_FIRST = 10
HEADER_NEXT = 8


def file_to_images(path: str) -> None:
    if not os.path.isfile(path):
        print(f"'{path}' does not exist!", file=sys.stderr)
        return

    with open(path, "rb") as f:
        data = f.read()

    total_len = len(data)
    if total_len == 0:
        print("Input file is empty. Nothing to encode!")
        return

    capacity_first = CAPACITY - HEADER_FIRST
    capacity_next = CAPACITY - HEADER_NEXT

    if total_len <= capacity_first:
        num_parts = 1
    else:
        remaining = total_len - capacity_first
        num_additional = math.ceil(remaining / capacity_next)
        num_parts = 1 + num_additional

    if num_parts > 65535:
        print("Too many parts (max 65535)!", file=sys.stderr)
        return

    base_name = os.path.basename(path)
    dir_name = os.path.dirname(path)
    prefix = os.path.join(dir_name, base_name + ".binimg")

    pos = 0
    for part_idx in range(num_parts):
        is_first = (part_idx == 0)

        if is_first:
            chunk_len = min(total_len - pos, capacity_first)
        else:
            chunk_len = min(total_len - pos, capacity_next)

        chunk = data[pos:pos + chunk_len]
        pos += chunk_len

        header = chunk_len.to_bytes(8, "big")
        if is_first:
            header += num_parts.to_bytes(2, "big")

        buf_len = len(header) + chunk_len
        height = math.ceil(buf_len / WIDTH)
        if height > MAX_HEIGHT:
            print("Internal error: Image too large!", file=sys.stderr)
            return

        num_pixels = WIDTH * height
        img_buf = bytearray(num_pixels)

        img_buf[0:len(header)] = header
        img_buf[len(header):len(header) + chunk_len] = chunk

        img = Image.frombytes("L", (WIDTH, height), bytes(img_buf))

        if is_first:
            out_name = prefix + ".png"
        else:
            out_name = f"{prefix}.{part_idx:02d}.png"

        img.save(out_name, format="PNG")
        print(f"Saved: {out_name} (part {part_idx + 1}/{num_parts}, {chunk_len} bytes)")


def main():
    if len(sys.argv) != 2:
        print(f"Use: {sys.argv[0]} PATH_TO_FILE", file=sys.stderr)
        sys.exit(1)

    file_to_images(sys.argv[1])


if __name__ == "__main__":
    main()
