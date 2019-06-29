#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    © Ihor Mirzov, June 2019.
    Distributed under GNU General Public License, version 2.

    Converts old Calculix 2.15 Fortran 77 code to the one with free form.
    Shifts comments and continuation marks for better code folding.
    Compiles all fortran sources with -ffree-form flag.
    Takes files to be compiled from Makefile.inc.

    The script will process sources from folder './ccx_2.15_original_fortran/'
    and put them into './ccx_2.15_converted_fortran/'. So, default usage is:
        python3 free_form_fortran.py

    Also you can explicitly point existing folder names to process:
        python3 free_form_fortran.py original_sources_dir converted_sources_dir
"""


import os, sys, re, shutil


# Main function which processes fortran files
def process(file_name, original_sources_dir, converted_sources_dir):
    print(file_name)

    # Read file
    with open(original_sources_dir+file_name, 'r', encoding='Windows-1252') as f:
        lines = f.readlines()

    # Simple replacements
    for i in range(len(lines)): # iterate over lines in file
        # Replace comment sign
        if re.match('^c|d|\*', lines[i].lower()):
            lines[i] = '! ' + lines[i][1:]

        # Replace tabs
        lines[i] = lines[i].replace('\t', ' '*7)

        # Braces with spaces
        lines[i] = lines[i].replace('reshape(( ', 'reshape((')

    # Move continuation symbol + exclusions
    for i in range(len(lines)-1): # iterate over lines in file

        # Current and next lines
        j = 0
        next_line = ''
        line = lines[i].rstrip() # cut '\n'
        while i+j < len(lines)-1:
            j += 1
            if not lines[i+j].startswith('!'): # non-comment
                next_line = lines[i+j].rstrip() # cut '\n'
                break

        # Move continuation symbol - '&' or others - to the end of previous line
        if re.match('^\s{5}\S', next_line): # if next_line isn't empty
            lines[i] = line + '&\n'
            lines[i+j] = ' '*6 + next_line[6:] + '\n'


        # Exclusion for fluidsections.f
        if 'fluidsections.f' in file_name:
            lines[i] = lines[i].replace('noil _mat', 'noil_mat')

        # Exclusion for resultsforc.f, resultsforc_em.f
        if 'resultsforc.f' in file_name \
            or 'resultsforc_em.f' in file_name:
            if re.match('^\s+if\(nodempc\(3', line) \
                and re.match('^\s{5}\S', next_line):
                lines[i] = line + next_line[6:] + '\n'
                lines[i+j] = '!\n'

        # Exclusion for xlocal.f
        if 'xlocal.f' in file_name:
            if line.endswith('D+0/'):
                lines[i] = line + next_line[6:] + '\n'
                lines[i+j] = '!\n'
            lines[i] = lines[i].replace(', ',',')
            lines[i] = lines[i].replace('00000000000000D','D')

        # Exclusion for hybsvd.f
        if 'hybsvd.f' in file_name:
            if len(lines[i]) > 72 and not lines[i].startswith('!'):
                if lines[i].endswith('&\n'):
                    lines[i] = lines[i][:71].rstrip() + '&\n'
                else:
                    lines[i] = lines[i][:71].rstrip() + '\n'

        # Exclusion for linscal.f, linvec.f, lintemp.f, lintemp_th.f
        if ('linscal.f' in file_name) \
            or ('linvec.f' in file_name) \
            or ('lintemp.f' in file_name) \
            or ('lintemp_th.f' in file_name) \
            or ('shape8hr.f' in file_name) \
            or ('umat_single_crystal.f' in file_name) \
            or ('umat_single_crystal_creep.f' in file_name):
            if lines[i].strip().endswith('reshape((&'):
                lines[i] = lines[i].rstrip()[:-1] + lines[i+j].strip() + '&\n'
                lines[i+j] = '!\n'
            if (lines[i].strip() == '),(/20,27/))') \
                or lines[i].strip() == '),(/6,18/))':
                lines[i-1] = lines[i-1].rstrip()[:-1] + lines[i].strip() + '\n'
                lines[i] = '!\n'
            if lines[i].strip().endswith('z4+(x&'):
                lines[i] = lines[i].rstrip()[:-2] + '&\n'
                lines[i+j] = ' '*9 + 'x' + lines[i+j].lstrip()

        # Exclusion for noelsets.f, splitline.f, statics.f
        if ('noelsets.f' in file_name) \
            or ('splitline.f' in file_name) \
            or ('statics.f' in file_name):
            if lines[i].endswith('=\'1&\n') \
                or lines[i].endswith(')=\'&\n') \
                or lines[i].endswith('\'NMIN=0&\n') \
                or lines[i].endswith('\'NMAX=0&\n'):
                lines[i] = lines[i].rstrip()[:-1] + '\'//&\n'
                lines[i+j] = ' '*6 + '\'\'//\n'
            if lines[i].strip() == '\'':
                lines[i] = lines[i][:6] + '\'' + lines[i][7:]

        # Exclusion zeta_calc.f
        if 'zeta_calc.f' in file_name:
            match = re.search('\s+d0', lines[i])
            if match: lines[i] = lines[i].replace(match.group(0), 'd0')
            match = re.search('\.\s+gt\.\s+', lines[i])
            if match: lines[i] = lines[i].replace(match.group(0), '.gt.')
            if lines[i].endswith('outside valid&\n'):
                lines[i] = lines[i].rstrip()[:-1] + '\'//&\n'
                lines[i+j] = lines[i+j][:6] + '\'' + lines[i+j][7:]

        # Exclusion for dqag.f
        if 'dqag.f' in file_name:
            match = re.search('/ \S+ \S+ \S+ \S+ d0 /', lines[i])
            if match:
                lines[i] = lines[i].replace(match.group(0), \
                    match.group(0).replace(' ', ''))

        # Exclusion for all files
        if lines[i].rstrip().endswith('&') and lines[i+j].strip() == '':
            lines[i] = lines[i][:-2] + '\n'

    # Shift comments for code folding
    shift = 0
    for i in range(len(lines),0,-1):
        match = re.match('^\s+', lines[i-1])
        if match and not lines[i-1].lstrip().startswith('!'):
            shift = len(match.group(0))
        if 'subroutine' in lines[i-1]:
            shift = 0

        if lines[i-1].lstrip().startswith('!'):
            lines[i-1] = ' '*shift + lines[i-1].strip() + '\n'

    # Write file
    with open(converted_sources_dir+file_name, 'w', encoding='Windows-1252') as f:
        for line in lines:
            f.write(line)


if (__name__ == '__main__'):
    # Clean screen
    os.system('cls' if os.name=='nt' else 'clear')

    # Path to folders
    try:
        original_sources_dir = sys.argv[-2] + '/'
        converted_sources_dir = sys.argv[-1] + '/'
    except:
        original_sources_dir = './ccx_2.15_original_fortran/'
        converted_sources_dir = './ccx_2.15_converted_fortran/'

    # Copy non-fortran files
    nonfortran_file_list = [os.path.basename(f) \
        for f in os.listdir(original_sources_dir) if not f.endswith('.f') ]
    for file_name in sorted(nonfortran_file_list):
        shutil.copy(original_sources_dir+file_name, converted_sources_dir+file_name)

    # Process fortran files
    fortran_file_list = [os.path.basename(f) \
        for f in os.listdir(original_sources_dir) if f.endswith('.f') ]
    for file_name in sorted(fortran_file_list):
        process(file_name, original_sources_dir, converted_sources_dir)
        # break # one file only

    # Take files to be compiled from Makefile.inc
    os.chdir(converted_sources_dir)
    with open('Makefile.inc', 'r') as makefile:
        lines = makefile.readlines()
    for line in lines:
        match = re.match('^\S+\.f', line)
        if match:
            # Compile files with -ffree-form flag
            file_name = match.group(0)
            if os.path.isfile(file_name) \
                and not os.path.isfile(file_name[:-2]+'.o'): # skip already compiled files
                try:
                    os.system('gfortran -Wall -O3 -fopenmp -ffree-form -c ' + file_name)
                except:
                    break

print('END')