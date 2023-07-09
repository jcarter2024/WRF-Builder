#!/bin/bash
#$-cwd

####### FUNCTIONS
get_libpng () {
  wget https://onboardcloud.dl.sourceforge.net/project/libpng/libpng16/1.6.37/libpng-1.6.37.tar.gz --no-check-certificate
    tar xvf libpng-1.6.37.tar.gz >& libpngtar.log
    cd libpng-1.6.37/
    ./configure --prefix="$1/wrf_libs_intel/"
    echo "Making libpng..."
    make >& libpngmake.log
    make install >& libpnginstall.log
    cd ../
    echo "cleaning up"
    rm libpng-1.6.37.tar.gz
    rm -r libpng-1.6.37
}


get_jasper () {
    wget https://www.ece.uvic.ca/~frodo/jasper/software/jasper-1.900.29.tar.gz
    tar xvf jasper-1.900.29.tar.gz >& jaspertar.log
    cd jasper-1.900.29/
    ./configure --prefix="$1/wrf_libs_intel/"
    echo "Making jasper..."
    make >& jaspermake.log
    make install >& jasperinstall.log
    cd ../
    echo "cleaning up"
    rm jasper-1.900.29.tar.gz
    rm -r jasper-1.900.29
}


####### CODE START
export CC=icc
export CXX=icpc
export FC=ifort
export F90=ifort

module load mpi/intel-17.0/openmpi/4.0.1
module load libs/intel-17.0/netcdf/4.6.2
module load tools/env/proxy
module load tools/gcc/git/2.24.0

# STEP 1: check if Build_WRF exists
echo "========================================="
echo "       Checking your WRF build..."
echo "========================================="

DIRECTORY="Build_WRF/"
if [ ! -d "$DIRECTORY" ]; then
  read -p "$DIRECTORY does not exist. Shall I build it? " confirm
  echo $confirm
  if [ $confirm == y ]; then
      mkdir Build_WRF
  else
  echo "Can't proceed without Build WRF"
  kill -INT $$
  fi
else
  echo "$DIRECTORY is present"
fi

#check if WRF and WPS exist
cd Build_WRF/
bw_dir=$(pwd)
DIRECTORY="WRF/"
if [ ! -d "$DIRECTORY" ]; then
  read -p "$DIRECTORY does not exist. Shall I build it? " confirm
  if [ $confirm == y ]; then 
      mkdir WRF
      git clone --recurse-submodules https://github.com/wrf-model/WRF WRF/
  fi
else
  echo "$DIRECTORY is present"
fi
DIRECTORY="WPS/"
if [ ! -d "$DIRECTORY" ]; then
  read -p "$DIRECTORY does not exist. Shall I build it? "
  if [ $confirm == y ]; then 
      mkdir WPS
      git clone https://github.com/wrf-model/WPS WPS/
  fi
else
  echo "$DIRECTORY is present"
fi

echo "     ===============    "
echo "     FILE structure"
echo "     ===============    "
echo " -->> $bw_dir"
echo "                        |        "
echo "                    Build_WRF    "
echo "                        |        "
echo "              WPS----------------WRF"



#must build jasper and libpng as they aren't intel compiled
DIRECTORY="wrf_libs_intel"
if [ ! -d "$DIRECTORY" ]; then
  read -p "$DIRECTORY does not exist. Shall I build it? " confirm
  echo $confirm
  if [ $confirm == y ]; then
      mkdir wrf_libs_intel
  else
  echo "Can't proceed without the libraries properly built"
  kill -INT $$
  fi
else
  echo "$DIRECTORY is present"
fi


read -p "I can build Jasper and LIBPNG, would you like me to do that? (y/n): " confirm 
if [ $confirm == y ]; then
    echo "Ok I'll build those and place them in $(pwd)/wrf_libs_intel/"
    if [ ! -d "wrf_libs_intel/" ]; then
        mkdir wrf_libs_intel
    fi
    cd wrf_libs_intel
    if [ ! -f "bin/libpng-config" ]; then
        echo "no libpng found, building..."
        get_libpng $bw_dir
    else
        echo "libpng found, skipping..."
    fi
    if [ ! -f "bin/jasper" ]; then
        echo "no jasper found, building..."
        get_jasper $bw_dir
    else
        echo "jasper found, skipping..."
    fi
    
else
    echo "Skipping, (assuming that these libraries are already built and correctly referenced)"
fi


export NETCDF=$NETCDFDIR
export WRFIO_NCD_LARGE_FILE_SUPPORT=1
export MPI_LIB=

compile_wrf() {
    ./clean -aa
    echo 1|echo 20|./configure >& wrfconfig.log
    echo "I'm compiling WRF, this might take a while..."
    ./compile -j 4 em_real 2>&1 | tee compile.log
            
    #check that it worked
    if [ -f "main/wrf.exe" ]; then
        echo "WRF built succesfully"
    else
        echo "Error with WRF build"
    fi
}

compile_wps() {
    ./clean 
    export JASPERLIB=$bw_dir/wrf_libs_intel/lib/
    export JASPERINC=$bw_dir/wrf_libs_intel/include/
    echo 17|./configure >& WPSconfig.log
    echo "I'm compiling WPS, this might take a while..."
    ./compile 2>&1 | tee compile.log
            
    #check that it worked
    if [ -f "geogrid.exe" ]; then
        echo "WPS built succesfully"
    else
        echo "Error with WPS build"
    fi
}

read -p "I can recompile WRF, shall I do that now? " confirm
if  [ $confirm == "y" ]; then 
    cd "$bw_dir/WRF"
    if [ -f "main/wrf.exe" ]; then
        read -p "I think WRF is already built, proceed? " confirm
        if [ $confirm == "y" ]; then
            compile_wrf
        else
            echo "skipping"
        fi
    else
        compile_wrf
    fi
fi

read -p "I can recompile WPS, shall I do that now? " confirm
if  [ $confirm == "y" ]; then 
    cd "$bw_dir/WPS"
    if [ -f "geogrid.exe" ]; then
        read -p "I think WPS is already built, proceed? " confirm
        if [ $confirm == "y" ]; then
            compile_wps
        else
            echo "Skipping"
        fi
    else
        compile_wps
    fi
fi

#if all of the above is done your WRF build should be ready to go. Now we can work on editing the files 

cd $bw_dir #<<<<<<<--------------! back in the build wrf directory
cd ../

#run the python code
# python3 MAIN.py 
./editor.sh

#allow for recompilation after edits
read -p "I can recompile WRF, shall I do that now? " confirm
if  [ $confirm == "y" ]; then 
    cd "$bw_dir/WRF"
    if [ -f "main/wrf.exe" ]; then
        read -p "I think WRF is already built, proceed? " confirm
        if [ $confirm == "y" ]; then
            compile_wrf
        else
            echo "skipping"
        fi
    else
        compile_wrf
    fi
fi
