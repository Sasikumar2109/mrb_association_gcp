import os
from PIL import Image

def optimize_images(input_dir, output_dir, target_width, target_height, quality=85, background_color=(255, 255, 255)):
    """
    Reads images from input_dir, resizes them to fit within target_width x target_height
    (maintaining aspect ratio), adds padding to reach the exact target size,
    compresses them, and saves them to output_dir.

    Args:
        input_dir (str): Path to the directory containing original images.
        output_dir (str): Path to the directory where optimized images will be saved.
        target_width (int): Desired fixed width for the optimized images.
        target_height (int): Desired fixed height for the optimized images.
        quality (int, optional): JPEG compression quality (0-100). Higher is better quality, larger file. Defaults to 85.
        background_color (tuple, optional): RGB tuple for the padding background. Defaults to white.
    """
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    os.makedirs(output_dir, exist_ok=True)
    print(f"Optimizing images from '{input_dir}' to '{output_dir}' (fixed size {target_width}x{target_height})...")

    supported_formats = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_formats):
            input_path = os.path.join(input_dir, filename)

            base_name, _ = os.path.splitext(filename)
            output_filename = base_name + ".jpg"
            output_path = os.path.join(output_dir, output_filename)

            try:
                with Image.open(input_path) as img:
                    # Convert to RGB if not already (important for JPG saving and background color)
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                    elif img.mode == 'P': # Palette mode, convert to RGB
                        img = img.convert('RGB')

                    original_width, original_height = img.size
                    
                    # Calculate aspect ratios
                    original_aspect = original_width / original_height
                    target_aspect = target_width / target_height

                    # Determine how to resize while maintaining aspect ratio
                    if original_aspect > target_aspect:
                        # Original is wider than target aspect ratio, scale by width
                        new_width = target_width
                        new_height = int(new_width / original_aspect)
                    else:
                        # Original is taller or same aspect ratio, scale by height
                        new_height = target_height
                        new_width = int(new_height * original_aspect)

                    # Resize the image
                    resized_img = img.resize((new_width, new_height), Image.LANCZOS) # LANCZOS is good for downscaling

                    # Create a new blank image with the target dimensions and desired background color
                    final_img = Image.new('RGB', (target_width, target_height), background_color)

                    # Calculate paste position to center the resized image
                    paste_x = (target_width - new_width) // 2
                    paste_y = (target_height - new_height) // 2

                    # Paste the resized image onto the new blank image
                    final_img.paste(resized_img, (paste_x, paste_y))

                    # Save the final image
                    final_img.save(output_path, quality=quality, optimize=True)
                print(f"Optimized: {filename} to {target_width}x{target_height}")
            except Exception as e:
                print(f"Could not optimize {filename}: {e}")
    print("Image optimization complete.")

if __name__ == "__main__":
    # --- Configuration ---
    # IMPORTANT: Adjust these paths and dimensions as needed!
    original_photos_dir = "data/orginal_photos"  # Your current photo directory
    optimized_photos_dir = "data/optimized_association_photos" # New directory for optimized photos

    # Target dimensions: All images will be exactly this size
    target_fixed_width = 600
    target_fixed_height = 500 

    # Compression quality (0-100). 85 is usually a good balance.
    compression_quality = 85
    
    # Background color for padding (R, G, B) - e.g., white
    padding_color = (255, 255, 255) 

    # Run the optimization
    optimize_images(
        original_photos_dir,
        optimized_photos_dir,
        target_fixed_width,
        target_fixed_height,
        compression_quality,
        padding_color
    )