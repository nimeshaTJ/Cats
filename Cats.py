#
# Author : Nimesha Jayatunge
# ID : 20464631
#
# Cats.py - Simulation of cats in an environment
#
# Revisions: 
#
# 17/Sep/2021 - Can read terrain and landmark data from scv files, and draw them onto pygame display
# 18/Sep/2021 - Landmaks can now have a quantity (x units of food/water)

import pygame
import random
import numpy as np
import csv

# Colours
green = (50,130,0)
blue = (0,100,255)
pink = (255,0,250)

# Defining the perimeter of the environment
num_rows = 50
num_cols = 50
cell_size = 10
display_width = num_cols*cell_size
display_height = num_rows*cell_size

# Function that reads in terrain data from a file and returns it as an array
def read_terrain(terrain_filename):
	terrain_array = np.zeros((num_rows,num_cols)) 
	with open(terrain_filename,'r') as terrain_file:
		terrain_list = list(csv.reader(terrain_file))
	for r in range(num_rows):
		for c in range(num_cols):
			try:
				terrain_array[r,c] = int(terrain_list[r][c])
			except IndexError:
				pass
	return terrain_array

# Processes the landmark list by converting strings into tuples of the form (landmark_type , quantity)
def process(raw_list):
	landmark_list = []
	for row in raw_list:
		processed_row = []
		for value in row:
			processed_value = None
			if value!= "":
				processed_value = (value.split(" ")[0], int(value.split(" ")[1]))
			processed_row.append(processed_value)
		landmark_list.append(processed_row)	
	return landmark_list

# Function that reads in food and water data from a file and returns them as arrays
def read_landmarks(landmark_filename):
	food_array = np.zeros((num_rows,num_cols))
	water_array = np.zeros((num_rows,num_cols)) 
	with open(landmark_filename,'r') as landmark_file:
		raw_list = list(csv.reader(landmark_file))
	landmark_list = process(raw_list)
			
	for r in range(len(landmark_list)):
		for c in range(len(landmark_list[0])):
			value = landmark_list[r][c]
			if value != None:
				landmark_type = value[0]
				quantity = value[1]
				try:
					if landmark_type == "F":
						food_array[r,c] = quantity
					else:
						water_array[r,c] = quantity
				except IndexError:
 					pass
	return food_array, water_array
			
# Function that takes a height value from 0 to 10, and returns the colour of the terrain at that height (dark brown to light brown)
def assign_terrain_colour(height):
	R = 13.5*height + 120
	G = 9*height + 80
	B = 0
	return((R,G,B))

# Function that draws and displays the current state of the environment (terrain, landmarks, and cats)
def draw_screen(terrain_array,food_array, water_array):
	for r in range(num_rows):
		for c in range(num_cols):
			terrain_colour = assign_terrain_colour(terrain_array[r,c])	
			pygame.draw.rect(gameDisplay, terrain_colour,[c*cell_size,r*cell_size,cell_size,cell_size])
			pygame.draw.circle(gameDisplay,green,((c+0.5)*cell_size,(r+0.5)*cell_size),food_array[r,c]*cell_size/10)
			pygame.draw.circle(gameDisplay,blue,((c+0.5)*cell_size,(r+0.5)*cell_size),water_array[r,c]*cell_size/10)


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
		
		terrain_array = read_terrain("terrain.csv")
		food_array, water_array = read_landmarks("landmarks.csv")
		draw_screen(terrain_array,food_array, water_array)
		pygame.display.update()
		clock.tick(framerate)		

pygame.quit()
quit()
