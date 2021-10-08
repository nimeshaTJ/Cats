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
# 29/Sep/2021 - Added event log and simulation statistics. 
# 30/Sep/2021 - Log, statistics and grid state can be saved to a new folder

import pygame
import pygame.ftfont
import os
import datetime
import random
import numpy as np
import csv
import sys

main_dir = os.getcwd()

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

# Simulation parameters
framerate = 20 										# Number of timesteps run per second
mating_cooldown_time = 24
jump_height = 4
sleep_hours = 8
eating_threshold = 25
drinking_threshold = 25

# Defining the Cat class
class Cat():
	def __init__(self,index,pos,age,temper,sex):
		self.alive = True
		self.index = index
		self.pos = pos
		self.age = age
		self.temper = temper   									# Can be friendly, aggressive, or meek
		self.sex = sex
		self.colour = None
		self.height = terrain_array[self.pos[0],self.pos[1]]
		self.attack_power = self.age*4    						# Older cats  deal more damage
		self.sleep_chance = random.uniform(0.01,0.05)
		self.engaged = False									# Whether the cat is currently interacting with something
		self.consuming = False									# Whether the cat is currently eating or drinking
		self.fighting = False									# Whether the cat is currently fighting another cat
		self.fleeing = False									# Whether the cat is currently running away from another cat
		self.sleeping = False									# Whether the cat is currently sleeping
		self.mating = False										# Whether the cat is currently mating with another cat
		self.mating_cooldown = 0  								# A timer that dictates how long the cat has to wait before it can mate again
		self.sleep_counter = 0 									# Keeps track of how long the cat has been sleeping for
		self.health = 100
		self.thirst = 0
		self.hunger = 0
		self.dehydrated = False									# True when the cat's thirst is maxed out (at 100)
		self.starving = False									# True when the cat's hunger is maxed put (at 100)
		self.total_food_eaten = 0
		self.total_water_drunk = 0	

	def __str__(self):
		return "Cat "+str(self.index)

	# Method for displaying the cat's attributes
	def display_self(self):
		if self.alive:
			status = 'ALIVE'
		else:
			status = 'DEAD'
		if self.temper == 'aggressive':
			tabs = "\t"
		else:
			tabs = "\t\t"
		spaces = 8-len(status)
		health = str(int(self.health))+"/100"
		return "Cat "+str(self.index)+"\t|  "+status+spaces*" "+"|  Health: "+health+"\t|  Age: "+str(self.age)+"  |  Temper: "+self.temper+tabs+"|  Sex: "+self.sex+"\t|  Current position: "+str(self.pos)

	# Method that assigns a colour to the cat based on its attributes	
	def set_colour(self):
		if self.sex=='male':
			self.colour = cyan
		else:
			self.colour = pink
		if self.fighting:
			self.colour = red
		elif self.fleeing:
			self.colour = yellow
		elif self.sleeping:
			self.colour = grey

	# Method that increases hunger and thirst each iteration, and hurts the cat if hunger and thirst get too high
	def hunger_and_thirst(self):
		self.starving = False
		self.dehydrated = False
	
		if self.hunger >= 100:
			self.starving = True										
		else:
			self.hunger+=0.5					# Cats get more hungry after each timestep		
		if self.thirst >= 100:
			self.dehydrated = True
		else:
			self.thirst+=1 						# Cats get thirsty faster than hungry
		if self.starving or self.dehydrated:			
			self.health-=1 						# Cat loses health over time if starving 
	

	def eat(self,foodpos,food_array):
		if self.hunger>=eating_threshold:						# Cat eats if it's hungrier than a certain threshold
			self.engaged = True
			self.consuming = True
			food_array[foodpos[0],foodpos[1]]-=0.5
			self.hunger-=15
			self.total_food_eaten+=0.5

	def drink(self,waterpos,water_array):
		if self.thirst>=drinking_threshold:						# Cat drinks if it's thirstier than a certain threshold
			self.engaged = True
			self.consuming = True
			water_array[waterpos[0],waterpos[1]]-=0.5
			self.thirst-=15
			self.total_water_drunk+=0.5		

	# Method for handling interactions with cats of the same sex
	def interact(self,neighbours,terrain_array,food_array,water_array,neighbourhood,alive_cats):
		has_an_aggressive_neighbour = False
		for neighbour in neighbours:
			attack_power = self.attack_power

			if self.sex==neighbour.sex:

				# Aggressive cats attack all other cats (of the same sex) unless sleeping
				if self.temper == "aggressive":
					if self.height>neighbour.height:
						attack_power *= 1.25 												# Cats on higher ground deal more damage
					if (not self.sleeping) or neighbour.temper=="aggressive":				
						self.engaged = True
						self.fighting = True
						self.sleeping = False												
						neighbour.health -= attack_power
					attack_power = self.attack_power	
				
				# Friendly cats only attak aggressive cats (of the same sex)
				elif self.temper == "friendly":
					if self.height>neighbour.height:
						attack_power *= 1.25
					if (neighbour.temper == "aggressive") and (not neighbour.sleeping):	
						self.sleeping = False
						self.engaged = True
						self.fighting = True
						neighbour.health -= attack_power
					attack_power = self.attack_power

				# Meek cats run away from all types of cats (of the same sex) unless sleeping
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

	# Method for handling behaviour while sleeping	
	def sleep(self):
		if self.sleeping:
			if self.sleep_counter > sleep_hours:			# Cats sleep for 'sleep_hours' number of hours at a stretch if uninterrupted
				self.sleep_counter = 0
				self.sleeping = False
			else:
				if self.health <= 95:
					self.health += 5 						# Cats gain health while sleeping
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
			try:														# Exception handling for data files of mismatching dimensions	
				terrain_array[r+1,c+1] = int(terrain_list[r][c])        
			except IndexError:
				pass
	return terrain_array

