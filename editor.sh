#!/bin/bash
#$-cwd

supported=("Morrison" "ISHMAEL" "P3")
read -p "Would you like me to perform some edits? " confirm
if [ $confirm == y ]; then

    #Check Variable is present
    var_oi=$1
    if [[ -n "$var_oi" ]]; then
        echo "Variable to be applied is $var_oi"
        
        read -p "Which microphysics scheme? 
        Morrison
        ISHMAEL
        P3
        : " schemetype  
        
        #check scheme is supported
        if [[ " ${supported[*]} " =~ " ${schemetype} " ]]; then
            echo "Ok! I will perform the edits on $schemetype"
    

            if [ $schemetype == "Morrison" ]; then 
                echo ""
                echo "Opening Morrison_editor python file..."
                python3 mp_scheme_scripts/Morrison_editor.py $var_oi
            else
                echo "Sorry, this programme does not support edits to this scheme at this time. The available options are:"
                printf '%s\n' "${supported[@]}"
            fi
     
        fi 
        
    else
        echo ""
        echo "--------------------------"
        echo "-->  Argument Error <----"
        echo "--------------------------"
        echo ""
        echo " Please ensure that a variable is specified"
    fi
    
    
else
    echo "Exiting..."
fi


echo ""
echo ""
echo "!!! PROGRAM END !!!"

