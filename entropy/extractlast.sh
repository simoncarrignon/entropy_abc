#!/bin/sh
#this bash script shouldn't exist: I used that to avoid spend time knowing how to read csv in python (a 20 min economy) 


awk 'BEGIN{FS=";"}{if(NR > 1 && $1 > 0)print $10 }' $1
