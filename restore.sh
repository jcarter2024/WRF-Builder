#use to undo changes for most recent run 


read -p "Are you sure you would like to restore? [y/n] " confirm
if [ $confirm == y ]; then
    read -p "restore from backup or from source? [b/s] " bs
    
    if [ $bs == b ]; then
        read -p "Which backup would you like to restore? [enter file suffix #] " number
        mv Build_WRF/WRF/phys/module_mp_morr_two_moment$number.F Build_WRF/WRF/phys/module_mp_morr_two_moment.F
        mv Build_WRF/WRF/phys/module_microphysics_driver$number.F Build_WRF/WRF/phys/module_microphysics_driver.F 
        mv Build_WRF/WRF/dyn_em/solve_em$number.F Build_WRF/WRF/dyn_em/solve_em.F
        mv Build_WRF/WRF/Registry/Registry$number.EM_COMMON Build_WRF/WRF/Registry/Registry.EM_COMMON
    
    elif [ $bs == s ]; then
        rm Build_WRF/WRF/phys/module_mp_morr_two_moment.F
        rm Build_WRF/WRF/phys/module_microphysics_driver.F
        rm Build_WRF/WRF/dyn_em/solve_em.F
        rm Build_WRF/WRF/Registry/Registry.EM_COMMON
        read -p "Which OS Windows or Mac? [w/m] " os
        
        if [ $os == w ]; then
            wget https://raw.githubusercontent.com/wrf-model/WRF/master/Registry/Registry.EM_COMMON Build_WRF/WRF/Registry/
            wget https://raw.githubusercontent.com/wrf-model/WRF/master/dyn_em/solve_em.F Build_WRF/WRF/dyn_em/
            wget https://raw.githubusercontent.com/wrf-model/WRF/master/phys/module_mp_morr_two_moment.F Build_WRF/WRF/phys/
            wget https://raw.githubusercontent.com/wrf-model/WRF/master/phys/module_microphysics_driver.F
            Build_WRF/WRF/phys/
        elif [ $os == m ]; then
            curl -O https://raw.githubusercontent.com/wrf-model/WRF/master/Registry/Registry.EM_COMMON 
            curl -O https://raw.githubusercontent.com/wrf-model/WRF/master/dyn_em/solve_em.F 
            curl -O https://raw.githubusercontent.com/wrf-model/WRF/master/phys/module_mp_morr_two_moment.F 
            curl -O https://raw.githubusercontent.com/wrf-model/WRF/master/phys/module_microphysics_driver.F
            
            mv Registry.EM_COMMON Build_WRF/WRF/Registry/Registry.EM_COMMON
            mv solve_em.F Build_WRF/WRF/dyn_em/solve_em.F
            mv module_mp_morr_two_moment.F Build_WRF/WRF/phys/module_mp_morr_two_moment.F
            mv module_microphysics_driver.F Build_WRF/WRF/phys/module_microphysics_driver.F
        else
            echo "must choose os"
        fi
    else
        echo "error, must be backup or source"
    fi
else
    echo "No edits made"
fi 
echo "Complete"