# Function that reads in food and water data from a file and returns them as arrays
def read_landmarks(landmark_filename):
	food_array = np.zeros((num_rows+2,num_cols+2))
	water_array = np.zeros((num_rows+2,num_cols+2)) 
	with open(landmark_filename,'r') as landmark_file:
		landmark_list = list(csv.reader(landmark_file))
			
	for r in range(len(landmark_list)):
		for c in range(len(landmark_list[0])):
			value = landmark_list[r][c]
			if value != "":
				try:													# Exception handling for data files of mismatching dimensions	
					if value == "F":
						food_array[r+1,c+1] = 1					
					else:
						water_array[r+1,c+1] = 1
				except IndexError:
 					pass
	return food_array, water_array

# Function that returns a list of valid cells that a cat can move to on the next iteration
def get_valid_moves(cat,terrain_array,food_array,water_array,cat_scent_array,neighbourhood,alive_cats):
	possible_moves = []
	r,c = cat.pos[0],cat.pos[1]
	if neighbourhood=="M":																								# Moore neighbourhood
		possible_moves.extend([[r-1,c-1],[r-1,c],[r-1,c+1],[r,c-1],[r,c],[r,c+1],[r+1,c-1],[r+1,c],[r+1,c+1]])
	else:																												# Von Neumann neighbourhood
		possible_moves.extend([[r-1,c],[r,c-1],[r,c],[r,c+1],[r+1,c]])

	valid_moves = [p for p in possible_moves]
	for cell in possible_moves:
		try:
			if cell[0]<1 or cell[0]>num_rows or cell[1]<1 or cell[1]>num_cols:									# Cats can't leave borders
				valid_moves.remove(cell)
			elif abs(terrain_array[cell[0],cell[1]] - terrain_array[cat.pos[0],cat.pos[1]]) > jump_height:		# Cats can't move across steep slopes
				valid_moves.remove(cell)
			elif (food_array[cell[0],cell[1]] > 0) or (water_array[cell[0],cell[1]] > 0):						# Cats can't walk on food or water
				valid_moves.remove(cell)
			else:
				for other_cat in alive_cats:
					if other_cat != cat and other_cat.pos == cell:												# Cats can't walk on other cats
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
	if neighbourhood=="M":																							# Moore neighbourhood
		surrounding_cells.extend([[r-1,c-1],[r-1,c],[r-1,c+1],[r,c-1],[r,c+1],[r+1,c-1],[r+1,c],[r+1,c+1]])
	else:																											# Von Neumann neighbourhood
		surrounding_cells.extend([[r-1,c],[r,c-1],[r,c+1],[r+1,c]])
	
	valid_surrounding_cells = [cell for cell in surrounding_cells]	
	for cell in surrounding_cells:
		if abs(terrain_array[cell[0],cell[1]] - terrain_array[r,c]) > jump_height:											# Cats don't interact with cells that are across a steep slope
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

