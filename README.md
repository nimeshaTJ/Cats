## 
## COMP1005 Assignment - Game of Cats
## Semester 2, 2021 v1.0
##
## Student Name: Nimesha Jayatunge
## Student ID: 20464631
##

## Description

A simulation of cats in an environment with adjustible parameters. 

## Setup

Before running the program, install the required external packages using the following commands:

pip install pygame==2.0.1

pip install numpy==1.16.6


## Usage

MAIN SIMULATION

1. Run the program using the following command:

python3 Cats.py terrain.csv landmarks.csv <mating_cooldown_time> <sleep_hours>

<> - optional

2. Enter "M" or "V" for neighbourhood choice

3. Enter number of hours to simulate (1 hour = 1 timestep)

4. Enter initial number of cats

5. Interact with the simulation using the following keys:

‘s’ – toggles the visualisation of cat scents (blue for male and pink for female)
‘f’ – toggles  the visualisation of food scents
‘w’ – toggles  the visualisation of water scents

6. Enter "Y" or "N" to save final grid state or not

7. Enter "Y" or "N" to save event log or not


PARAMETER SWEEP

1. Run the program using the following command:

sh ParameterSweep.sh terrain.csv landmarks.csv <neighbourhood> <max_hours> <cat_number> <low_cooldown> <hi_cooldown> <step_cooldown> <low_sleep> <hi_sleep> <step_sleep>


 
## Contents  
 
├── Cats.py           -  Main source code

├── SweepBase.py      -  Base code for parameter sweep

├── ParameterSweep.sh -  Bash script for parameter sweep

├── terrain.csv       -  csv containing terrain height data for simulation

├── terrain2.csv      -  csv containing terrain height data for testing

├── landmarks.csv     -  csv containing food and water data for simulation

├── landmarks2.csv    -  csv containing food and water data for testing

├── landmarks3.csv    -  empty csv for testing

├── heart.png         -  Sprite of a cartoon heart, used in the simulation

├── README.txt        -  README file

└──_Tests	      -  Test outputs

## Dependencies 

pygame

os

numpy

random

csv

sys 
 
## Version information 
 
17/Sep/2021 - Can read terrain and landmark data from scv files, and draw them onto pygame display.

18/Sep/2021 - Landmarks can now have a quantity (x units of food/water).

18/Sep/2021 - Created Cat class, movement rules and Moore/von Neumann neighbour detection.

19/Sep/2021 - Cats have hunger and thirst, and can eat food and drink water. Cats can also detect whether other cats are nearby.

20/Sep/2021 - Implemented engagement rules for cats; restructured sections of code and improved movement system.

23/Sep/2021 - Added time of day and sleeping mechanic for cats.

25/Sep/2021 - Cats leave a scent when passing through a cell.

26/Sep/2021 - Added reproduction mechanic.

27/Sep/2021 - Cats search for food and water based on scent.

29/Sep/2021 - Added event log and simulation statistics.

30/Sep/2021 - Log, statistics and grid state can be saved to a new folder

10/Oct/2021 - Added parameter sweep functionality