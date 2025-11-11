# bin2img

A tiny utility that converts any file into one or more PNG images (and back), each with a maximum size of 2048×2048 pixels. If the data doesn’t fit into a single image, it automatically splits it into multiple parts, similar to how WinRAR volumes work.

## Requirements

- Python
- [Pillow](https://pillow.readthedocs.io/) library

## Scripts

- `bin2img.py` – converts an input file into a PNG image (and additional parts if the file is large).
- `img2bin.py` – converts the generated PNG images back into the original file.

## Header format

Each PNG image starts with a small header encoded in the first pixels:

- **Pixels 0–7 (8 bytes):** 64-bit unsigned integer in big-endian order storing the number of valid payload bytes in this particular image. The decoder reads exactly this many bytes from the pixel data; any remaining pixels are padding.
- **Pixels 8–9 (2 bytes, first image only):** 16-bit unsigned integer in big-endian order storing the total number of parts the original file was split into. This field is present only in the first (index) image; in all subsequent images, these pixels are part of the normal payload.

All header fields are encoded in the same way as the payload: the grayscale value of each pixel directly corresponds to the original byte value.


## Example usage

```bash
python bin2img.py example.zip
```

This will create files like:

- `example.zip.binimg.png`
- `example.zip.binimg.01.png`
- `example.zip.binimg.02.png`
- ...

```bash
python img2bin.py example.zip.binimg.png
```

This reads the first/index PNG image, automatically discovers and loads all subsequent parts, and reconstructs the original file.

## Notes

The tool uses lossless PNG format: the grayscale value of each pixel directly encodes the original byte value. If you convert these PNGs to JPEG or another lossy format, the encoded data will be irreversibly corrupted.
