#!/bin/bash 

terrain=$1
landmarks=$2
neighbourhood=$3 
max_hours=$4 
init_pop=$5 
low_cooldown=$6
hi_cooldown=$7
step_cooldown=$8
low_sleep=${9}
hi_sleep=${10} 
step_sleep=${11} 

new_dir=Sweep`date "+%Y-%m-%d_%H:%M:%S"` 
mkdir $new_dir
cp SweepBase.py $new_dir 
cp $terrain $new_dir
cp $landmarks $new_dir
cp heart.png $new_dir
cd $new_dir 

message="Terrain file: $terrain\n\
Landmarks file: $landmarks\n\
Neighbourhood: $neighbourhood\n\
Simulation length (hours): $max_hours\n\
Number of cats: $init_pop\n\
Mating cooldown time: $low_cooldown $hi_cooldown $step_cooldown\n\
Sleep hours: $low_sleep $hi_sleep $step_sleep"

echo "\n$message"

echo "$message" > Parameters.txt 

for m in `seq $low_cooldown $step_cooldown $hi_cooldown`;
do
	for s in `seq $low_sleep $step_sleep $hi_sleep`; 
	do 
		echo "\n\nSimulating: Mating cooldown time $m, sleep hours $s\n" 
		python3 SweepBase.py $terrain $landmarks $neighbourhood $max_hours $init_pop $m $s 
	done 
done 

# This file was created using "dosage_sweep.sh" from Practical 8 as a reference
# Maxville, Valerie. 2021. “dosage_sweep.sh” Practical 8, COMP1005 Fundamentals of Programming, Semester 2, 2021