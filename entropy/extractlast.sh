#!/bin/sh
#this bash script shouldn't exist: I used that to avoid spend time knowing how to read csv in python (a 20 min economy) 
#and is titlte is misleading:it's not "extractlast"but extract "non 0". It's last ONLY if serializatio time = 2


awk 'BEGIN{FS=";"}{if(NR > 1 && $1 > 0)print $13 }' $1
