import sys
import shutil
import re

# !!!!!!!!!!!!!!!!!!! ** USER VARIABLES ** !!!!!!!!!!!!!!!!!!!!!!!#
FILEPATH = 'Build_WRF/WRF/phys/module_mp_morr_two_moment-Copy1.F' # <<<------- Change before running 
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#


#-----------------------------------------------------> FUNCTIONS <---------------------------------------------------------------
def subroutine_finder(filepath, ROUTINE_NAME):
    """Locate line numbers for subroutines"""
    start = 0
    end   = 0
    with open(filepath, 'r') as fn:
        for (i, line) in enumerate(fn):
            if ROUTINE_NAME in line or ROUTINE_NAME.upper() in line or ROUTINE_NAME.lower() in line:
                if '!' not in line:
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

def extract(filename, phrase):
    """ This routine finds the last linenumber at which your variable is set equal to something.
        Currently checks that:
            . variable is not part of a comment
            . variable comes prior to equals sign
            . variable name is not part of a larger variable name on left-side (i.e. nprac vs prac)
            . flexible for space-split and lines without spaces split by operations (*/+-)
            
        Improvements:
            . Variable name could be part of a larger name on right side (i.e. pracn vs prac), don't believe this 
            exists in Morrison code
    """
   
    phrase_present = []
    with open(filename, 'r') as fn:
        for (i, line) in enumerate(fn):

            if phrase.upper() in line or phrase.lower() in line:
                tmp = line.split() #tmp is a list of words in line split by spaces

                #if tmp len is 1 then no spaces!
                if len(tmp)==1:
                    tmp = re.split('=|\*|\+|-', line)
                
                #search each element of tmp to see what is present
                pos_comment = 99
                pos_equals  = 99
                pos_phrase  = 100 #must be greater intitially to ensure compatibility with defs
                for (a, split) in enumerate(tmp):
                    
                    if phrase.upper() in split:
                        #check that the variable is not a variation with letters beforehand i.e. npracg vs pracg
                        qkchk = split.split(phrase.upper())
                        if qkchk[0] == '': #nothing before our variable
                            pos_phrase = a
           
                    elif phrase.lower() in split:
                        qkchk = split.split(phrase.lower())
                        if qkchk[0] == '': #nothing before our variable
                            pos_phrase = a
                        
                    #we want the first (earliest) instance of ! and equals
                    if '!' in split and a < pos_comment: 
                        pos_comment = a
                    if '=' in split and a < pos_equals:
                        pos_equals = a
             
                    
                if pos_comment < pos_phrase:
                    #is a comment IGNORE
#                     print("Ignoring due to comment::::", line)
                    pass
                elif pos_equals < pos_phrase:
#                     print("Ignoring due to =", line)
                    #is on RHS of equation IGNORE
                    pass
                elif pos_equals == 99:
#                     print("Ignoring due to lack of =", line)
                    pass
                elif pos_equals == pos_phrase:
                    print('no spaces in line', line)
                    #split according to all delimitters
                    tmp = re.split('=|\*|\+|-', this)
                    
        
                else:
                    print('good line at', i, 'equals',pos_equals, 'phrase is', pos_phrase, line)
                    phrase_present.append(i)
                    
    return phrase_present[-1]


def bracket_find(filepath, linestart):
    """Supply the subroutine start line, retrieve the line where the arguments (in brackets) start and stop"""
    bracket_count = 99
    with open(filepath, 'r') as fn:
        for (i, line) in enumerate(fn):
            if linestart <= i:
                if '(' in line and bracket_count == 99:
                    bracket_count = 1
                    argstart = i
                elif '(' in line:
                    bracket_count +=1

                if ')' in line:
                    bracket_count -= 1

                if bracket_count == 0:
                    argsend  = i
                    break
                
    return argstart, argsend


def line_write(filepath, string, linenumber):
    temp = open('temp', 'w')
    with open(filepath, 'r') as f:
        for i, line in enumerate(f):
            if i == linenumber: #REAL end +1
                temp.write(string+'\n')
            temp.write(line)
    temp.close()

    #move temp to file
    filepathout = increase_fn(filepath)
    print(filepath,'->',  filepathout)
    shutil.copy(filepath, filepathout)
    shutil.copy('temp', str(filepath))
    
    
def real_search(filepath, linestart, lineend):
    #get location of last Real call 
    with open(filepath, 'r') as fn:
        for (i, line) in enumerate(fn):
            if linestart <= i <= lineend:
                if 'REAL ' in line:
                    final_inst  = i
    return final_inst
    
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
        line_write(FILEPATH, ','+var_oi, code_qualities['MORR_TWO_MOMENT_MICRO_callargsend'])


 # STEP 5 = create a 3d? variable in the outer routine
#----------------------------------------------------------------
#first find the location of the outer subroutine 
ROUTINE_NAME   = 'SUBROUTINE MP_MORR_TWO_MOMENT'
code_qualities = {}

print("checking for the current line numbers of the interior subroutine", ROUTINE_NAME)
code_qualities['MP_MORR_TWO_MOMENT_start'], code_qualities['MP_MORR_TWO_MOMENT_end'] = subroutine_finder(FILEPATH, ROUTINE_NAME)

#check if we have put in a real segment previously 
code_qualities['our_real_list_end'] = 0

with open(FILEPATH, 'r') as fn:
    for (i, line) in enumerate(fn):
        if '! ==== MP EDITOR VARIABLES END ===== !' in line: #we've amended previously, find latest real 
            code_qualities['our_real_list_end'] = i-1
            break 
            
if code_qualities['our_real_list_end'] == 0: #not edited before, find the last position of REALS 
    real_ln = real_search(FILEPATH, code_qualities['MP_MORR_TWO_MOMENT_start'], code_qualities['MP_MORR_TWO_MOMENT_end'])
    line_write(FILEPATH, '! ==== MP EDITOR VARIABLES END ===== !', real_ln+1)
    code_qualities['our_real_list_end'] = real_ln
            
## code_qualities['our_real_list_end'] tells us where we should edit 
line_write(FILEPATH, '   REAL, DIMENSION(ims:ime, kms:kme, jms:jme), INTENT(INOUT):: '+var_oi, code_qualities['our_real_list_end']+1)
