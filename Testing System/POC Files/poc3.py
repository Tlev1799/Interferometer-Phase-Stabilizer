import numpy as np
import cv2

# Specify the path to your text file
input_text_file = 'temp\\file number 1'  # Change this to your text file path

# Load the 2D matrix from the text file
matrix = np.loadtxt(input_text_file, dtype=np.uint8, delimiter=',')

cv2.namedWindow('image 2', cv2.WINDOW_NORMAL)
cv2.imshow("image 2", matrix)

# Print the loaded matrix to verify
print("Loaded matrix:")
print(matrix)

print("Before wait")
cv2.waitKey(0)
print("After wait")
cv2.destroyAllWindows()
print("Finished")
