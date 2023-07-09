#use to undo changes for most recent run 
read -p "Are you sure you would like to restore the most recent backup? [y/n] " confirm
if [ $confirm == y ]; then
    mv Build_WRF/WRF/phys/module_mp_morr_two_moment1.F Build_WRF/WRF/phys/module_mp_morr_two_moment.F
    mv Build_WRF/WRF/phys/module_microphysics_driver1.F Build_WRF/WRF/phys/module_microphysics_driver.F 
    mv Build_WRF/WRF/dyn_em/solve_em1.F Build_WRF/WRF/dyn_em/solve_em.F
    mv Build_WRF/WRF/Registry/Registry1.EM_COMMON Build_WRF/WRF/Registry/Registry.EM_COMMON
else
    echo "No edits made"
fi 
echo "Complete"