# Reproduction between two cats
def reproduce(birth_index,cat1,cat2,cell):
	index = len(alive_cats)+len(dead_cats)+birth_index
	cat1.engaged = True
	cat1.mating = True
	cat1.mating_cooldown = mating_cooldown_time														# Cats have a 24-hour cooldown time before they can reproduce again
	cat2.engaged = True
	cat2.mating = True
	cat2.mating_cooldown = mating_cooldown_time
	temper = random.choice(["aggressive","friendly","meek"])
	sex = random.choice(['male','female'])
	baby = Cat(index,cell,1,temper,sex)
	heart_pos = cell_size*(cat1.pos[1]+cat2.pos[1])/2 , cell_size*(cat1.pos[0]-2)
	hearts.append(heart_pos)														# Creating a heart image to be drawn to the screen
	event = "Day "+str(day)+", Hour "+str(hour_of_day)+": Cat "+str(cat1.index)+" and Cat "+str(cat2.index)+" gave birth to Cat "+str(baby.index)+"!\n"
	event_log.append(event)
	print(event)															
	return baby

# Function that maps height values (0 to 10) to RGB (dark brown to light brown)
def assign_terrain_colour(height):
	R = 5*height + 40
	G = -2*height + 90
	B = 0
	return((R,G,B))

# Function that assigns colour and transparency to a cat's scent
def cat_scent_colour(sex,value):
	alpha = value*255
	if sex=='female':
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

# Function that makes cats leave a scent (male or female) that evaporates over time
def update_cat_scents(alive_cats,cat_scent_array):
	temp_scents = cat_scent_array.copy()
	for cat in alive_cats:
		temp_scents[cat.pos[0],cat.pos[1]] = [cat,cat.sex,1]		# Each element of this array holds the cat that created the scent, the cat's sex, and the intensity of the scent at that cell	
	for r in range(num_rows):
		for c in range(num_cols):
			temp_scents[r+1,c+1][2]*=0.9
			if temp_scents[r+1,c+1][2]<0.01:
				temp_scents[r+1,c+1] = [None,None,0]
	return temp_scents				

# Function that diffuses the scent of food and water into the environment; The diffusion model is sourced from heat.py from COMP1005 Prac05
# Maxville, Valerie. 2021. “heat.py” Prac05 supporting files, COMP1005 Fundamentals of Programming, Semester 2, 2021
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

# Function that kills cats if their health is below 0
def kill_cats(alive_cats,dead_cats):
	for cat in alive_cats:
		if cat.health<=0:
			cat.health = 0
			cat.alive = False
			dead_cats.append(cat)
			if cat.fighting:
				event = "Day "+str(day)+", Hour "+str(hour_of_day)+": Cat "+str(cat.index)+" has been killed.\n"
			elif cat.dehydrated:
				event = "Day "+str(day)+", Hour "+str(hour_of_day)+": Cat "+str(cat.index)+" has died of thirst.\n"
			else:
				event = "Day "+str(day)+", Hour "+str(hour_of_day)+": Cat "+str(cat.index)+" has died of hunger.\n"
			event_log.append(event)
			print(event)
	alive_cats = [cat for cat in alive_cats if cat.alive]
	return alive_cats, dead_cats

