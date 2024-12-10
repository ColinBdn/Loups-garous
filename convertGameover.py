from PIL import Image
import numpy as np

path = './images/loup-garou.png'
image = Image.open(path).convert('L')

image = np.asarray(image)
# print(image)

black_threshold = 50
white_threshold = 50

image_clamped = np.where(image < black_threshold, 0, image)  # Set "pretty black" pixels to 0
image_clamped = np.where(image_clamped > white_threshold, 1, image_clamped)  # Set "pretty white" pixels to 1

# print(image_clamped)

# print(len(image_clamped)*len(image_clamped[0]))

# with open("image_array.txt", "w") as f:
#     # Start defining the C array
#     f.write("const unsigned char gameOverBuffer[] = {\n")
    
#     # Write each row of the array
#     for row in image_clamped:
#         f.write("    " + ", ".join(map(str, row)) + ",\n")
    
#     # Close the array definition
#     f.write("};\n")

image = Image.fromarray(image_clamped*255)
image.save("./images/loup-garou.png")