# WRF-Builder

This programme can retrieve and compile WRF, and is capable of "extracting" microphysical variables for supported schemes. Extraction refers to taking a (one-dimensional) local variable, collecting it in a 4d array, and exporting this to the registry (history file). 

Currently supported schemes are:
    . Morrison 2-Moment (Opt 10)
   
Upcoming schemes are:
    . ISHMAEL (opt 55)
    . P3
    

QUICK START:
    . Clone this repository using git-tools on the command line 
    . execute ". mp_build.sh" and follow the command line directions, which require user input
    . If you'd like to skip to the mp extraction simply execute ". editor.sh" and follow the command line directions
        
        
Capabilities:
        mp_build.sh can:
            . Create a logical filestructure for a WRF build
            . retrieve the latest WPS and WRF from github 
            . build the nescessary libraries from source
            . compile WPS
            . compile WRF
            .calls "editor.sh"
        editor.sh can:
            . extract a microphysical variable from scheme to registry (including all intermediary files)
            . provides opportunity for user to rename variable, add description and units for NETCDF attributes
            . create backups for all modified files automatically
        restore.sh can:
            . restore edited files from auto-backups* or from source*
            
Developed on Mac-OS, compatible with UNIX based systems*
     
     
    







Order:
env load ----> Loads the right environment files, builds libraries, builds WRF and WPS, compiles WRF and WPS. Right now this env_load_v2.sh and should be run in the cwd like so $: . env_load.sh

Editor -----> Allows the user to specify a microphysics scheme and opens the corresponding python file for this editing to take place. For example, the user specifies Morrison and the file Morrison_editor.py is opened like so $: python3 Morrison_editor.py