# Function that creates cat objects
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
		sex = random.choice(['male','female'])
		cat = Cat(i+1, pos, age, temper, sex)
		alive_cats.append(cat)
	return alive_cats

# Function that draws and displays the current state of the environment (terrain, landmarks, and cats)
def draw_screen(terrain_array,food_array, water_array, alive_cats, dead_cats, show_scents, heart_image, hearts):
	gameDisplay.fill(black)	
	for row in range(num_rows):
		for col in range(num_cols):
			r = row+1
			c = col+1
			terrain_colour = assign_terrain_colour(terrain_array[r,c])	
			pygame.draw.rect(gameDisplay, terrain_colour,[c*cell_size,r*cell_size,cell_size,cell_size])					
			pygame.draw.circle(gameDisplay,green,(int((c+0.5)*cell_size),int((r+0.5)*cell_size)),int(food_array[r,c]*cell_size/2))	# Food are green circles
			pygame.draw.circle(gameDisplay,blue,(int((c+0.5)*cell_size),int((r+0.5)*cell_size)),int(water_array[r,c]*cell_size/2))	# Water are blue circles
			if show_scents:
				scent_image,scentcolour = cat_scent_colour(cat_scent_array[r,c][1],cat_scent_array[r,c][2])
				if cat_scent_array[r,c][2]>0:
					gameDisplay.blit(scent_image, (c*cell_size,r*cell_size))					# Drawing cat scents to the screen
			if show_food_scent:
				food_scent_image = landmark_scent_colour("food",food_scent_array[r,c])
				if food_scent_array[r,c]>0:
					gameDisplay.blit(food_scent_image, (c*cell_size,r*cell_size))				# Drawing food scents to the screen
			if show_water_scent:
				water_scent_image = landmark_scent_colour("water",water_scent_array[r,c])
				if water_scent_array[r,c]>0:
					gameDisplay.blit(water_scent_image, (c*cell_size,r*cell_size))				# Drawing water scents to the screen

	for cat in dead_cats:
		r = cat.pos[0]
		c = cat.pos[1]
		pygame.draw.line(gameDisplay , black, (c*cell_size,r*cell_size), ((c+1)*cell_size,(r+1)*cell_size))		#
		pygame.draw.line(gameDisplay , black, ((c+1)*cell_size,r*cell_size), (c*cell_size,(r+1)*cell_size))		# Dead cats are drawn as X's
	for cat in alive_cats:
		r = cat.pos[0]
		c = cat.pos[1]
		pygame.draw.circle(gameDisplay , cat.colour, (int((c+0.5)*cell_size),int((r+0.5)*cell_size)),int(cell_size*(cat.age/16 + 1/4)))					# Live cats are coloured circles
		pygame.draw.circle(gameDisplay , black, (int((c+0.5)*cell_size),int((r+0.5)*cell_size)), int(cell_size*(cat.age/16 + 1/4)), int(cell_size/10))  # With a black outline
	for heart in hearts:
		gameDisplay.blit(heart_image,(heart[0],heart[1]))		# Draws a heart on screen if cats reproduce

# Function that displays the current time (in days and hours) on the screen	
def display_time(hour,day,hour_of_day,fontface,gameDisplay):
	line1 = "Day "+str(day)+", Hour "+str(hour_of_day)
	line1display = fontface.render(line1,True,white)
	line2 = "Total hours: "+str(hour)
	line2display = fontface.render(line2,True,white)
	gameDisplay.blit(line1display,(10,(num_rows+1)*cell_size))
	gameDisplay.blit(line2display,(10,(num_rows+2)*cell_size+5))	

