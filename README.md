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


 
## Contents  
 
├── Cats.py

├── terrain.csv

├── landmarks.csv

├── heart.png

├── README.txt

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