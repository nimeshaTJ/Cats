#
# Author : Nimesha Jayatunge
# ID : 20464631
#
# Cats.py - Simulation of cats in an environment
#
# Revisions: 
#
# 17/Sep/2021 - Can read terrain and landmark data from scv files, and draw them onto pygame display

import pygame
import random
import numpy as np
import csv

# Colours
green = (0,255,0)
blue = (0,0,255)
pink = (255,0,250)

# Defining the perimeter of the environment
num_rows = 50
num_cols = 50
cell_size = 10
display_width = num_cols*cell_size
display_height = num_rows*cell_size

# Function that reads in terrain and landmark (food, water, bed) data from a file and returns them as arrays
def read_data(terrain_filename, landmarks_filename):
	terrain_array = np.zeros((num_rows,num_cols))
	landmarks_array = np.full((num_rows,num_cols)," ")
	terrain_file = open(terrain_filename,'r')
	landmarks_file = open(landmarks_filename,'r')
	terrain_list = list(csv.reader(terrain_file))
	landmarks_list = list(csv.reader(landmarks_file))
	for r in range(num_rows):
		for c in range(num_cols):
			try:
				terrain_array[r,c] = int(terrain_list[r][c])
			except IndexError:
				pass
			try:
				landmarks_array[r,c] = landmarks_list[r][c]
			except IndexError:
				pass
	terrain_file.close()
	landmarks_file.close()
	return terrain_array, landmarks_array

# Function that takes a height value from 0 to 10, and returns the colour of the terrain at that height (dark brown to light brown)
def assign_terrain_colour(height):
	R = 13.5*height + 120
	G = 9*height + 80
	B = 0
	return((R,G,B))

# Function that draws and displays the current state of the environment (terrain, landmarks, and cats)
def draw_screen(terrain_array,landmarks_array):
	for r in range(num_rows):
		for c in range(num_cols):
			terrain_colour = assign_terrain_colour(terrain_array[r,c])	
			pygame.draw.rect(gameDisplay, terrain_colour,[c*cell_size,r*cell_size,cell_size,cell_size])
			if landmarks_array[r,c] == "F":
				pygame.draw.circle(gameDisplay,green,((c+0.5)*cell_size,(r+0.5)*cell_size),cell_size/2)
			if landmarks_array[r,c] == "W":
				pygame.draw.circle(gameDisplay,blue,((c+0.5)*cell_size,(r+0.5)*cell_size),cell_size/2)	
			if landmarks_array[r,c] == "B":
				pygame.draw.circle(gameDisplay,pink,((c+0.5)*cell_size,(r+0.5)*cell_size),cell_size/2)


gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption("Cats")
clock = pygame.time.Clock()
crashed = False
framerate = 2

if __name__ == "__main__":

	while not crashed:

		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				crashed = True
		
		terrain_array, landmarks_array = read_data("terrain.csv","landmarks.csv")
		draw_screen(terrain_array,landmarks_array)
		pygame.display.update()
		clock.tick(framerate)		

pygame.quit()
quit()
