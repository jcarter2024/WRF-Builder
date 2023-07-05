#!/bin/bash
#$-cwd

supported=("Morrison" "ISHMAEL" "P3")
read -p "Would you like me to perform some edits? " confirm
if [ $confirm == y ]; then
    read -p "What microphysics scheme? 
    Morrison
    ISHMAEL
    P3
    : " schemetype
    
    if [[ " ${supported[*]} " =~ " ${schemetype} " ]]; then
    # whatever you want to do when array contains value
    echo "Ok! I will perform the edits on $schemetype"
    else
    echo "Sorry, this programme does not support edits to this scheme at this time. The available options are:"
    printf '%s\n' "${supported[@]}"
    fi
fi

if [ $schemetype == "Morrison" ]; then 
echo "Opening Morrison_editor python file..."
python3 mp_scheme_scripts/Morrison_editor.py
fi 

echo "Complete"

