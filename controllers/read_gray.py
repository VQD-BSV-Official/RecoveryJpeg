# from PIL import Image, ImageFile

# # Allow loading of truncated images
# ImageFile.LOAD_TRUNCATED_IMAGES = True

# def is_corrupted(pixel):
#     """Check if the pixel is likely to be corrupted (based on certain criteria)."""
#     r, g, b = pixel
#     return r > 250 and g < 5 and b < 5  # Example condition, adjust based on your corruption

# def fix_corrupted_image(image_path, output_path):
#     try:
#         # Open the image
#         img = Image.open(image_path)
#         pixels = img.load()  # Load the pixel data

#         # Image dimensions
#         width, height = img.size

#         # Iterate over all pixels to find corrupted ones
#         for x in range(width):
#             for y in range(height):
#                 current_pixel = pixels[x, y]
                
#                 if is_corrupted(current_pixel):
#                     # If corrupted, replace it with an average of surrounding pixels
#                     surrounding_pixels = []

#                     # Check neighboring pixels, avoiding boundaries
#                     for dx in [-1, 0, 1]:
#                         for dy in [-1, 0, 1]:
#                             nx, ny = x + dx, y + dy
#                             if 0 <= nx < width and 0 <= ny < height and (dx, dy) != (0, 0):
#                                 surrounding_pixels.append(pixels[nx, ny])

#                     if surrounding_pixels:
#                         # Average the surrounding pixel values
#                         avg_r = sum([p[0] for p in surrounding_pixels]) // len(surrounding_pixels)
#                         avg_g = sum([p[1] for p in surrounding_pixels]) // len(surrounding_pixels)
#                         avg_b = sum([p[2] for p in surrounding_pixels]) // len(surrounding_pixels)

#                         # Replace the corrupted pixel with the average
#                         pixels[x, y] = (avg_r, avg_g, avg_b)

#         # Save the fixed image
#         img.save(output_path)
#         print(f"Corrupted parts removed, and image saved successfully at {output_path}")
        
#     except Exception as e:
#         print(f"Error processing image: {e}")

# # Path to your image and output
# input_image = "IMG_2.JPG"
# output_image = "IMG_2_fixed.JPG"

# fix_corrupted_image(input_image, output_image)




from PIL import Image, ImageFile
from io import BytesIO

# Allow loading of truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

def is_corrupted(pixel):
    """Check if the pixel is likely to be corrupted (based on certain criteria)."""
    r, g, b = pixel
    return r > 250 and g < 5 and b < 5  # Example condition, adjust based on your corruption

def fix_corrupted_image_from_bytes(image_data):
    try:
        # Open the image from byte data
        img = Image.open(BytesIO(image_data))
        pixels = img.load()  # Load the pixel data

        # Image dimensions
        width, height = img.size

        # Iterate over all pixels to find corrupted ones
        for x in range(width):
            for y in range(height):
                current_pixel = pixels[x, y]
                
                if is_corrupted(current_pixel):
                    # If corrupted, replace it with an average of surrounding pixels
                    surrounding_pixels = []

                    # Check neighboring pixels, avoiding boundaries
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < width and 0 <= ny < height and (dx, dy) != (0, 0):
                                surrounding_pixels.append(pixels[nx, ny])

                    if surrounding_pixels:
                        # Average the surrounding pixel values
                        avg_r = sum([p[0] for p in surrounding_pixels]) // len(surrounding_pixels)
                        avg_g = sum([p[1] for p in surrounding_pixels]) // len(surrounding_pixels)
                        avg_b = sum([p[2] for p in surrounding_pixels]) // len(surrounding_pixels)

                        # Replace the corrupted pixel with the average
                        pixels[x, y] = (avg_r, avg_g, avg_b)

        # Return the fixed image as byte data
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()

    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def run(image_bytes):
    # with open('test.jpg', 'rb') as dump:
    #     image_bytes = dump.read() 

    fixed_image_data = fix_corrupted_image_from_bytes(image_bytes)
    return fixed_image_data

    # with open('test2.jpg', 'wb') as w:
    #     w.write(fixed_image_data)

    # if fixed_image_data:
    #     print("Corrupted parts removed, and image processed successfully.")
    # Do something with `fixed_image_data`, e.g., send it over a network, store it, etc.
