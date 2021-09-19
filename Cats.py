#
# Author : Nimesha Jayatunge
# ID : 20464631
#
# Cats.py - Simulation of cats in an environment
#
# Revisions: 
#
# 17/Sep/2021 - Can read terrain and landmark data from scv files, and draw them onto pygame display.
# 18/Sep/2021 - Landmarks can now have a quantity (x units of food/water).
# 18/Sep/2021 - Created Cat class, movement rules and Moore/von Neumann neighbour detection.
# 19/Sep/2021 - Cats have hunger and thirst, and can eat food and drink water. Cats can also detect whether other cats are nearby.

import pygame
import random
import numpy as np
import csv

# Colours
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
green = (50,130,0)
blue = (0,100,255)

# Defining the perimeter of the simulation
num_rows = 50
num_cols = 50
cell_size = 10
display_width = (num_cols+2)*cell_size           # Width of display in pixels
display_height = (num_rows+2)*cell_size			 # Height of display in pixels
framerate = 10

# Cat class
class Cat():
	def __init__(self,pos,age,temper,sex):
		self.pos = pos
		self.age = age
		self.temper = temper   					# Can be friendly, aggressive, or meek 
		self.sex = sex              
		self.colour = white
		self.attack_power = self.age*5 + 5   	# Older cats deal more damage
		self.neighbours = []
		self.engaged = False
		self.health = 100
		self.thirst = 0
		self.hunger = 0

	def eat(self,food,food_array):
		if self.hunger>=25:
			food_array[food[0],food[1]]-=1
			self.hunger-=15

	def drink(self,water,water_array):
		if self.thirst>=25:
			water_array[water[0],water[1]]-=1
			self.thirst-=15		

	def die(self,cats):
		cats.remove(self)

# Function that reads in terrain data from a file and returns it as an array
def read_terrain(terrain_filename):
	terrain_array = np.zeros((num_rows+2,num_cols+2)) 
	with open(terrain_filename,'r') as terrain_file:
		terrain_list = list(csv.reader(terrain_file))
	for r in range(num_rows):
		for c in range(num_cols):
			try:														# try statement handles data files of wrong dimensions	
				terrain_array[r+1,c+1] = int(terrain_list[r][c])        
			except IndexError:
				pass
	return terrain_array

# Function that reads in food and water data from a file and returns them as arrays
def read_landmarks(landmark_filename):
	food_array = np.zeros((num_rows+2,num_cols+2))
	water_array = np.zeros((num_rows+2,num_cols+2)) 
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
						food_array[r+1,c+1] = quantity					
					else:
						water_array[r+1,c+1] = quantity
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
			if value != "":
				processed_value = (value.split(" ")[0], int(value.split(" ")[1]))		# List item is a tuple if landmark is present
			processed_row.append(processed_value)
		landmark_list.append(processed_row)	
	return landmark_list

# Calculates a valid move for each cat and moves it there
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
		
			if next_pos[0]<1 or next_pos[0]>num_rows or next_pos[1]<1 or next_pos[1]>num_cols:					# Cats can't leave borders
				cant_move_there = True
				next_pos = [cat.pos[0],cat.pos[1]]
			elif abs(terrain_array[next_pos[0],next_pos[1]] - terrain_array[cat.pos[0],cat.pos[1]]) > 4:		# Cats can't move across steep slopes
				cant_move_there = True
				next_pos = [cat.pos[0],cat.pos[1]]
			elif (food_array[next_pos[0],next_pos[1]] > 0) or (water_array[next_pos[0],next_pos[1]] > 0):			# Cats can't walk on food or water
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
			#cat.interact()
			#return None
		else:
			cat.engaged = False

		neighbouring_water = []
		neighbouring_food = []
		for cell in surrounding_cells:
			if water_array[cell[0],cell[1]] > 0:
				neighbouring_water.append(cell)
			elif food_array[cell[0],cell[1]] > 0:
				neighbouring_food.append(cell)
		
		if len(neighbouring_food)>0 or len(neighbouring_water)>0:		
			eat_or_drink(cat,neighbouring_food,neighbouring_water,food_array,water_array)

