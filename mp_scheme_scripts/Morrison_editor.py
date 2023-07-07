import sys
import shutil

### FUNCTIONS =============================================================
def subroutine_finder(filepath, ROUTINE_NAME):
    """Locate line numbers for subroutines"""
    with open(filepath, 'r') as fn:
        for (i, line) in enumerate(fn):
            if ROUTINE_NAME.upper() in line or ROUTINE_NAME.lower() in line:
                tmp = line.split()
                if 'END' in tmp:
                    print('end', i)
                    end = i
                else:
                    print('start', i)
                    start = i

    return start, end


def deconstruct_path(filepath):
    filename_ext = filepath.split('/')[-1]
    path         = filepath[:-len(filename_ext)]
    filenameonly = filename_ext.split('.')[0]
    return path, filename_ext, filenameonly



def increase_fn(filepath):
    """Strips the filename and adds one to the end"""
    
    #first deconstruct the old path 
    path, filename_ext, filenameonly = deconstruct_path(filepath)
    
    letters = filenameonly.rstrip('0123456789')
    numbs   = filenameonly[len(letters):]
    
    #incase there is no number
    if len(numbs) == 0:
        numbs=0

    numbs_new       = str(int(numbs)+1)
    filenameonlynew = letters+numbs_new
    
    filepathnew     = path+filenameonlynew+'.'+filename_ext.split('.')[1]
    
    return filepathnew
### =============================================================



#USER VARIABLES
FILEPATH = 'Build_WRF/WRF/phys/module_mp_morr_two_moment-Copy1.F'


######CODE
FILEPATHNEW = increase_fn(FILEPATH)
shutil.copy(FILEPATH, FILEPATHNEW)

print('Ive made a backup before we begin', FILEPATH, '---->', FILEPATHNEW)
print("I will work on the old file") 




# variable_to_extract = sys.argv[1] #first argument passed from shell


#get the start and end points of the interior subroutine
ROUTINE_NAME = 'SUBROUTINE MP_MORR_TWO_MOMENT'
code_qualities = {}

code_qualities['MP_MORR_TWO_MOMENT_start'], code_qualities['MP_MORR_TWO_MOMENT_end'] = subroutine_finder(
    FILEPATH, 'SUBROUTINE MP_MORR_TWO_MOMENT')

