import os
import sys
import subprocess #note use for subprocesses over os module (depreciated)
# from python3_modfiles import module
import shutil
import re

##### OLD python build functions. These have since been replaced with BASH

def check_BUILDWRF():
    """This function checks if a build_wrf directory is present or builds one"""
    
    parent_level = os.listdir()
    
    if "Build_WRF" in parent_level:
        print("Build WRF present, checking for WRF and WPS")
    
    else:
        print("Build_WRF not present, shall I create a new WRF build from scratch?")
        answer = str(input())
        if answer == 'yes' or answer == 'y':
            subprocess.call('mkdir Build_WRF', shell=True)
            print("BUILT!")

        else:
            centre_message('Cannot proceed without Build_WRF directory')
            sys.exit()
            
            
def load_module(module_name):
    """ Load a module into the external shell i.e. load_module('tools/env/proxy')"""
    module('load', str(module_name))

            
def check_WRFWPS():
    """This function checks if WRF or WPS directory is present or builds one"""
  
    fraternal_dirs = os.listdir('Build_WRF')
    
    if 'WRF' in fraternal_dirs and 'WPS' in fraternal_dirs:
        print('WRF and WPS present')
            
    elif 'WRF' in fraternal_dirs and 'WPS' not in fraternal_dirs:
        print('WPS is missing, would you like me to build it from scratch?')
        answer = input()
                                
        if answer == 'yes' or answer == 'y':
            if confirm() == 'y':
                subprocess.call('mkdir Build_WRF/WPS', shell=True)
                load_module('tools/env/proxy')
                load_module('tools/gcc/git/2.24.0')
                subprocess.call('git clone https://github.com/wrf-model/WPS Build_WRF/WPS', shell=True)
                    
    elif 'WRF' not in fraternal_dirs and 'WPS' in fraternal_dirs:
        print('WRF is missing, would you like me to build it from scratch?')
        answer = input()                
                    
        if answer == 'yes' or answer == 'y':
            if confirm() == 'y':
                subprocess.call('mkdir Build_WRF/WRF', shell=True)
                load_module('tools/env/proxy')
                load_module('tools/gcc/git/2.24.0')
                subprocess.call('git clone --recurse-submodules https://github.com/wrf-model/WRF Build_WRF/WRF', shell=True)
                    
    else:
        print('WRF and WPS is missing, would you like me to build them from scratch?')
        answer = input()
        if answer == 'yes' or answer == 'y':
            if confirm() == 'y':
                subprocess.call('mkdir Build_WRF/WPS', shell=True)
                subprocess.call('mkdir Build_WRF/WRF', shell=True)
                load_module('tools/env/proxy')
                load_module('tools/gcc/git/2.24.0')
                subprocess.call('git clone https://github.com/wrf-model/WPS Build_WRF/WPS', shell=True)
                subprocess.call('git clone --recurse-submodules https://github.com/wrf-model/WRF Build_WRF/WRF', shell=True)


#Smaller functions
def centre_message(a):
	print()
	print("-----------------------------------------------------------------------------")
	print("--------------------->"   ,a ," <----------------------")
	print("-----------------------------------------------------------------------------")
    

def confirm():
    """Triple check to save bad errors"""
    print('Are you sure?')
    answer = input()
    if answer == 'y' or answer == 'yes':
        out = 'y'
    else:
        out = 'n'
    return out

def compile_WRF():
    os.chdir('Build_WRF/WRF')
    print("The Current working directory is: {0}".format(os.getcwd()))
    subprocess.call('echo $NETCDFDIR', shell=True)
    subprocess.call('./clean -aa', shell=True)
    print('cleaned')
    
    cmd = "echo 1|echo 34|./configure"
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    #check output for completion
   
    x = str(output).split("\\n")
    if x[-4] == 'This build of WRF will use NETCDF4 with HDF5 compression':
        print("Configured Succesfully")
        
    subprocess.call('./compile em_real >& log.compile', shell=True)

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
                print(line)
                #initialise our open bracket
                if '(' in line and bracket_count == 99:
                    bracket_count = 1
                    argstart = i
                elif '(' in line:
                    bracket_count +=1

                #track the close bracket that matches
                if ')' in line and '!' not in line:
                    bracket_count -= 1
                    
                elif ')' in line and '!' in line:
                    tmp = line.split()
                    #iterate to determine if ! comes before )
                    index_a = 0
                    index_b = 0
                    for (i, l) in enumerate(tmp):
                        if '!' in l:
                            index_a = i
                        elif ')' in l:
                            index_b = i
                    if index_a < index_b:
                        #bracket is within a comment
                        print("Bracket within comment")
                        pass
                    else:
                        bracket_count -= 1
                
                #break when we have closed our first bracket
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