# Function that decides whether to eat or drink given landmarks in its neighbourhood
def eat_or_drink(cat,neighbouring_food,neighbouring_water,food_array,water_array):
		if len(neighbouring_water)==0:													# If there's only food in its neighbourhood
			cat.eat(random.choice(neighbouring_food),food_array)
		elif len(neighbouring_food)==0:													# If there's only water in its neighbourhood
			cat.drink(random.choice(neighbouring_water),water_array)
		else:																			# If there's both food and water in its neighbourhood
			if cat.hunger>cat.thirst:													# Chooses based on whether its more hungry or more thirsty
				cat.eat(random.choice(neighbouring_food),food_array)
			else:
				cat.drink(random.choice(neighbouring_water),water_array)

def hunger_and_thirst(cats):
	for cat in cats:
		cat.hunger+=0.2
		cat.thirst+=0.4

def kill_cats(cats):
	alive_cats = [cat for cat in cats if (cat.health>0 and cat.hunger<100 and cat.thirst<100)]
	return alive_cats

# Function that maps height values (0 to 10) to RGB (dark brown to light brown)
def assign_terrain_colour(height):
	R = 13.5*height + 120
	G = 9*height + 80
	B = 0
	return((R,G,B))

# Function that draws and displays the current state of the environment (terrain, landmarks, and cats)
def draw_screen(terrain_array,food_array, water_array, cats):
	
	for r in range(num_rows+2):
		for c in range(num_cols+2):
			terrain_colour = assign_terrain_colour(terrain_array[r,c])													
			pygame.draw.rect(gameDisplay, terrain_colour,[c*cell_size,r*cell_size,cell_size,cell_size])					
			pygame.draw.circle(gameDisplay,green,((c+0.5)*cell_size,(r+0.5)*cell_size),food_array[r,c]*cell_size/10)	# Food are green circles
			pygame.draw.circle(gameDisplay,blue,((c+0.5)*cell_size,(r+0.5)*cell_size),water_array[r,c]*cell_size/10)	# Water are blue circles
	for cat in cats:
		r = cat.pos[0]
		c = cat.pos[1]
		pygame.draw.circle(gameDisplay , cat.colour, ((c+0.5)*cell_size,(r+0.5)*cell_size), cell_size*(cat.age/16 + 1/4))	# Cats are white circles

	pygame.draw.rect(gameDisplay, black, [0,0,display_width,cell_size])														# 
	pygame.draw.rect(gameDisplay, black, [0,0,cell_size,display_height])													# Drawing 				
	pygame.draw.rect(gameDisplay, black, [0,display_height-cell_size,display_width,cell_size])								# boundaries						
	pygame.draw.rect(gameDisplay, black, [display_width-cell_size,0,cell_size,display_height])								#

def show_cats(cats):
	for cat in cats:
		print("health: ", cat.health)
		print("age: ", cat.age)
		print("temper: ", cat.temper)
		print("health: ", cat.health)
		print("hunger: ", cat.hunger)
		print("thirst: ", cat.thirst)
		print("\n\n")

# Creating cat objects
def create_cats():
	cats = []
	for i in range(20):
		cell_is_occupied = True
		while cell_is_occupied:
			cell_is_occupied = False
			pos = [random.randint(1,num_rows), random.randint(1,num_cols)]
			for cat in cats:
				if cat.pos == pos:
					cell_is_occupied = True
			if (water_array[pos[0],pos[1]] > 0) or (food_array[pos[0],pos[1]] > 0):
				cell_is_occupied = True

		age = random.randint(0,4)
		temper = random.choice(["aggressive","friendly","meek"])
		sex = random.choice(["m","f"])
		cat = Cat(pos, age, temper, sex)
		cats.append(cat)
	return cats

if __name__ == "__main__":

	# terrain_filename = input("\nPlease enter a terrain data file:    ")
	# landmark_filename = input("\nPlease enter a landmark data file:    ")
	neighbourhood = input("\nPlease enter the desired neighbourhood (M or V):    ")
	terrain_array = read_terrain("terrain.csv")
	food_array, water_array = read_landmarks("landmarks.csv")
	cats = create_cats()
	# Initializing pygame
	gameDisplay = pygame.display.set_mode((display_width,display_height))
	pygame.display.set_caption("Cats")
	clock = pygame.time.Clock()
	crashed = False

	while not crashed:

		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				crashed = True												# Quits simulation if user closes pygame window
		
		draw_screen(terrain_array,food_array, water_array, cats)			# Updates the pygame display so that it
		pygame.display.update()												# draws the new frame
		move_cats(cats,terrain_array,food_array,water_array,neighbourhood)
		hunger_and_thirst(cats)		
		cats = kill_cats(cats)
		clock.tick(framerate)												# Updates at 2 frames per second

pygame.quit()
quit()
