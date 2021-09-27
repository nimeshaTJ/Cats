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
# 23/Sep/2021 - Added time of day and sleeping mechanic for cats.
# 25/Sep/2021 - Cats leave a scent when passing through a cell.
# 26/Sep/2021 - Added reproduction mechanic.
# 27/Sep/2021 - Cats search for food and water based on scent.

import pygame
import pygame.ftfont	
import random
import numpy as np
import csv
import sys

# Colours
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
green = (50,220,70)
blue = (30,90,160)
yellow = (200,220,0)
pink = (250,0,255)
cyan = (70,230,255)
grey = (130,130,130)

# Defining the perimeter of the simulation
num_rows = 50
num_cols = 50
cell_size = 10
display_width = (num_cols+2)*cell_size				# Width of display in pixels
display_height = (num_rows+2)*cell_size	+30			# Height of display in pixels
framerate = 2

# Defining the Cat class
class Cat():
	def __init__(self,pos,age,temper,sex):
		self.alive = True
		self.pos = pos
		self.age = age
		self.temper = temper   									# Can be friendly, aggressive, or meek 
		self.sex = sex              
		self.colour = white
		self.height = terrain_array[self.pos[0],self.pos[1]]
		self.attack_power = self.age*4    						# Older cats  deal more damage
		self.sleep_chance = random.uniform(0.01,0.05)
		self.engaged = False
		self.consuming = False
		self.fighting = False
		self.fleeing = False
		self.sleeping = False
		self.mating = False
		self.mating_cooldown = 0
		self.sleep_counter = 0
		self.health = 100
		self.thirst = 0
		self.hunger = 0
		self.parched = False
		self.starving = False

	def eat(self,foodpos,food_array):
		if self.hunger>=25:
			self.engaged = True
			self.consuming = True
			food_array[foodpos[0],foodpos[1]]-=0.5
			self.hunger-=15

	def drink(self,waterpos,water_array):
		if self.thirst>=25:
			self.engaged = True
			self.consuming = True
			water_array[waterpos[0],waterpos[1]]-=0.5
			self.thirst-=15		

	def interact(self,neighbours,terrain_array,food_array,water_array,neighbourhood,alive_cats):
			has_an_aggressive_neighbour = False
			for neighbour in neighbours:
				attack_power = self.attack_power

				if self.sex==neighbour.sex:

					if self.temper == "aggressive":
						if self.height>neighbour.height:
							attack_power *= 1.25 											# Cats on higher ground deal more damage
						if (not self.sleeping) or neighbour.temper=="aggressive":
							self.engaged = True
							self.fighting = True
							self.sleeping = False
							neighbour.health -= attack_power
						attack_power = self.attack_power	
					
					elif self.temper == "friendly":
						if self.height>neighbour.height:
							attack_power *= 1.25
						if (neighbour.temper == "aggressive") and (not neighbour.sleeping):	
							self.sleeping = False
							self.engaged = True
							self.fighting = True
							neighbour.health -= attack_power
						attack_power = self.attack_power

					else:
						if neighbour.temper == "aggressive":
							has_an_aggressive_neighbour = True
						if (not self.sleeping) or has_an_aggressive_neighbour:
							self.sleeping = False
							self.engaged = True
							self.fleeing = True
							valid_moves = get_valid_moves(self,terrain_array,food_array,water_array,cat_scent_array,neighbourhood,alive_cats)
							self.pos = random.choice(valid_moves)
							for move in valid_moves:
								new_neighbours = check_surroundings(self,move,alive_cats)[0]
								if len(new_neighbours)==0:
									self.pos = move
									break
		
	def sleep(self):
		if self.sleeping:
			if self.sleep_counter > 8:			# Cats sleep for 8 hours at a stretch if uninterrupted
				self.sleep_counter = 0
				self.sleeping = False
			else:
				if self.health <= 95:
					self.health += 5 			# Cats gain health while sleeping
				self.sleep_counter+=1
		else:
			self.sleep_counter = 0

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

