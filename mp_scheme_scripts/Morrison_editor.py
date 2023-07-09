from useful_funcs import *


# !!!!!!!!!!!!!!!!!!! ** USER VARIABLES ** !!!!!!!!!!!!!!!!!!!!!!!#
FILEPATH = 'Build_WRF/WRF/phys/module_mp_morr_two_moment.F' # <<<------- Change before running 
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#


#the records_dict holds dictionaries for each file that can be edited by this code. Any changes are stored here and output at 
# the end of the programme

records_dict = {'module mp_morr_two_moment.F':{}, 'module_microphysics_driver.F':{}, 'solve_em.F':{}, 'Registry.EM_COMMON':{}}

#----------------------------------------------------> C O D E <------------------------------------------------------------------
 
# STEP 1 = Backup the old file
#--------------------------------
big_bound("module mp_morr_two_moment.F")

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
print("Checking if the variable is already written into the interior subroutine's argument list...")
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
        line_write(FILEPATH, ','+var_oi+'&', code_qualities['MORR_TWO_MOMENT_MICRO_argsend'], records_dict['module mp_morr_two_moment.F'])
        
        print("I'll also add a corresponding variable to the argument list of this subroutine in the CALL")
        #get the location of the call to micro
        code_qualities['MORR_TWO_MOMENT_MICRO_call'] = subroutine_finder(FILEPATH, 'call MORR_TWO_MOMENT_MICRO')[0]
        #find the bracket loc
        code_qualities['MORR_TWO_MOMENT_MICRO_callargstart'], code_qualities['MORR_TWO_MOMENT_MICRO_callargsend'] = bracket_find(FILEPATH, code_qualities['MORR_TWO_MOMENT_MICRO_call'])
        line_write(FILEPATH, ','+var_oi+'&', code_qualities['MORR_TWO_MOMENT_MICRO_callargsend'],records_dict['module mp_morr_two_moment.F'])


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
    line_write(FILEPATH, '! ==== MP EDITOR VARIABLES END ===== !', real_ln+1, records_dict['module mp_morr_two_moment.F'])
    code_qualities['our_real_list_end'] = real_ln
            
## code_qualities['our_real_list_end'] tells us where we should edit 
print()

#first check that the variable doesn't already exist!

print('\n Writing 3D variable definition')
with open(FILEPATH, 'r') as fn:
    for line in fn:
        if 'REAL, DIMENSION(ims:ime, kms:kme, jms:jme), INTENT(INOUT):: '+var_oi in line:
            print("Variable definition already present, skipping")
            break
    
    else: 
        line_write(FILEPATH, '   REAL, DIMENSION(ims:ime, kms:kme, jms:jme), INTENT(INOUT):: '+var_oi, code_qualities['our_real_list_end']+1, records_dict['module mp_morr_two_moment.F'])

 # STEP 6 = add to routine args list 
#----------------------------------------------------------------

#get the location of start and end brackets for mp_morr_two_moment routine 
code_qualities['MP_MORR_TWO_MOMENT_argstart'], code_qualities['MP_MORR_TWO_MOMENT_argsend'] = bracket_find(FILEPATH, code_qualities['MP_MORR_TWO_MOMENT_start'])

print()
print('\n Writing 3D variable to argument list')
skipit = 'no'
with open(FILEPATH, 'r') as fn:
    for (i, line) in enumerate(fn):
        if  code_qualities['MP_MORR_TWO_MOMENT_argstart'] < i < code_qualities['MP_MORR_TWO_MOMENT_argsend']:
            if var_oi in line:
                print("Variable definition already present, skipping")
                skipit = 'yes'
                break

if skipit == 'no':
    line_write(FILEPATH, ','+var_oi+'&', code_qualities['MP_MORR_TWO_MOMENT_argsend'], records_dict['module mp_morr_two_moment.F'])


      
# STEP 7 = add to args list in microphysics driver
#----------------------------------------------------------------   
big_bound("module_microphysics_driver.F")

#changing to new file 
FILEPATH = 'Build_WRF/WRF/phys/module_microphysics_driver.F'
    
