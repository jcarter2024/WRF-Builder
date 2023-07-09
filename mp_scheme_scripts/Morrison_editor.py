from useful_funcs import *


# !!!!!!!!!!!!!!!!!!! ** USER VARIABLES ** !!!!!!!!!!!!!!!!!!!!!!!#
FILEPATH = 'Build_WRF/WRF/phys/module_mp_morr_two_moment-Copy1.F' # <<<------- Change before running 
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#


#----------------------------------------------------> C O D E <------------------------------------------------------------------
 
    
# STEP 1 = Backup the old file
#--------------------------------

print()
FILEPATHNEW = increase_fn(FILEPATH)
shutil.copy(FILEPATH, FILEPATHNEW)

print('Ive made a backup before we begin', FILEPATH, '---->', FILEPATHNEW)
print("I will work on the old file") 



# STEP 2 = get the start and end points of the interior subroutine
 #----------------------------------------------------------------
print()
ROUTINE_NAME   = 'SUBROUTINE MORR_TWO_MOMENT_MICRO'
code_qualities = {}

print("checking for the current line numbers of the interior subroutine", ROUTINE_NAME)
code_qualities['MORR_TWO_MOMENT_MICRO_start'], code_qualities['MORR_TWO_MOMENT_MICRO_end'] = subroutine_finder(FILEPATH, 'SUBROUTINE MORR_TWO_MOMENT_MICRO')


# STEP 3 = get the line number of the final call to our variable, check its within the interior subroutine
 #----------------------------------------------------------------
var_oi = sys.argv[1]
print()
print("Now locating your var", var_oi)
#first argument passed from shell

#get final line number of your variable 
code_qualities['MYVAR_FINAL_LN'] = extract(FILEPATH, var_oi)
print('last instance of your var is on line', code_qualities['MYVAR_FINAL_LN'])

if code_qualities['MORR_TWO_MOMENT_MICRO_start'] < code_qualities['MYVAR_FINAL_LN'] < code_qualities['MORR_TWO_MOMENT_MICRO_end']:
    print("This is within the interior subroutine")
else:
    print("this variable is outside the interior subroutine")
    sys.exit("Check variable scope")
   

 # STEP 4 = find subroutine argument start/end and check that the variable is in the subroutine arguments list
#----------------------------------------------------------------
print()
print("Checking if the variable is already written into the subroutine's argument list...")
code_qualities['MORR_TWO_MOMENT_MICRO_argstart'], code_qualities['MORR_TWO_MOMENT_MICRO_argsend'] = bracket_find(FILEPATH, code_qualities['MORR_TWO_MOMENT_MICRO_start'])

varpresent  = 'no'

with open(FILEPATH, 'r') as fn:
    filelines = fn.readlines()[code_qualities['MORR_TWO_MOMENT_MICRO_argstart']:code_qualities['MORR_TWO_MOMENT_MICRO_argsend']+1]
    for line in filelines:
        if var_oi.upper() in line or var_oi.lower() in line:
            varpresent = 'yes'
        
    
    if varpresent == 'yes':
        print('var is present, skipping this part...')
        print('NOTE!! This code currently assumes that the subroutine defntn and call have matching argument lists!')
    else:
        print('var not present in argument list, I\'ll add it to the end')
        line_write(FILEPATH, ','+var_oi, code_qualities['MORR_TWO_MOMENT_MICRO_argsend'])
        
        print("I'll also add a corresponding variable to the argument list of this subroutine in the CALL")
        #get the location of the call to micro
        code_qualities['MORR_TWO_MOMENT_MICRO_call'] = subroutine_finder(FILEPATH, 'call MORR_TWO_MOMENT_MICRO')[0]
        #find the bracket loc
        code_qualities['MORR_TWO_MOMENT_MICRO_callargstart'], code_qualities['MORR_TWO_MOMENT_MICRO_callargsend'] = bracket_find(FILEPATH, code_qualities['MORR_TWO_MOMENT_MICRO_call'])
        line_write(FILEPATH, ','+var_oi+'&', code_qualities['MORR_TWO_MOMENT_MICRO_callargsend'])


 # STEP 5 = create a 3D variable in the outer routine
#----------------------------------------------------------------

#first find the location of the outer subroutine 
ROUTINE_NAME   = 'SUBROUTINE MP_MORR_TWO_MOMENT'
code_qualities = {}

print()
print("checking for the current line numbers of the outer subroutine", ROUTINE_NAME)
code_qualities['MP_MORR_TWO_MOMENT_start'], code_qualities['MP_MORR_TWO_MOMENT_end'] = subroutine_finder(FILEPATH, ROUTINE_NAME)

#check if we have put in a real segment previously 
code_qualities['our_real_list_end'] = 0

with open(FILEPATH, 'r') as fn:
    for (i, line) in enumerate(fn):
        if '! ==== MP EDITOR VARIABLES END ===== !' in line: #we've amended previously, find latest real 
            print("Detected previous use, appending this variable to end of list")
            code_qualities['our_real_list_end'] = i-1
            break 
            
if code_qualities['our_real_list_end'] == 0: #not edited before, find the last position of REALS 
    print("This is the first time using the MP editor, I'll add in a commented line that will highlight your variables")
    print("It'll look like: ! ==== MP EDITOR VARIABLES END ===== !") 
    real_ln = real_search(FILEPATH, code_qualities['MP_MORR_TWO_MOMENT_start'], code_qualities['MP_MORR_TWO_MOMENT_end'])
    line_write(FILEPATH, '! ==== MP EDITOR VARIABLES END ===== !', real_ln+1)
    code_qualities['our_real_list_end'] = real_ln
            
## code_qualities['our_real_list_end'] tells us where we should edit 
print()
print('\n Writing 3D variable definition')
line_write(FILEPATH, '   REAL, DIMENSION(ims:ime, kms:kme, jms:jme), INTENT(INOUT):: '+var_oi, code_qualities['our_real_list_end']+1)

 # STEP 6 = add to routine args list 
#----------------------------------------------------------------

#get the location of start and end brackets for mp_morr_two_moment routine 
code_qualities['MP_MORR_TWO_MOMENT_argstart'], code_qualities['MP_MORR_TWO_MOMENT_argsend'] = bracket_find(FILEPATH, code_qualities['MP_MORR_TWO_MOMENT_start'])