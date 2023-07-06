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
### =============================================================



#USER VARIABLES
FILEPATH = '../Build_WRF/WRF/phys/module_mp_morr_two_moment-Copy1.F'


######CODE

#deconstruct old filename and add to the suffix
filename     = FILEPATH.split('/')[-1]
filepath     = FILEPATH[:-len(filename)]
filenameonly = filename.split('.')[0]
letters      = filenameonly.rstrip('0123456789')
numbs        = filenameonly[len(head):]

#incase there is no number
if len(numbs) == 0:
    numbs=0
    
#add one to suffix
numbs_new = str(int(numbs)+1)

#reconstruct and copy old file to new filename
FILEPATHNEW = filepath+letters+numbs_new+filename[-2:]
shutil.copy(FILEPATH, FILEPATHNEW)

print('Ive made a backup before we begin', FILEPATH, '---->', FILEPATHNEW)
print("I will work on the old file", filenameonly) 





variable_to_extract = sys.argv[1] #first argument passed from shell


#get the start and end points of the interior subroutine
ROUTINE_NAME = 'SUBROUTINE MP_MORR_TWO_MOMENT'
code_qualities = {}

code_qualities['MP_MORR_TWO_MOMENT_start'], code_qualities['MP_MORR_TWO_MOMENT_end'] = subroutine_finder(
    '../Build_WRF/WRF/phys/module_mp_morr_two_moment-Copy1.F', 'SUBROUTINE MP_MORR_TWO_MOMENT')