print()
print("Now editing microphysics driver")
FILEPATHNEW = increase_fn(FILEPATH)
shutil.copy(FILEPATH, FILEPATHNEW)

print('Ive made a backup before we begin', FILEPATH, '---->', FILEPATHNEW)
print("I will work on the old file") 
    
#locate the calling subroutine     
ROUTINE_NAME   = 'SUBROUTINE MORR_TWO_MOMENT_MICRO'
code_qualities = {}

#do a quick check to make sure that our microphysics scheme is imported 
proceed = 'no'
with open(FILEPATH, 'r') as fn:
    for line in fn:
        if 'CASE (MORR_TWO_MOMENT)' in line:
            print('Microphysics scheme is supported by driver')
            proceed = 'yes'
    
if proceed == 'yes':
    
    #get location of microphysics driver subroutine
    print("checking for the current line numbers of the interior subroutine", ROUTINE_NAME)
    code_qualities['microphysics_driver_start'], code_qualities['microphysics_driver_end'] = (
    subroutine_finder(FILEPATH, 'SUBROUTINE microphysics_driver'))

    #and get the arguments location 
    code_qualities['microphysics_driver_argstart'], code_qualities['microphysics_driver_argsend'] = (
    bracket_find(FILEPATH, code_qualities['microphysics_driver_start']))
    
    #if variable not already in there, add it 
    #add our variable to the end of the module argument list 
    print()
    print('\n Writing 3D variable to argument list of mirophysics driver')
    skipit = 'no'
    with open(FILEPATH, 'r') as fn:
        for (i, line) in enumerate(fn):
            if  code_qualities['microphysics_driver_argstart'] < i < code_qualities['microphysics_driver_argsend']:
                if var_oi in line:
                    print("Variable definition already present, skipping")
                    skipit = 'yes'
                    break

    if skipit == 'no':
        line_write(FILEPATH, ','+var_oi+'&', code_qualities['microphysics_driver_argsend'],
                   records_dict['module_microphysics_driver.F'])
    
    
    #find the CALL mp_morr_two_moment brackets
    code_qualities['mp_morr_two_moment_call'] = subroutine_finder(FILEPATH, 'CALL mp_morr_two_moment(')[0]
    
    code_qualities['mp_morr_two_moment_argstart'], code_qualities['mp_morr_two_moment_argsend'] = (
    bracket_find(FILEPATH, code_qualities['mp_morr_two_moment_call']))
    
    #add our variable to the end of the arg list if it doesn't already exist 
    #add our variable to the end of the module argument list 
    print()
    print('\n Writing variable to argument list of morrison call')
    skipit = 'no'
    with open(FILEPATH, 'r') as fn:
        for (i, line) in enumerate(fn):
            if  code_qualities['mp_morr_two_moment_argstart'] < i < code_qualities['mp_morr_two_moment_argsend']:
                if var_oi in line:
                    print("Variable definition already present, skipping")
                    skipit = 'yes'
                    break

    if skipit == 'no':
        line_write(FILEPATH, ','+var_oi+'='+var_oi+'&', code_qualities['mp_morr_two_moment_argsend'],
               records_dict['module_microphysics_driver.F'])
    
     
    
# STEP 8 = add to args list in solve_em
#----------------------------------------------------------------   
big_bound('solve_em.F')

#changing to new file 
FILEPATH = 'Build_WRF/WRF/dyn_em/solve_em.F'
    
print()
print("Now editing solve_em.F")
FILEPATHNEW = increase_fn(FILEPATH)
shutil.copy(FILEPATH, FILEPATHNEW)

print('Ive made a backup before we begin', FILEPATH, '---->', FILEPATHNEW)
print("I will work on the old file") 


#find where the microphysics driver is called
#locate the calling subroutine     
code_qualities = {}

#get location of microphysics driver subroutine
code_qualities['microphysics_driver_call'] = subroutine_finder(FILEPATH, 'CALL microphysics_driver(')[0]
    
