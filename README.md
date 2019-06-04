© Ihor Mirzov, UJV Rez, May 2019.  
Distributed under GNU General Public License, version 2.

<br/><br/>



# Fortran code converter for Calculix 2.15

Converts old Calculix 2.15 Fortran 77 code to the one with free form.  
Shifts comments and continuation marks for better code folding.  
Compiles all fortran sources with -ffree-form flag. Takes files to be compiled from Makefile.inc.

The script will process sources from folder './ccx_2.15_original_fortran/' and put them into './ccx_2.15_converted_fortran/'. So, default usage is:

    python3 free_form_fortran.py

Also you can explicitly point existing folder names to process:

    python3 free_form_fortran.py original_sources_dir converted_sources_dir