# Returns a list of valid cells that a cat can move to on the next iteration
def get_valid_moves(cat,terrain_array,food_array,water_array,cat_scent_array,neighbourhood,alive_cats):
	possible_moves = []
	r,c = cat.pos[0],cat.pos[1]
	if neighbourhood=="M":
		possible_moves.extend([[r-1,c-1],[r-1,c],[r-1,c+1],[r,c-1],[r,c],[r,c+1],[r+1,c-1],[r+1,c],[r+1,c+1]])
	else:
		possible_moves.extend([[r-1,c],[r,c-1],[r,c],[r,c+1],[r+1,c]])

	valid_moves = [p for p in possible_moves]
	for cell in possible_moves:
		try:
			if cell[0]<1 or cell[0]>num_rows or cell[1]<1 or cell[1]>num_cols:							# Cats can't leave borders
				valid_moves.remove(cell)
			elif abs(terrain_array[cell[0],cell[1]] - terrain_array[cat.pos[0],cat.pos[1]]) > 4:		# Cats can't move across steep slopes
				valid_moves.remove(cell)
			elif (food_array[cell[0],cell[1]] > 0) or (water_array[cell[0],cell[1]] > 0):				# Cats can't walk on food or water
				valid_moves.remove(cell)
			else:
				for other_cat in alive_cats:
					if other_cat != cat and other_cat.pos == cell:										# Cats can't walk on other catss
						valid_moves.remove(cell)		
		except ValueError:
			pass
	avoided_scents = [v for v in valid_moves]
	for cell in valid_moves:
		if cat_scent_array[cell[0],cell[1]][1]==cat.sex and cat_scent_array[cell[0],cell[1]][0]!=cat:		# Cats avoid scents of the same sex 
			probability = cat_scent_array[cell[0],cell[1]][2]
			if random.random()<probability:
				avoided_scents.remove(cell)

	return avoided_scents

# Function that returns the cats, food cells and water cells within a cat's neighbourhood 
def check_surroundings(cat,pos,alive_cats):
	surrounding_cells = []
	r,c = pos[0],pos[1]
	if neighbourhood=="M":
		surrounding_cells.extend([[r-1,c-1],[r-1,c],[r-1,c+1],[r,c-1],[r,c+1],[r+1,c-1],[r+1,c],[r+1,c+1]])
	else:
		surrounding_cells.extend([[r-1,c],[r,c-1],[r,c+1],[r+1,c]])
	
	valid_surrounding_cells = [cell for cell in surrounding_cells]
	for cell in surrounding_cells:
		if abs(terrain_array[cell[0],cell[1]] - terrain_array[r,c]) > 4:
			valid_surrounding_cells.remove(cell)

	neighbours = [neighbour for neighbour in alive_cats if (neighbour!=cat) and (neighbour.pos in valid_surrounding_cells)]
	
	neighbouring_water = []
	neighbouring_food = []
	for cell in valid_surrounding_cells:
		if water_array[cell[0],cell[1]] > 0:
			neighbouring_water.append(cell)
		elif food_array[cell[0],cell[1]] > 0:
			neighbouring_food.append(cell)
	
	return neighbours, neighbouring_food, neighbouring_water

# Reproduction between two cats
def reproduce(cat1,cat2,cell):
	global hearts
	cat1.engaged = True
	cat1.mating = True
	cat1.mating_cooldown = 24
	cat2.engaged = True
	cat2.mating = True
	cat2.mating_cooldown = 24
	temper = random.choice(["aggressive","friendly","meek"])
	sex = random.choice(["m","f"])
	baby = Cat(cell,1,temper,sex)
	heart_pos = cell_size*(cat1.pos[1]+cat2.pos[1])/2 , cell_size*(cat1.pos[0]-2)
	hearts.append(heart_pos)
	return baby

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

