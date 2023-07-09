#!/bin/bash
#$-cwd

supported=("Morrison" "ISHMAEL" "P3")
echo ""
read -p "Would you like me to perform some edits? [y/n]: " confirm
if [ $confirm == y ]; then

    #Check Variable is present
    var_oi=$1
    if [[ -n "$var_oi" ]]; then
        echo ""
        echo "--------> Variable to be extracted is  ===> $var_oi"
        
        read -p "Which microphysics scheme? [ Morrison / ISHMAEL / P3 ]: " schemetype  
        
        #check scheme is supported
        if [[ " ${supported[*]} " =~ " ${schemetype} " ]]; then
            echo ""
            echo "--------> Ok! I will perform the edits on $schemetype"
    

            if [ $schemetype == "Morrison" ]; then 
            
                read -p "What are the SI units of this variable? " units
                read -p "What would you like the NETCDF keyword to be for this variable? " NETCDFNAME
                read -p "Provide a short description of this variable: " descriptor
                echo ""
                echo "--------> Opening Morrison_editor python file..."
                python3 mp_scheme_scripts/Morrison_editor.py $var_oi $units $NETCDFNAME $descriptor
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