# Function that calculates and returns various statistics for a list of cat objects
def get_stats(cats):
	agr = 0 							# Number of aggressive cats
	frnd = 0 							# Number of friendly cats
	meek = 0 							# Number of meek cats
	total_age = 0                   	# Total age of all cats
	for cat in cats:
		if cat.temper == "aggressive":
			agr+=1
		elif cat.temper == "friendly":
			frnd+=1
		elif cat.temper == "meek":
			meek+=1
		total_age += cat.age
	if len(cats)>0:
		avg_age = round(total_age/len(cats) , 2)	# Average age of cats	
	else:
		avg_age = 0	
	return agr,frnd,meek,avg_age

# Function to print statistics at the end of the simulation
def show_stats(init_cats,alive_cats,dead_cats,births):
	init_agr,init_frnd,init_meek,init_avg_age = get_stats(init_cats)
	curr_agr,curr_frnd,curr_meek,curr_avg_age = get_stats(alive_cats)
	total_food_eaten = 0
	total_water_drunk = 0
	for cat in alive_cats+dead_cats:
		total_food_eaten+=cat.total_food_eaten
		total_water_drunk+=cat.total_water_drunk
	avg_food_eaten = round(total_food_eaten/(len(alive_cats)+len(dead_cats)) , 2)
	avg_water_drunk = round(total_water_drunk/(len(alive_cats)+len(dead_cats)) , 2)

	stats = """\n\n#### STATISTICS ####\n\n
Initial population: """+str(init_pop)+"""
Initial number of aggressive cats: """+str(init_agr)+"""
Initial number of friendly cats: """+str(init_frnd)+"""
Initial number of meek cats: """+str(init_meek)+"""
Initial average age of cats: """+str(init_avg_age)+"""

Births: """+str(births)+"""
Deaths: """+str(len(dead_cats))+"""

Current population: """+str(len(alive_cats))+"""
Current number of aggressive cats: """+str(curr_agr)+"""
Current number of friendly cats: """+str(curr_frnd)+"""
Current number of meek cats: """+str(curr_meek)+"""
Current average age of cats: """+str(curr_avg_age)+"""

Total units of food eaten: """+str(total_food_eaten)+"""
Average units of food eaten by a single cat: """+str(avg_food_eaten)+"""
Total units of water drunk: """+str(total_water_drunk)+"""
Average units of water drunk by a single cat: """+str(avg_water_drunk)+"\n\n"
	print(stats)
	return stats

# Function that displays each cat's status 
def show_cats(alive_cats,dead_cats):
	for cat in alive_cats:
		print(cat.display_self())
	for cat in dead_cats:
		print(cat.display_self())

# Function to ask user for a choice of two inputs
def ask_choice(prompt,option1,option2,error_message):
	invalid = True
	while invalid:
		invalid = False
		ans = input(prompt).upper() 				
		if ans!=option1 and ans!=option2:
			print(error_message)
			invalid = True
	return ans

# Function to ask user for an integer input
def ask_number(prompt,error_message):
	invalid = True
	while invalid:
		invalid = False	
		try:	
			ans = int(input(prompt))	
		except ValueError:
			print(error_message)
			invalid = True
	return ans