# Function that increases hunger and thirst each iteration, and hurts the cat if hunger and thirst get too high
def hunger_and_thirst(alive_cats):
	for cat in alive_cats:
		if cat.hunger >= 100:
			cat.starving = True
		else:
			cat.hunger+=1			
		if cat.thirst >= 100:
			cat.parched = True
		else:
			cat.thirst+=2
		if cat.starving or cat.parched:
			cat.health-=1
	
		cat.starving = False
		cat.parched = False

# Funnction that assigns a colour to each cat based on its attributes
def cat_colour(alive_cats):
	for cat in alive_cats:
		cat.colour = white
		if cat.fighting:
			cat.colour = red
		elif cat.fleeing:
			cat.colour = yellow
		elif cat.sleeping:
			cat.colour = grey

# Function that assigns colour and transparency to a cat's scent
def cat_scent_colour(sex,value):
	alpha = value*255
	if sex=="f":
		colour = pink
	else:
		colour = cyan
	scent_image = pygame.Surface((cell_size,cell_size))
	scent_image.set_alpha(alpha)
	pygame.draw.rect(scent_image,colour,scent_image.get_rect())
	return scent_image,colour

# Function to assign colour and transparency for food and water scent
def landmark_scent_colour(type_of_landmark,value):
	if type_of_landmark=="food":
		colour = green
	else:
		colour = blue
	alpha = value*255
	scent_image = pygame.Surface((cell_size,cell_size))
	scent_image.set_alpha(alpha)
	pygame.draw.rect(scent_image,colour,scent_image.get_rect())
	return scent_image

# Kills cats if their health is below 0
def kill_cats(alive_cats,dead_cats):
	for cat in alive_cats:
		if cat.health<=0:
			dead_cats.append(cat)
	alive_cats = [cat for cat in alive_cats if cat.health>0]
	return alive_cats, dead_cats

# Function that maps height values (0 to 10) to RGB (dark brown to light brown)
def assign_terrain_colour(height):
	R = 5*height + 40
	G = -2*height + 90
	B = 0
	return((R,G,B))

def show_cats(alive_cats,dead_cats):
	for i,cat in enumerate(alive_cats):
		print("Cat ",i,": ALIVE")
		print("pos: ", cat.pos)
		print("health: ", cat.health)
		print("age: ", cat.age)
		print("temper: ", cat.temper)
		print("hunger: ", cat.hunger)
		print("thirst: ", cat.thirst)
		print("attack: ", cat.attack_power)
		print("\n\n")
	for i,cat in enumerate(dead_cats):
		print("Cat ",i,": DEAD\n\n\n")

# Creating cat objects
def create_cats(n):
	alive_cats = []
	for i in range(n):
		cell_is_occupied = True
		while cell_is_occupied:
			cell_is_occupied = False
			pos = [random.randint(1,num_rows), random.randint(1,num_cols)]
			for cat in alive_cats:
				if cat.pos == pos:
					cell_is_occupied = True
			if (water_array[pos[0],pos[1]] > 0) or (food_array[pos[0],pos[1]] > 0):
				cell_is_occupied = True
		age = random.randint(1,5)
		temper = random.choice(["aggressive","friendly","meek"])
		sex = random.choice(["m","f"])
		cat = Cat(pos, age, temper, sex)
		alive_cats.append(cat)
	return alive_cats

