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
# 20/Sep/2021 - Implemented engagement rules for cats; restructured sections of code and improved movement system.

import pygame
import random
import numpy as np
import csv

# Colours
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
green = (15,150,50)
blue = (30,90,160)
yellow = (200,220,0)

# Defining the perimeter of the simulation
num_rows = 50
num_cols = 50
cell_size = 10
display_width = (num_cols+2)*cell_size           # Width of display in pixels
display_height = (num_rows+2)*cell_size			 # Height of display in pixels
framerate = 2

# Cat class
class Cat():
	def __init__(self,pos,age,temper,sex,height):
		self.pos = pos
		self.age = age
		self.temper = temper   					# Can be friendly, aggressive, or meek 
		self.sex = sex              
		self.colour = white
		self.height = height
		self.attack_power = self.age*5    	# Older cats  deal more damage
		self.neighbours = []
		self.engaged = False
		self.fighting = False
		self.fleeing = False
		self.health = 100
		self.thirst = 0
		self.hunger = 0

	def eat(self,foodpos,food_array):
		if self.hunger>=25:
			food_array[foodpos[0],foodpos[1]]-=2.5
			self.hunger-=15

	def drink(self,waterpos,water_array):
		if self.thirst>=25:
			water_array[waterpos[0],waterpos[1]]-=2.5
			self.thirst-=15		

	def interact(self,neighbours,terrain_array,food_array,water_array,neighbourhood,cats):
		attack_power = self.attack_power
		if self.temper == "aggressive":
			self.engaged = True
			self.fighting = True
			for neighbour in neighbours:
				if self.height>neighbour.height:
					attack_power *= 1.5 					# Cats on higher ground deal more damage
				neighbour.health -= attack_power
				attack_power = self.attack_power
		
		elif self.temper == "friendly":
			for neighbour in neighbours:
				if self.height>neighbour.height:
					attack_power *= 1.5
				if neighbour.temper == "aggressive":
					self.engaged = True
					self.fighting = True
					neighbour.health -= attack_power
				attack_power = self.attack_power

		else:
			self.engaged = True
			self.fleeing = True
			valid_moves = get_valid_moves(self,terrain_array,food_array,water_array,neighbourhood,cats)
			self.pos = random.choice(valid_moves)
			for move in valid_moves:
				new_neighbours = check_surroundings(self,move,cats)[0]
				if len(new_neighbours)==0:
					self.pos = move
					break


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
def get_valid_moves(cat,terrain_array,food_array,water_array,neighbourhood,cats):
	possible_moves = []
	r,c = cat.pos[0],cat.pos[1]
	if neighbourhood=="M":
		possible_moves.extend([[r-1,c-1],[r-1,c],[r-1,c+1],[r,c-1],[r,c],[r,c+1],[r+1,c-1],[r+1,c],[r+1,c+1]])
	else:
		possible_moves.extend([[r-1,c],[r,c-1],[r,c],[r,c+1],[r+1,c]])

	valid_moves = [p for p in possible_moves]
	for cell in possible_moves:
		if cell[0]<1 or cell[0]>num_rows or cell[1]<1 or cell[1]>num_cols:							# Cats can't leave borders
			valid_moves.remove(cell)
		elif abs(terrain_array[cell[0],cell[1]] - terrain_array[cat.pos[0],cat.pos[1]]) > 4:		# Cats can't move across steep slopes
			valid_moves.remove(cell)
		elif (food_array[cell[0],cell[1]] > 0) or (water_array[cell[0],cell[1]] > 0):				# Cats can't walk on food or water
			valid_moves.remove(cell)
		else:
			for other_cat in cats:
				if other_cat != cat and other_cat.pos == cell:
					valid_moves.remove(cell)		
			
	return valid_moves

