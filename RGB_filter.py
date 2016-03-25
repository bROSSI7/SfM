# RGB filter: Select a user defined range of RGB values from Agisoft Photoscan point clouds
# Becca Rossi w/ help from Konrad

# import stuff
import pandas as pd
import numpy as np
import colorsys

# Define column names (Photoscan point cloud exports do not have header).
cols = ['x', 'y', 'z', 'r', 'g', 'b']

root = r'C:\Users\Rebecca Rossi\Desktop\GC\Working_Data\sfm_working\photoscan_outputs\RGB_input\213L_3gcps_1pts_ng_VegClumpTest.txt'

# Read in point cloud ASCII file into pandas DataFrame with 
# space delimiter, no header, and defined column names.
df = pd.read_csv(root, sep = ' ', header = None, names=cols)

# The colorsys module requires rescaled RGB values.
# Rescale RGB values in DataFrame by dividing each column by 255.

df['r2'] = df['r']/255
df['g2'] = df['g']/255
df['b2'] = df['b']/255

# Redefine the rescaled RGB values as r, g, and b to work with in the RGB to HSV conversion.
r = df['r2']
g = df['g2']
b = df['b2']

# Convert the r, g, b, values to h, l, s, values using the colorsys.rgb_to_hsv function and
# place in new columns titled 'h', 'l', and 's' in the DataFrame.
df['h'], df['l'], df['s'] = np.vectorize(colorsys.rgb_to_hls)(r, g, b)

# Where h is between the range of green angles and the saturation is between a specified percent, the string 'green' is returned in a new column titled 'green_color' or else the string 'not green' is returned.
df['green_color'] = np.where((0.166 <= df['h']) & (df['h'] <= 0.4166) & (0.2 <= df['s']) & (df['s'] <= 1), 'green', 'not green')

# Extract only rows of data with "green values".
output1 = df.loc[df['green_color'] == 'green']
output2 = df.loc[df['green_color'] == 'not green']

# Output new green color dataframe into a green and not green ASCII file.

output1.to_csv('213L_3gcps_1pts_g.txt', sep = ' ', columns = cols, header = False, index = False)
output2.to_csv('213L_3gcps_1pts_ng.txt', sep = ' ', columns = cols, header = False, index = False)