# Main sequence of events
def main_loop(alive_cats,terrain_array,food_array,water_array,cat_scent_array,neighbourhood,hour_of_day):
	births = []
	for cat in alive_cats:
		cat.height = terrain_array[cat.pos[0],cat.pos[1]]
		cat.engaged = False
		cat.consuming = False
		cat.fighting = False
		cat.fleeing = False	
		cat.mating = False
		if cat.mating_cooldown>0:
			cat.mating_cooldown-=1
		neighbours,neighbouring_food,neighbouring_water = check_surroundings(cat,cat.pos,alive_cats)
		if len(neighbours)>0:
			cat.interact(neighbours,terrain_array,food_array,water_array,neighbourhood,alive_cats)	
		if not (cat.fighting or cat.fleeing):
			if (not cat.sleeping) and (len(neighbouring_food)>0 or len(neighbouring_water)>0):		
				eat_or_drink(cat,neighbouring_food,neighbouring_water,food_array,water_array)

	for cat in alive_cats:
		if (not cat.engaged) and (not cat.mating) and (not cat.sleeping):
			neighbours = check_surroundings(cat,cat.pos,alive_cats)[0]
			for neighbour in neighbours:
				if (cat.sex!=neighbour.sex) and (not neighbour.engaged) and (not neighbour.mating) and (not neighbour.sleeping):
					if (cat.hunger<75) and (cat.thirst<75) and (neighbour.hunger<75) and (neighbour.thirst<75):
						if (cat.mating_cooldown==0) and (neighbour.mating_cooldown==0):
							potential_spots = get_valid_moves(cat,terrain_array,food_array,water_array,cat_scent_array,neighbourhood,alive_cats)
							chosen_spot = random.choice(potential_spots)
							baby = reproduce(cat,neighbour,chosen_spot)
							births.append(baby)

	for cat in alive_cats:
		initial_sleep_chance = cat.sleep_chance
		if hour_of_day > 21 or hour_of_day < 5:						# More likely to sleep at night
			cat.sleep_chance*=5
		multiplier = -0.02*cat.health + 3 							# The lower the cat's health, the more likely it is to go to sleep
		cat.sleep_chance*=multiplier
		if random.random()<cat.sleep_chance and (cat.hunger < 50 and cat.thirst < 50) and (not cat.engaged):			# Cats only sleep if they are not hungry or thirsty
			cat.sleeping = True
		cat.sleep_chance = initial_sleep_chance

	for cat in alive_cats:
		cat.sleep()
		if (not cat.engaged) and (not cat.sleeping):
			valid_moves = get_valid_moves(cat,terrain_array,food_array,water_array,cat_scent_array,neighbourhood,alive_cats)
			choices = [v for v in valid_moves]
			if cat.hunger<75 and cat.thirst<75 and cat.mating_cooldown==0:
				neighbour_scent_value = 0
				for move in valid_moves:
					scent = cat_scent_array[move[0],move[1]]
					if scent[1]!=None and scent[1]!=cat.sex:
						if scent[2]>neighbour_scent_value:
							neighbour_scent_value = scent[2]
							choices = [move]
						elif scent[2]==neighbour_scent_value:
							choices.append(move)
				pass
			else:
				food_scents = []
				water_scents = []
				temp_choices = []
				for move in valid_moves:
					if food_scent_array[move[0],move[1]]>0:
						food_scents.append(food_scent_array[move[0],move[1]])
					if water_scent_array[move[0],move[1]]>0:
						water_scents.append(water_scent_array[move[0],move[1]])
				if (cat.hunger>50) and (cat.hunger>cat.thirst or len(water_scents)==0):
					for move in valid_moves:
						probability = food_scent_array[move[0],move[1]]
						if random.random()<=probability:
							temp_choices.append(move)
				elif (cat.thirst>50) and (cat.thirst>=cat.hunger or len(food_scents)==0):
					for move in valid_moves:
						probability = water_scent_array[move[0],move[1]]
						if random.random()<=probability:
							temp_choices.append(move)
				if len(temp_choices)>0:
					choices = [c for c in temp_choices]
			cat.pos = random.choice(choices)
	
	alive_cats.extend(births)			
	cat_colour(alive_cats)	
	hunger_and_thirst(alive_cats)
	return len(births)

# Function that makes cats leave a scent (male or female) that evaporates over time
def update_cat_scents(alive_cats,cat_scent_array):
	temp_scents = cat_scent_array.copy()
	for cat in alive_cats:
		temp_scents[cat.pos[0],cat.pos[1]] = [cat,cat.sex,1]
	for r in range(num_rows):
		for c in range(num_cols):
			temp_scents[r+1,c+1][2]*=0.9
			if temp_scents[r+1,c+1][2]<0.01:
				temp_scents[r+1,c+1] = [None,None,0]
	return temp_scents				

