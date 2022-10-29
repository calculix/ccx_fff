#! /usr/bin/env python3
# -*- coding: utf-8 -*-

""" © Ihor Mirzov, January 2020.
Distributed under GNU General Public License v3.0

Converts Calculix old Fortran 77 code to the one with free form.
Shifts comments and continuation marks for better code folding.
Compiles all fortran sources with -ffree-form flag.
Takes files to be compiled from Makefile.inc.
The script will process sources from folder 'src'
and put them into 'src_fff'. 

Default usage is:
python3 ccx_fff.py
or:
Ctrl+F5 from VSCode

Also you can explicitly point folders to process:
python3 ccx_fff.py ./src ./ccx_linux/src_fff
python3 ccx_fff.py ./src ./ccx_windows/src_fff """

import os
import sys
import re
import shutil

# Get folders to work with
def get_dirs():
    try:
        original_sources_dir = sys.argv[-2] + '/'
        converted_sources_dir = sys.argv[-1] + '/'
    except:

        # OS name
        if os.name=='nt':
            op_sys = 'ccx_windows'
        else:
            op_sys = 'ccx_linux'

        original_sources_dir = 'src'
        converted_sources_dir = os.path.join(op_sys, 'src_fff')

    if not os.path.isdir(converted_sources_dir):
        os.mkdir(converted_sources_dir)

    return original_sources_dir, converted_sources_dir

# Copy files
def copy_files(original_sources_dir, converted_sources_dir):

    # Copy non-fortran files
    nonfortran_file_list = [os.path.basename(f) \
        for f in os.listdir(original_sources_dir)
            if not f.endswith('.f')]
    for file_name in sorted(nonfortran_file_list):
        shutil.copy(os.path.join(original_sources_dir, file_name),
            os.path.join(converted_sources_dir, file_name))

    # Process fortran files
    fortran_file_list = [os.path.basename(f) \
        for f in os.listdir(original_sources_dir)
            if f.endswith('.f')]

    return sorted(fortran_file_list)

# Main function which processes fortran files
def process(file_name, original_sources_dir, converted_sources_dir):
    print(file_name)

    # Read file
    with open(os.path.join(original_sources_dir, file_name),
            'r', encoding='Windows-1252') as f:
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

        # Exclusion for linscal.f, linvec.f, lintemp*.f
        if ('linscal.f' in file_name) \
            or ('linvec.f' in file_name) \
            or ('lintemp.f' in file_name) \
            or ('lintemp_th' in file_name) \
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
            or ('crackpropagations.f' in file_name) \
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
        if lines[i].rstrip().endswith('&') and lines[i+1].strip().startswith(('\'', '\"')):
            lines[i] = lines[i].rstrip()[:-1] + ' ' + lines[i+1].strip()
            continue

    # Shift comments for code folding
    shift = 0
    for i in range(len(lines),0,-1):
        match = re.match('^\s+', lines[i-1])
        if match and not lines[i-1].lstrip().startswith('!'):
            shift = len(match.group(0))
        if lines[i-1].lstrip().startswith('subroutine'):
            shift = 0

        if lines[i-1].lstrip().startswith('!'):
            lines[i-1] = ' '*shift + lines[i-1].strip() + '\n'

    # Write file
    with open(os.path.join(converted_sources_dir, file_name),
            'w', encoding='Windows-1252') as f:
        for line in lines:
            f.write(line)

# Compile processed Fortran files
def compile(converted_sources_dir):
    os.chdir(converted_sources_dir)

    # Take files to be compiled from Makefile.inc
    with open('Makefile.inc', 'r') as makefile:
        lines = makefile.readlines()
    for line in lines:
        match = re.match('^\S+\.f', line)
        if match:
            # Compile files with -ffree-form flag
            file_name = match.group(0)
            if os.path.isfile(file_name):
                if not os.path.isfile(file_name[:-2]+'.o'): # skip already compiled files
                    # try:
                    os.system('gfortran -Wall -O2 -fopenmp -ffree-form -c ' + file_name)
                    # except Exception as e:
                    #     print(str(e.__traceback__))
                    #     break

if __name__ == '__main__':

    # Clean screen
    os.system('cls' if os.name=='nt' else 'clear')

    # Get folders to work with
    src, fff = get_dirs()

    # Copy all files
    fortran_file_list = copy_files(src, fff)

    # Convert Fortran files
    for file_name in fortran_file_list:
        process(file_name, src, fff)

    # compile(fff)
    print('END')
