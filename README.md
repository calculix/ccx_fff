© Ihor Mirzov, May 2019  
Distributed under GNU General Public License v3.0

<br/><br/>



# Fortran code converter for Calculix 2.15

Converts old Calculix 2.15 Fortran 77 code to the one with free form. Shifts comments and continuation marks for better code folding. Compiles all fortran sources with -ffree-form flag. Takes files to be compiled from Makefile.inc. The script will process sources from folder *./ccx_2.15_original_fortran/* and put them into *./ccx_2.15_converted_fortran/*. Now sources in folder '*./ccx_2.15_converted_fortran/*' are ready for the *make* command. Refer to the official manual instructions how to build. To understand the difference in sources see images below.

Before conversion:  
![before conversion](img_original.png "before conversion")

After conversion:  
![after conversion](img_converted.png "after conversion")

<br/><br/>



# How to use

Default usage is:

    python3 free_form_fortran.py

Also you can explicitly point existing folder names to process:

    python3 free_form_fortran.py original_sources_dir converted_sources_dir

<br/><br/>



# Your help

- Simply use this software and ask questions.
- Share your models and screenshots.
- Report problems by [posting issues](https://github.com/imirzov/ccx_free_form_fortran/issues).
- Do something from the [TODO-list](#TODO).

<br/><br/>



# TODO

- Check comments in initialconditionss.f