# Function that diffuses the scent of food and water into the environment; The diffusion model is sourced from heat.py of Prac03   
def diffuse(array,neighbourhood):
	copy = array.copy()
	for r in range(1,len(array)-1):
		for c in range(1,len(array[0])-1):
			value = array[r,c]
			change = 0
			if neighbourhood == 'M':
				new = (array[r-1,c-1]*0.1 + array[r-1,c]*0.1+ array[r-1,c+1]*0.1 + array[r,c-1]*0.1+ array[r,c]*0.2 + array[r,c+1]*0.1+ array[r+1,c-1]*0.1 + array[r+1,c]*0.1+ array[r+1,c+1]*0.1)
			else:
				new = (array[r-1,c]*0.15 + array[r,c-1]*0.15 + array[r,c]*0.4 + array[r,c+1]*0.15 + array[r+1,c]*0.15)
			if new<0.01:
				copy[r,c]=0
			else:
				copy[r,c]=new
	return copy

# Function to increment the current hour and day
def increment_time(hour, day, hour_of_day):
	hour+=1
	day = hour//24
	hour_of_day = hour%24
	return hour,day,hour_of_day

# Function that draws and displays the current state of the environment (terrain, landmarks, and cats)
def draw_screen(terrain_array,food_array, water_array, alive_cats, dead_cats, show_scents, heart_image, hearts):
	gameDisplay.fill(black)	
	for row in range(num_rows):
		for col in range(num_cols):
			r = row+1
			c = col+1
			terrain_colour = assign_terrain_colour(terrain_array[r,c])	
			pygame.draw.rect(gameDisplay, terrain_colour,[c*cell_size,r*cell_size,cell_size,cell_size])					
			pygame.draw.circle(gameDisplay,green,((c+0.5)*cell_size,(r+0.5)*cell_size),food_array[r,c]*cell_size/2)	# Food are green circles
			pygame.draw.circle(gameDisplay,blue,((c+0.5)*cell_size,(r+0.5)*cell_size),water_array[r,c]*cell_size/2)	# Water are blue circles
			if show_scents:
				scent_image,scentcolour = cat_scent_colour(cat_scent_array[r,c][1],cat_scent_array[r,c][2])
				if cat_scent_array[r,c][2]>0:
					gameDisplay.blit(scent_image, (c*cell_size,r*cell_size))
			if show_food_scent:
				food_scent_image = landmark_scent_colour("food",food_scent_array[r,c])
				if food_scent_array[r,c]>0:
					gameDisplay.blit(food_scent_image, (c*cell_size,r*cell_size))
			if show_water_scent:
				water_scent_image = landmark_scent_colour("water",water_scent_array[r,c])
				if water_scent_array[r,c]>0:
					gameDisplay.blit(water_scent_image, (c*cell_size,r*cell_size))

	for cat in dead_cats:
		r = cat.pos[0]
		c = cat.pos[1]
		pygame.draw.line(gameDisplay , black, (c*cell_size,r*cell_size), ((c+1)*cell_size,(r+1)*cell_size))
		pygame.draw.line(gameDisplay , black, ((c+1)*cell_size,r*cell_size), (c*cell_size,(r+1)*cell_size))
	for cat in alive_cats:
		r = cat.pos[0]
		c = cat.pos[1]
		pygame.draw.circle(gameDisplay , cat.colour, ((c+0.5)*cell_size,(r+0.5)*cell_size), cell_size*(cat.age/16 + 1/4))	# Cats are white circles
	for heart in hearts:
		gameDisplay.blit(heart_image,(heart[0],heart[1]))

# Function that displays the current time (in days and hours) on the screen	
def display_time(hour,day,hour_of_day,fontface,gameDisplay):
	line1 = "Day "+str(day)+", Hour "+str(hour_of_day)
	line1display = fontface.render(line1,True,white)
	line2 = "Total hours: "+str(hour)
	line2display = fontface.render(line2,True,white)
	gameDisplay.blit(line1display,(10,(num_rows+1)*cell_size))
	gameDisplay.blit(line2display,(10,(num_rows+2)*cell_size+5))	

