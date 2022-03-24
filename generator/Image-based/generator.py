from audioop import avg
from PIL import Image
import sys
import math
from statistics import mean

from cv2 import sqrt
from numpy import iterable

if len(sys.argv) != 2:
    raise Exception("Usage: generator.py example-image")


class color:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue
        
        # pixel
        self.pixel = (self.red, self.green, self.blue)



grey = color(128, 128, 128)
white = color(255, 255, 255)
red = color(255, 0, 0)
black = color(0, 0, 0)


# Function for comparing colors RGB values
def compareRGB(col1:color, col2:color, threshold=0.8):
    # Taking mean of red channel values
    # Rmean = (col1.red + col2.red)*.5
    # Taking difference in color, making deltaRed, deltaGreen, deltaBlue
    dR, dG, dB = col1.red - col2.red, col1.green - col2.green, col1.blue - col2.blue

    dRsq, dGsq, dBsq = dR**2, dG**2, dB**2

    # Delta color, obtained by the formula according to compuphase.com
    # check it out -> https://www.compuphase.com/cmetric.htm
    # dColor = ((512 + Rmean)*(dRsq/256) + (4*dGsq) + (767-Rmean)*dBsq)**.5
    dColor = math.sqrt(dRsq+dGsq+dBsq)

    maxColor = 255 * math.sqrt(3)

    pColor = (dColor*100)/maxColor

    print("Distance:", dColor)
    print("Percentage:", pColor)
    

def average(iterable):
    return sum(iterable)/len(iterable)


# Set of colors
colorSet = set()

# Chunk size
CHUNK_SIZE = 1

# Opening the file and seeings what's inside
with Image.open(sys.argv[1]) as img:
    HEIGHT, WIDTH = img.size
    
    print(WIDTH, HEIGHT)

    total = WIDTH * HEIGHT

    chunk = 1
    total_chunks = int((WIDTH*HEIGHT)/(CHUNK_SIZE**2))

    print("Opening file")
    with open("maze.txt", mode='w+') as maze:

        # Iterating through the image
        for i in range(0, WIDTH, CHUNK_SIZE):
            for j in range(0, HEIGHT, CHUNK_SIZE):
                # Extracting RGB values of pixels in chunks and averaging them
                R, G, B = [], [], []
                try:
                    if chunk != 1:
                        print(f"Working on Chunk: {chunk} out of {total_chunks}")
                        
                        for k in range(i, i + CHUNK_SIZE):
                            for l in range(j, j + CHUNK_SIZE):
                                r, g, b = img.getpixel((k, l))
                                R.append(r)
                                G.append(g)
                                B.append(b)
                        chunk += 1
                    
                    else:
                        r, g, b = img.getpixel((i, j))
                        R.append(r)
                        G.append(g)
                        B.append(b)

                except IndexError:
                        continue

                # Taking average of each channel of chunk
                R = list(map(lambda r: 0.299*r, R))
                G = list(map(lambda g: 0.587*g, G))
                B = list(map(lambda b: 0.114*b, B))
                
                GRAYSCALE = list(sum(i) for i in zip(R, G, B))

                GRAYSCALE = average(GRAYSCALE)

                # print(f"CHUNK [{i}:{i+CHUNK_SIZE}][{j}:{j+CHUNK_SIZE}] GrayScale: {int(GRAYSCALE)}\n")


            #     # Converting to grayscale image
            #     GRAYSCALE = 0.299*R + 0.587*G + 0.114*B

                # Changing the range of Grayscale from 0 to 255, to -127 to 128
                GRAYSCALE = int(GRAYSCALE) - 128

                if GRAYSCALE <= 0:
                    # The color seems to be black
                    # string = str(u"\u2588".encode('utf-8'))
                    # maze.write(string)
                    maze.write("#")
                elif GRAYSCALE > 0:
                    # The color seems to be white
                    maze.write(" ")
            maze.write("\n")