# Main sequence of events; returns the number of births that occurred during the timestep
def main_loop(alive_cats,terrain_array,food_array,water_array,cat_scent_array,neighbourhood,hour_of_day):
	births = []

	# Cat to cat and food/water interaction rules
	for cat in alive_cats:
		cat.height = terrain_array[cat.pos[0],cat.pos[1]]
		cat.engaged = False
		cat.consuming = False
		cat.fighting = False
		cat.fleeing = False	
		cat.mating = False
		if cat.mating_cooldown>0:
			cat.mating_cooldown-=1 			# Decrementing the mating cooldown timer every timestep
		neighbours,neighbouring_food,neighbouring_water = check_surroundings(cat,cat.pos,alive_cats)
		if len(neighbours)>0:
			cat.interact(neighbours,terrain_array,food_array,water_array,neighbourhood,alive_cats)	
		if not (cat.fighting or cat.fleeing):
			if (not cat.sleeping) and (len(neighbouring_food)>0 or len(neighbouring_water)>0):		
				eat_or_drink(cat,neighbouring_food,neighbouring_water,food_array,water_array)

	# Reproduction rules		
	for cat in alive_cats:
		if (not cat.engaged) and (not cat.mating) and (not cat.sleeping):
			neighbours = check_surroundings(cat,cat.pos,alive_cats)[0]
			for neighbour in neighbours:
				if (cat.sex!=neighbour.sex) and (not neighbour.engaged) and (not neighbour.mating) and (not neighbour.sleeping):
					if (cat.hunger<75) and (cat.thirst<75) and (neighbour.hunger<75) and (neighbour.thirst<75):
						if (cat.mating_cooldown==0) and (neighbour.mating_cooldown==0):
							potential_spots = get_valid_moves(cat,terrain_array,food_array,water_array,cat_scent_array,neighbourhood,alive_cats)
							chosen_spot = random.choice(potential_spots)   							# Choosing a random valid cell for the baby to spawn in
							baby = reproduce(len(births)+1,cat,neighbour,chosen_spot)
							births.append(baby)

	# Sleeping rules						
	for cat in alive_cats:
		initial_sleep_chance = cat.sleep_chance
		if hour_of_day >= 21 or hour_of_day < 5:					# More likely to sleep at night
			cat.sleep_chance*=5
		multiplier = -0.02*cat.health + 3 							# The lower the cat's health, the more likely it is to go to sleep
		cat.sleep_chance*=multiplier
		if random.random()<cat.sleep_chance and (cat.hunger < 75 and cat.thirst < 75) and (not cat.engaged):		# Cats only sleep if they are not hungry or thirsty
			cat.sleeping = True
		cat.sleep_chance = initial_sleep_chance

	# Movement rules	
	for cat in alive_cats:
		cat.sleep()
		# print(cat.hunger,cat.thirst,cat.health)
		if (not cat.engaged) and (not cat.sleeping):
			valid_moves = get_valid_moves(cat,terrain_array,food_array,water_array,cat_scent_array,neighbourhood,alive_cats)
			choices = [v for v in valid_moves]			# List of move choices the cat will randomly choose from 						
			if cat.hunger<eating_threshold and cat.thirst<drinking_threshold and cat.mating_cooldown==0:
				# Making the cat follow the scent of the opposite sex:
				neighbour_scent_value = 0
				for move in valid_moves:
					scent = cat_scent_array[move[0],move[1]]
					# List of move choices becomes the cells with highest scent of the opposite sex:		
					if scent[1]!=None and scent[1]!=cat.sex:	
						if scent[2]>neighbour_scent_value:
							neighbour_scent_value = scent[2]
							choices = [move]
						elif scent[2]==neighbour_scent_value:
							choices.append(move)
				pass
			else:
				# Making the cat follow food and water scents:
				food_scents = []							# List of cells with food scents in the neighbourhood
				water_scents = []							# List of cells with water scents in the neighbourhood
				temp_choices = []
				for move in valid_moves:
					if food_scent_array[move[0],move[1]]>0:
						food_scents.append(food_scent_array[move[0],move[1]])
					if water_scent_array[move[0],move[1]]>0:
						water_scents.append(water_scent_array[move[0],move[1]])
				if (cat.hunger>eating_threshold) and (cat.hunger>cat.thirst or len(water_scents)==0):
					for move in valid_moves:
						probability = food_scent_array[move[0],move[1]]
						if random.random()<=probability:
							temp_choices.append(move)
				elif (cat.thirst>drinking_threshold) and (cat.thirst>=cat.hunger or len(food_scents)==0):
					for move in valid_moves:
						probability = water_scent_array[move[0],move[1]]
						if random.random()<=probability:
							temp_choices.append(move)
				if len(temp_choices)>0:						# If there are no food or water scents in the neighbourhood, move choices list is unchanged
					choices = [c for c in temp_choices]
			cat.pos = random.choice(choices)
	
	alive_cats.extend(births)				# Adding new births to the cat population		

	for cat in alive_cats:
		cat.set_colour()					# Setting the colour for each cat
		cat.hunger_and_thirst()				# Updating each cat's hunger and thirst levels
	
	return len(births)						# Returning number of births that occurred 