def check_surroundings(cat,pos,cats):
	surrounding_cells = []
	r,c = pos[0],pos[1]
	if neighbourhood=="M":
		surrounding_cells.extend([[r-1,c-1],[r-1,c],[r-1,c+1],[r,c-1],[r,c+1],[r+1,c-1],[r+1,c],[r+1,c+1]])
	else:
		surrounding_cells.extend([[r-1,c],[r,c-1],[r,c+1],[r+1,c]])
	
	neighbours = [neighbour for neighbour in cats if (neighbour!=cat) and (neighbour.pos in surrounding_cells)]
	
	neighbouring_water = []
	neighbouring_food = []
	for cell in surrounding_cells:
		if water_array[cell[0],cell[1]] > 0:
			neighbouring_water.append(cell)
		elif food_array[cell[0],cell[1]] > 0:
			neighbouring_food.append(cell)
	
	return neighbours, neighbouring_food, neighbouring_water
	
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
		cat.hunger+=0.1
		cat.thirst+=0.2

def set_cat_colour(cat):
	cat.colour = white
	if cat.fighting:
		cat.colour = red
	elif cat.fleeing:
		cat.colour = yellow
	
def kill_cats(cats):
	alive_cats = [cat for cat in cats if (cat.health>0 and cat.hunger<100 and cat.thirst<100)]
	return alive_cats

# Function that maps height values (0 to 10) to RGB (dark brown to light brown)
def assign_terrain_colour(height):
	R = 5*height + 40
	G = -2*height + 90
	B = 0
	return((R,G,B))

# Function that draws and displays the current state of the environment (terrain, landmarks, and cats)
def draw_screen(terrain_array,food_array, water_array, cats):
	
	for r in range(num_rows+2):
		for c in range(num_cols+2):
			terrain_colour = assign_terrain_colour(terrain_array[r,c])													
			pygame.draw.rect(gameDisplay, terrain_colour,[c*cell_size,r*cell_size,cell_size,cell_size])					
			pygame.draw.circle(gameDisplay,yellow,((c+0.5)*cell_size,(r+0.5)*cell_size),food_array[r,c]*cell_size/10)	# Food are yellow circles
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
		height = terrain_array[pos[0],pos[1]]
		cat = Cat(pos, age, temper, sex, height)
		cats.append(cat)

	return cats

def main_loop(cats,terrain_array,food_array,water_array,neighbourhood):
	for cat in cats:
		cat.engaged = False
		cat.fighting = False
		cat.fleeing = False
		neighbours,neighbouring_food,neighbouring_water = check_surroundings(cat,cat.pos,cats)
		cat.neighbours = neighbours
		if len(neighbours)>0:
			cat.interact(neighbours,terrain_array,food_array,water_array,neighbourhood,cats)	
		else:
			if len(neighbouring_food)>0 or len(neighbouring_water)>0:		
				eat_or_drink(cat,neighbouring_food,neighbouring_water,food_array,water_array)

	for cat in cats:
		if not cat.engaged:
			valid_moves = get_valid_moves(cat,terrain_array,food_array,water_array,neighbourhood,cats)
			cat.pos = random.choice(valid_moves)
			cat.height = terrain_array[cat.pos[0],cat.pos[1]]
				
	for cat in cats:
		set_cat_colour(cat)
	
	hunger_and_thirst(cats)
	
if __name__ == "__main__":

	# terrain_filename = input("\nPlease enter a terrain data file:    ")
	# landmark_filename = input("\nPlease enter a landmark data file:    ")
	neighbourhood = input("\nPlease enter the desired neighbourhood (M or V):    ")
	terrain_array = read_terrain("terrain.csv")
	food_array, water_array = read_landmarks("landmarks.csv")
	max_iterations = int(input("How many hours should be simulated? (enter 0 for indefinite)\n"))
	cats = create_cats()
	# Initializing pygame
	gameDisplay = pygame.display.set_mode((display_width,display_height))
	pygame.display.set_caption("Cats")
	clock = pygame.time.Clock()
	crashed = False

	iteration_count = 0
	while not crashed:

		for event in pygame.event.get():

			if (event.type == pygame.QUIT):											# Quits simulation if user closes pygame window 
				crashed = True				

		if (max_iterations>0) and (iteration_count==max_iterations):				# Quits the simulation after the specified number of iterations
			crashed = True

		draw_screen(terrain_array,food_array, water_array, cats)					# Updates the pygame display so that it
		pygame.display.update()														# draws the new frame
		main_loop(cats,terrain_array,food_array,water_array,neighbourhood)
		cats = kill_cats(cats)
		clock.tick(framerate)														# Updates at 2 frames per second
		iteration_count += 1

pygame.quit()
#show_cats(cats)
quit()