# Function to print statistics at the end of the simulation
def show_stats(init_pop,alive_cats,dead_cats,births):
	agr = 0
	frnd = 0
	meek = 0
	total_age = 0
	for cat in alive_cats:
		if cat.temper == "aggressive":
			agr+=1
		elif cat.temper == "friendly":
			frnd+=1
		elif cat.temper == "meek":
			meek+=1
		total_age += cat.age
	if len(alive_cats)>0:
		avg_age = round(total_age/len(alive_cats) , 2)
	else:
		avg_age = 0	

	print()
	print("Initial population: ",init_pop)
	print("Births: ", births)
	print("Deaths: ", len(dead_cats))
	print("Current population: ",len(alive_cats))
	print()
	print("Number of aggressive cats: ", agr)
	print("Number of friendly cats: ", frnd)
	print("Number of meek cats: ", meek)
	print("Average age of cats: ",avg_age)
	print()

if __name__ == "__main__":

	neighbourhood = input("\nPlease enter the desired neighbourhood (M or V):\n")
	max_hours = int(input("How many hours should be simulated? (enter 0 for indefinite):\n"))
	
	terrain_array = read_terrain(sys.argv[1])
	food_array, water_array = read_landmarks(sys.argv[2])
	food_scent_array = np.zeros((num_rows+2,num_cols+2))
	water_scent_array = np.zeros((num_rows+2,num_cols+2))
	init_pop = 20
	alive_cats = create_cats(init_pop)
	births = 0
	dead_cats = []
	cat_scent_array = np.empty((num_rows+2,num_cols+2),dtype = object)
	for r in range(num_rows+2):
		for c in range(num_cols+2):
			cat_scent_array[r,c] = [None,None,0]
			food_scent_array[r,c] = food_array[r,c]
			water_scent_array[r,c] = water_array[r,c]

	# Initializing pygame
	pygame.init()
	gameDisplay = pygame.display.set_mode((display_width,display_height))
	fontface = pygame.ftfont.SysFont('Courier New',15,bold=True)
	pygame.display.set_caption("Cats")
	clock = pygame.time.Clock()

	crashed = False
	hour,day,hour_of_day = 0,0,0
	show_scents = False
	show_food_scent = False
	show_water_scent = False
	heart_image = pygame.image.load("heart.png")
	while not crashed:
		hearts = []

		for event in pygame.event.get():

			if (event.type == pygame.QUIT):															# Quits simulation if user closes pygame window 
				crashed = True	
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_s:
					show_scents = not show_scents
				if event.key == pygame.K_f:
					show_food_scent = not show_food_scent
				if event.key == pygame.K_w:
					show_water_scent = not show_water_scent

		if (max_hours>0) and (hour==max_hours):														# Quits the simulation after the specified number of iterations
			crashed = True

		cat_scent_array = update_cat_scents(alive_cats,cat_scent_array)
		births += main_loop(alive_cats,terrain_array,food_array,water_array,cat_scent_array,neighbourhood,hour_of_day)
		food_scent_array = np.where(food_array>0,food_array,diffuse(food_scent_array,neighbourhood))
		water_scent_array = np.where(water_array>0,water_array,diffuse(water_scent_array,neighbourhood))
		alive_cats, dead_cats = kill_cats(alive_cats,dead_cats)
		clock.tick(framerate)																						
		draw_screen(terrain_array,food_array, water_array, alive_cats, dead_cats, show_scents, heart_image, hearts)	    # Updates the pygame display
		display_time(hour,day,hour_of_day,fontface,gameDisplay)
		pygame.display.update()																							# Draws the new frame
		hour,day,hour_of_day = increment_time(hour,day,hour_of_day)

pygame.quit()
show_stats(init_pop,alive_cats,dead_cats,births)
quit()