code_qualities['microphysics_driver_argstart'], code_qualities['microphysics_driver_argsend'] = (
bracket_find(FILEPATH, code_qualities['microphysics_driver_call']))
    
#add our variable to the end of the arg list if it doesn't already exist 
print()
print('\n Writing variable to argument list of microphysics driver call')
skipit = 'no'
with open(FILEPATH, 'r') as fn:
    for (i, line) in enumerate(fn):
        if  code_qualities['microphysics_driver_argstart'] < i < code_qualities['microphysics_driver_argsend']:
            if var_oi in line:
                print("Variable definition already present, skipping")
                skipit = 'yes'
                break

if skipit == 'no':
    line_write(FILEPATH, ','+var_oi+'=grid%'+var_oi+'&', code_qualities['microphysics_driver_argsend'],
           records_dict['solve_em.F'])
    #YES I'm aware that this bisects some arguments, ultimately the code works and isn't that the aim? ;)

    
# STEP 9 = Amend registry to include new var
#----------------------------------------------------------------   

big_bound('Registry.EM_COMMON')

#changing to new file 
FILEPATH = 'Build_WRF/WRF/Registry/Registry.EM_COMMON'
    
print()
print("Now editing the registry (Registry.EM_COMMON)")
FILEPATHNEW = increase_fn(FILEPATH)
shutil.copy(FILEPATH, FILEPATHNEW)

print('Ive made a backup before we begin', FILEPATH, '---->', FILEPATHNEW)
print("I will work on the old file") 
print()


# add in an appropriate place, is there a morrison vars section
units      =  "\"" + sys.argv[2] + "\""
NETCDFNAME =  "\"" + sys.argv[3] + "\""
descriptor =  "\"" + sys.argv[4] + "\""

#do not amend
registry_string = ('state'+'    '+'real'+'   '+var_oi+'     '+'ikj'+'    '+'misc'+'        '+'1'+
                   '         '+'-'+'      '+'h'+'       '+NETCDFNAME+'    '+descriptor+'        '+units)

#quick check that var isn't already in registry 

hasbeenedited = 'no'
with open(FILEPATH, 'r') as fn:
    retrieved = fn.readlines()
    
matching_already = [s for s in retrieved if var_oi in s]
if len(matching_already) > 0:
    print("!!!!!!! WARNING!!!!!!!   ::    This var might already exist in the registry, check line", retrieved.index(matching_already[0]))
    print("continue? [y/n]: ")
    x = input()
    if x == 'y':
        pass
    else:
        print("Exiting")
        sys.exit()
    
if any('# MY MP EDITOR VARIABLES' in s for s in retrieved):
            hasbeenedited = 'yes'

#simple case, add below this line 
if hasbeenedited == 'yes':  
    matching = [s for s in retrieved if '# MY MP EDITOR VARIABLES' in s]
    linenum = retrieved.index(matching[0])
    
    line_write(FILEPATH, registry_string, linenum, records_dict['Registry.EM_COMMON'])
    
    
#not been edited before, so add in a line 
else:
    #get the linenumber for scalars
    matching = [s for s in retrieved if '# Other Scalars' in s]
    linenum = retrieved.index(matching[0])
    
    #write in our edit line above this ]
    line_write(FILEPATH, '\n# MY MP EDITOR VARIABLES', linenum-1, records_dict['Registry.EM_COMMON'])
    line_write(FILEPATH, registry_string, linenum, records_dict['Registry.EM_COMMON'])
    
    
#add to the mp scheme vars list - search for line of package   morr_two_moment
with open(FILEPATH, 'r') as fn:
    for (i, line) in enumerate(fn):
        if 'package   morr_two_moment mp_physics==10' in line :
            if var_oi in line:
                print('This variable already exists in the registry')
            else:
                print('adding to package expectancies [scalar]')
                line_append(FILEPATH, ',pracg', i, records_dict['Registry.EM_COMMON'])

# STEP 10 = Recompile WRF
#----------------------------------------------------------------  



#FINAL STEP 
#----------------------------------------------------------------  
#print summary of all line changes 
summarise(records_dict)

    
 
    
    
    
    