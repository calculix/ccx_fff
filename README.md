© Ihor Mirzov, December 2019  
Distributed under GNU General Public License v3.0
Libraries ARPACK and SPOOLES have their own licenses

<br/><br/>



[How to use](#how-to-use) |
[Downloads](#downloads) |
[Your help](#your-help) |
[How to compile CalculiX](#how-to-compile-calculix)

<br/><br/>



# Fortran code converter for CalculiX 2.16

Converts old CalculiX Fortran 77 code to the one with free form. Shifts comments and continuation marks for better code folding. Compiles all fortran sources with -ffree-form flag. Takes files to be compiled from Makefile.inc. The script will process sources from folder *ccx_2.16* and put them into *ccx_2.16_ffree_form*. Now those sources are ready for the *make* command. Refer to the official manual instructions how to build. To understand the difference in sources see images below.

Before conversion:  
![before conversion](img_original.png "before conversion")

After conversion - code folding works like a charm:  
![after conversion](img_converted.png "after conversion")

<br/><br/>



# How to use

Default usage is:

    python3 free_form_fortran.py

Also you can explicitly point existing folders to process:

    python3 free_form_fortran.py original_sources_dir converted_sources_dir

All sources are already compiled and built with multithreading. So you can start using CalculiX binaries:

    - ccx_2.16/ccx_2.16_MT

    - ccx_2.16_ffree_form/ccx_2.16_MT

<br/><br/>



# Downloads

Release version of converted and compiled sources together with original one could be found on [the releases page](https://github.com/imirzov/ccx_free_form_fortran/releases).

<br/><br/>



# Your help

- Simply use this software and ask questions.
- Report problems by [posting issues](https://github.com/imirzov/ccx_free_form_fortran/issues).

<br/><br/>



# How to compile CalculiX

<br/><br/>



## Get the prerequisite ARPACK:

    wget http://www.caam.rice.edu/software/ARPACK/SRC/arpack96.tar.gz

    wget http://www.caam.rice.edu/software/ARPACK/SRC/patch.tar.gz

Unpack the two files:

    tar xzvf arpack96.tar.gz

    tar xzvf patch.tar.gz

Edit the makefile "ARmake.inc"

- Change the home directory to the directory where you extracted ARPACK:

        ./ccx_free_form_fortran/ARPACK

- Change platform to:

        PLAT = INTEL

- Change the Fortran compiler to your version by changing the FC variable:

        FC = gfortran

- If you are using gfortran remove -cg89 from the line

        FFLAGS = -O -cg89

- Change the definitions of MAKE and SHELL to be simply make and sh, respectively, with no paths


Edit the file "UTIL/second.f", adding a "*" to the front of the line

    EXTERNAL           ETIME


From the directory "ARPACK", type in the command line:

    make lib

Now you have ARPACK/libarpack_INTEL.a

<br/><br/>



## Get the prerequisite SPOOLES

Download Spooles:

    http://www.netlib.org/linalg/spooles/spooles.2.2.tgz

Unpack it into:

    ./ccx_free_form_fortran/SPOOLES.2.2/

    cd ./ccx_free_form_fortran/SPOOLES.2.2/

Change the compiler version in "Make.inc" to:

    CC = gcc

Complile library:

    make lib

    cd ./ccx_free_form_fortran/SPOOLES.2.2/MT

    make lib

Now we have SPOOLES.2.2/spools.a and SPOOLES.2.2/MT/src/spoolesMT.a

<br/><br/>



## Compile CalculiX

    cd ./ccx_free_form_fortran/ccx_2.16_ffree_form

Edit "Makefile_MT":

- Add "-DUSE_MT=1" to the CFLAGS.

- Add "-ffree-form" to the FFLAGS. It'll remove fixed width of the code lines. So now continuation symbol (&) could be placed in the end of strings, and code folding will work much better.

- Change the compiler version "CC=cc".

- Check pathes for DIR and LIBS to libarpack_INTEL.a, spooles.a and spoolesMT.a.

Make using MT version of the makefile:

    make -f Makefile_MT

Now we have static shared library 'ccx_2.16_MT.a' and final executable 'ccx_2.16_MT'.

Move final executable to make available command 'ccx':

    sudo mv ccx_2.16_MT /usr/local/bin/ccx

To clean folder:

    rm -f *.a *.o
