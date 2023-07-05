# WRF-Builder

This programme makes the WRF code and edits the microphysics scheme

Order:
env load ----> Loads the right environment files, builds libraries, builds WRF and WPS, compiles WRF and WPS. Right now this env_load_v2.sh and should be run in the cwd like so $: . env_load.sh

Editor -----> Allows the user to specify a microphysics scheme and opens the corresponding python file for this editing to take place. For example, the user specifies Morrison and the file Morrison_editor.py is opened like so $: python3 Morrison_editor.py
