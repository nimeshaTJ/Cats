#
# Author : Nimesha Jayatunge
# ID : 20464631
#
# Cats.py - Simulation of cats in an environment
#
# Revisions: 
#
# 17/Sep/2021 - Can read terrain and landmark data from scv files, and draw them onto pygame display
# 18/Sep/2021 - Landmarks can now have a quantity (x units of food/water)
# 18/Sep/2021 - Created Cat class, movement rules and Moore/von Neumann neighbour detection

import pygame
import random
import numpy as np
import csv

# Colours
white = (255,255,255)
red = (255,0,0)
green = (50,130,0)
blue = (0,100,255)

# Defining the perimeter of the environment
num_rows = 50
num_cols = 50
cell_size = 10
display_width = num_cols*cell_size           # Width of display in pixels
display_height = num_rows*cell_size			 # Height of display in pixels

# Cat class
class Cat():
	def __init__(self,pos,health,age,temper):
		self.pos = pos
		self.health = health
		self.age = age
		self.temper = temper                 # Can be friendly, aggressive, or meek 
		self.colour = white
		self.attack_power = self.age*5 + 5   # Older cats deal more damage
		self.neighbours = []
		self.engaged = False

# Function that reads in terrain data from a file and returns it as an array
def read_terrain(terrain_filename):
	terrain_array = np.zeros((num_rows,num_cols)) 
	with open(terrain_filename,'r') as terrain_file:
		terrain_list = list(csv.reader(terrain_file))
	for r in range(num_rows):
		for c in range(num_cols):
			try:														# try statement handles data files of wrong dimensions	
				terrain_array[r,c] = int(terrain_list[r][c])        
			except IndexError:
				pass
	return terrain_array

# Function that reads in food and water data from a file and returns them as arrays
def read_landmarks(landmark_filename):
	food_array = np.zeros((num_rows,num_cols))
	water_array = np.zeros((num_rows,num_cols)) 
	with open(landmark_filename,'r') as landmark_file:
		raw_list = list(csv.reader(landmark_file))
	landmark_list = process(raw_list)									# landmark_list is now a list of tuples
			
	for r in range(len(landmark_list)):
		for c in range(len(landmark_list[0])):
			value = landmark_list[r][c]
			if value != None:
				landmark_type = value[0]							
				quantity = value[1]
				try:													# try statement handles data files of wrong dimensions	
					if landmark_type == "F":
						food_array[r,c] = quantity					
					else:
						water_array[r,c] = quantity
				except IndexError:
 					pass
	return food_array, water_array

# Processes the landmark list by converting strings into tuples of the form (landmark_type , quantity)
def process(raw_list):
	landmark_list = []
	for row in raw_list:
		processed_row = []
		for value in row:
			processed_value = None														# List item is None if no landmark present
			if value!= "":
				processed_value = (value.split(" ")[0], int(value.split(" ")[1]))		# List item is a tuple if landmark is present
			processed_row.append(processed_value)
		landmark_list.append(processed_row)	
	return landmark_list

def move_cats(cats,terrain_array,food_array,water_array,neighbourhood):
	moves = [-1,0,1]
	for cat in cats:
		next_pos = [cat.pos[0],cat.pos[1]]
		cant_move_there = True																
		while cant_move_there:
			cant_move_there = False
			if neighbourhood == "M":														# Movement within a Moore neighbourhood
				next_pos[0]+=random.choice(moves)
				next_pos[1]+=random.choice(moves)
			else:																			# Movement within a von Neumann neighbourhood
				axis = random.choice(['x','y'])
				if axis == 'y':  
					next_pos[0] += random.choice(moves)
				else:
					next_pos[1] += random.choice(moves)
		
			if next_pos[0]<0 or next_pos[0]>num_rows-1 or next_pos[1]<0 or next_pos[1]>num_cols-1:				# Cats cant leave borders
				cant_move_there = True
				next_pos = [cat.pos[0],cat.pos[1]]
			elif abs(terrain_array[next_pos[0],next_pos[1]] - terrain_array[cat.pos[0],cat.pos[1]]) > 4:		# Cats cant move across steep slopes
				cant_move_there = True
				next_pos = [cat.pos[0],cat.pos[1]]
		
		cat.pos = next_pos
		
		surrounding_cells = []
		r,c = cat.pos[0],cat.pos[1]
		if neighbourhood=="M":
			surrounding_cells.extend([[r-1,c-1],[r-1,c],[r-1,c+1],[r,c-1],[r,c+1],[r+1,c-1],[r+1,c],[r+1,c+1]])
		else:
			surrounding_cells.extend([[r-1,c],[r,c-1],[r,c+1],[r+1,c]])
		cat.neighbours = [neighbour for neighbour in cats if (neighbour!=cat) and (neighbour.pos in surrounding_cells)]
		if len(cat.neighbours)>0:
			cat.engaged = True
		else:
			cat.engaged = False
		
# Function that maps height values (0 to 10) to RGB (dark brown to light brown)
def assign_terrain_colour(height):
	R = 13.5*height + 120
	G = 9*height + 80
	B = 0
	return((R,G,B))

# Function that draws and displays the current state of the environment (terrain, landmarks, and cats)
def draw_screen(terrain_array,food_array, water_array, cats):
	for r in range(num_rows):
		for c in range(num_cols):
			terrain_colour = assign_terrain_colour(terrain_array[r,c])													
			pygame.draw.rect(gameDisplay, terrain_colour,[c*cell_size,r*cell_size,cell_size,cell_size])					
			pygame.draw.circle(gameDisplay,green,((c+0.5)*cell_size,(r+0.5)*cell_size),food_array[r,c]*cell_size/10)	# Food are green circles
			pygame.draw.circle(gameDisplay,blue,((c+0.5)*cell_size,(r+0.5)*cell_size),water_array[r,c]*cell_size/10)	# Water are blue circles
	for cat in cats:
		r = cat.pos[0]
		c = cat.pos[1]
		pygame.draw.circle(gameDisplay , cat.colour, ((c+0.5)*cell_size,(r+0.5)*cell_size), cell_size*(cat.age/16 + 1/4))	# Cats are white circles

def show_cats(cats):
	for cat in cats:
		print("health: ", cat.health)
		print("age: ", cat.age)
		print("temper: ", cat.temper)
		print("\n\n")

# Creating cat objects
cats = []
for i in range(2):
	pos = [random.randint(0,num_rows-1), random.randint(0,num_cols-1)]
	health = 100
	age = random.randint(0,4)
	temper = random.choice(["aggressive","friendly","meek"])
	cat = Cat(pos, health, age, temper)
	cats.append(cat)

if __name__ == "__main__":

	# terrain_filename = input("\nPlease enter a terrain data file:    ")
	# landmark_filename = input("\nPlease enter a landmark data file:    ")
	neighbourhood = input("\nPlease enter the desired neighbourhood (M or V):    ")
	terrain_array = read_terrain("terrain.csv")
	food_array, water_array = read_landmarks("landmarks.csv")

	# Initializing pygame
	gameDisplay = pygame.display.set_mode((display_width,display_height))
	pygame.display.set_caption("Cats")
	clock = pygame.time.Clock()
	crashed = False
	framerate = 2

	while not crashed:

		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				crashed = True												# Quits simulation if user closes pygame window
		
		draw_screen(terrain_array,food_array, water_array, cats)			# Updates the pygame display so that it
		pygame.display.update()												# draws the new frame
		move_cats(cats,terrain_array,food_array,water_array,neighbourhood)			
		clock.tick(framerate)												# Updates at 2 frames per second

pygame.quit()
quit()