if __name__ == "__main__":

	try:
		terrain_array = read_terrain(sys.argv[1])				# Command line argument for terrain file
		food_array, water_array = read_landmarks(sys.argv[2])	# Command line argument for landmark file
	except IndexError:
		print("\nError: Please enter valid terrain csv and landmark csv as command line arguments.")
	else:
		try:												
			mating_cooldown_time = int(sys.argv[3])			# User can provide a different mating cooldown time as a cmd line argument (optional)
		except:
			pass
		try:							
			sleep_hours = int(sys.argv[4])					# User can provide a different sleep length as a cmd line argument (optional)
		except:
			pass
		food_scent_array = np.zeros((num_rows+2,num_cols+2))
		water_scent_array = np.zeros((num_rows+2,num_cols+2))
		cat_scent_array = np.empty((num_rows+2,num_cols+2),dtype=object)		

		neighbourhood = ask_choice("\nEnter the desired neighbourhood (M or V):\n","M","V","\nError: Not a valid neighbourhood.") 											# Moore or Von Neumann
		max_hours = ask_number("\nHow many hours should be simulated? (enter 0 for indefinite):\n","\nError: Not a valid simulation length. Please provide an integer.") 	# Number of iterations the sim should run for
		init_pop = ask_number("\nEnter the initial number of cats:\n","\nError: Not a valid simulation length. Please provide an integer.") 								# Initial population of cats	
		
		alive_cats = create_cats(init_pop)					# Creating initial list of cat objects
		init_cats = alive_cats.copy()						# Storing initial list of cat objects				
		dead_cats = []										# List of cats that have died
		births = 0 											# Total number of births
		for r in range(num_rows+2):
			for c in range(num_cols+2):
				cat_scent_array[r,c] = [None,None,0]
				food_scent_array[r,c] = food_array[r,c]
				water_scent_array[r,c] = water_array[r,c]
		event_log = ["### LOG ###\n\n"]						# Log of events that occur during the simulation

		# Initializing pygame
		pygame.init()
		gameDisplay = pygame.display.set_mode((display_width,display_height))
		fontface = pygame.ftfont.SysFont('Courier New',15,bold=True)
		pygame.display.set_caption("Cats")
		clock = pygame.time.Clock()

		crashed = False		
		hour,day,hour_of_day = -1,0,0
		show_scents = False
		show_food_scent = False
		show_water_scent = False
		heart_image = pygame.image.load("heart.png")

		print("\n\n\t\t\tSIMULATION START\n")
		print("\n\n#### LOG ####\n\n")
		while not crashed:
			hour,day,hour_of_day = increment_time(hour,day,hour_of_day)
			
			hearts = []

			for event in pygame.event.get():

				if (event.type == pygame.QUIT):								# Quits simulation if user closes pygame window 
					crashed = True	
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_s:								# User can toggle the visualisation of cat scents with "s" key
						show_scents = not show_scents	
					if event.key == pygame.K_f:								# User can toggle the visualisation of food scents with "f" key
						show_food_scent = not show_food_scent
					if event.key == pygame.K_w:								# User can toggle the visualisation of water scents with "w" key
						show_water_scent = not show_water_scent

			if (max_hours>0) and (hour==max_hours):							# Quits the simulation after the specified number of iterations
				crashed = True

			cat_scent_array = update_cat_scents(alive_cats,cat_scent_array)
			births += main_loop(alive_cats,terrain_array,food_array,water_array,cat_scent_array,neighbourhood,hour_of_day) 		
			food_scent_array = np.where(food_array>0,food_array,diffuse(food_scent_array,neighbourhood))
			water_scent_array = np.where(water_array>0,water_array,diffuse(water_scent_array,neighbourhood))
			alive_cats, dead_cats = kill_cats(alive_cats,dead_cats)
			clock.tick(framerate)																						
			draw_screen(terrain_array,food_array, water_array, alive_cats, dead_cats, show_scents, heart_image, hearts)	    
			display_time(hour,day,hour_of_day,fontface,gameDisplay)
			pygame.display.update()											# Draws the new frame

		print("\n\n\n\t\t\tSIMULATION END\n\n\n")
		# show_cats(alive_cats,dead_cats)
		stats = show_stats(init_cats,alive_cats,dead_cats,births)			# Prints statistics after the simulation is over

		show_scents = False
		show_food_scent = False
		show_water_scent = False
		draw_screen(terrain_array,food_array, water_array, alive_cats, dead_cats, show_scents, heart_image, hearts)
		display_time(hour,day,hour_of_day,fontface,gameDisplay)

		now = str(datetime.datetime.now())[:19]
		now = '_'.join(now.split(' '))
		now = '.'.join(now.split(':'))
		new_dir = "Simulation_"+now 			# Creating a unique name for the new directory
		
		save_grid = ask_choice("\nSave current grid state? (Y/N): ","Y","N","\nError: Please enter Y or N.")	# User can choose to save grid state as an image and arrays
		if save_grid == "Y":
			if new_dir not in os.listdir():
				os.mkdir(new_dir)				# Creating new directory for data to be saved in	
			os.chdir(new_dir)

			pygame.image.save(gameDisplay,"simulation.png")							# Saving image of final frame of simulation
			terrain_array_save = terrain_array[1:num_rows+1,1:num_cols+1]			# Terrain array used in the simulation
			landmark_array_save = np.empty((num_rows,num_cols),dtype=object)		# Layout of food and water in the final frame of simulation
			cats_array_save = np.empty((num_rows,num_cols),dtype=object)			# Positions of cats in final frame of simulation
			for r in range(num_rows):
				for c in range(num_cols):
					cats_array_save[r,c] = ""
					if water_array[r+1,c+1] > 0:
						landmark_array_save[r,c] = "W "+str(water_array[r+1,c+1])
					elif food_array[r+1,c+1] > 0:
						landmark_array_save[r,c] = "F "+str(food_array[r+1,c+1])
					else:
						landmark_array_save[r,c] = ""

			for cat in alive_cats+dead_cats:
				r,c = cat.pos[0],cat.pos[1]
				if cat.alive:
					cats_array_save[r-1,c-1]="A"
				else:
					cats_array_save[r-1,c-1]="D"

			# Converting the arrays to csv files and saving them
			np.savetxt("terrain_used.csv", terrain_array_save, delimiter=",", fmt='%s')
			np.savetxt("final_landmarks.csv", landmark_array_save, delimiter=",", fmt='%s')
			np.savetxt("final_cats.csv", cats_array_save, delimiter=",", fmt='%s')
			
			os.chdir(main_dir)

		pygame.quit()		  		# Exit simulation

		save_log = ask_choice("\nSave event log? (Y/N): ","Y","N","\nError: Please enter Y or N.")	# User can choose to save event log to an output file
		if save_log == "Y":	
			if new_dir not in os.listdir():
				os.mkdir(new_dir)
			os.chdir(new_dir)

			with open("log.txt","w") as out:
				for ev in event_log:
					out.write(ev)
				out.write(stats)

			os.chdir(main_dir)
	quit()