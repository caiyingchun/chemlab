from ..core.system import System
from ..core.molecule import Atom

from ..data.symbols import symbol_list
import re

symbol_list = [s.lower() for s in symbol_list]


gro_to_cl = {
'OW' : 'O',
'OW1': 'O',
'HW1': 'H',
'HW2': 'H',
'HW3': 'H',
'LI' : 'Li',
'CL' : 'Cl',
'NA' : 'Na',
}

def parse_gro(filename):
    with open(filename) as fn:
        lines = fn.readlines()
        title = lines.pop(0)
        natoms = int(lines.pop(0))
        atomlist = []

        # Let's parse all the natoms
        for i, l in enumerate(lines):
            
            if i == natoms:
                # This is the box size
                fields = l.split()
                boxsize = float(fields[0])
                sys = System(atomlist, boxsize)
                sys.rarray -= sys.boxsize * 0.5
                return sys

            fields = l[0:5], l[5:10], l[10:15], l[15:20], l[20:28], l[28:36], l[36:42]
            fields = [f.strip() for f in fields]
            
            if len(fields) == 7:
                #Only positions are provided
                molidx = int(l[0:5])
                moltyp = l[5:10].strip()
                attyp = l[10:15].strip()
                atidx  = int(l[15:20])
                rx     = float(l[20:28])
                ry     = float(l[28:36])
                rz     = float(l[36:42])
                
                # Do I have to convert back the atom types, probably yes???
                if attyp.lower() not in symbol_list:
                    attyp = gro_to_cl[attyp]
                
                atomlist.append(Atom(attyp, [rx, ry, rz]))                


def parse_gro_lines(lines):
    '''Reusable parsing'''
    title = lines.pop(0)
    natoms = int(lines.pop(0))
    atomlist = []
    for l in lines:
        fields = l.split()
        if len(fields) == 6:
            #Only positions are provided
            molidx = int(l[0:5])
            moltyp = l[5:10].strip()
            attyp = l[10:15].strip()
            atidx  = int(l[15:20])
            rx     = float(l[20:28])
            ry     = float(l[28:36])
            rz     = float(l[36:42])

            # Do I have to convert back the atom types, probably yes???
            if attyp.lower() not in symbol_list:
                attyp = gro_to_cl[attyp]

            atomlist.append(Atom(attyp, [rx, ry, rz]))                

        if len(fields) == 3:
            # This is the box size
            boxsize = float(fields[0])
            return System(atomlist, boxsize)
                
def write_gro(sys, filename):
    
    lines = []
    lines.append('Generated by chemlab')
    lines.append('{:>5}'.format(sys.n))
    
    at_n = 0
    # Residue Number
    for i, b in enumerate(sys.bodies):
        res_n = i + 1
        
        try:
            res_name = b.export['groname']
        except KeyError:
            raise Exception('Gromacs exporter need the residue name as groname')

        for j, a in enumerate(b.atoms):
            try:
                at_name = a.export['grotype']
            except KeyError:
                raise Exception('Gromacs exporter needs the atom type as grotype')
            
            at_n += 1
            x, y, z = a.coords # + sys.boxsize*0.5
            
            lines.append('{:>5}{:>5}{:>5}{:>5}{:>8.3f}{:>8.3f}{:>8.3f}'
                         .format(res_n, res_name, at_name, at_n, x, y, z))
    
    lines.append('{:>10.5f}{:>10.5f}{:>10.5f}'.format(sys.boxsize, sys.boxsize, sys.boxsize))
    
    for line in lines:
        print line
        
    lines = [l + '\n' for l in lines]
    
    with open(filename, 'w') as fn:
        fn.writelines(lines)
        
# Util functions
def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]

def read_gro_traj(filename):
    with open(filename) as fn:
        lines = fn.readlines()
    
    # Compute the dimension of each frame!
    natoms = int(lines[1])
    dim_frame = natoms + 3
    
    frames = chunks(lines, dim_frame)
    syslist = []
    for f in frames:
        sys = parse_gro_lines(f)
        sys.rarray -= sys.boxsize*0.5
        syslist.append(sys)
        
    return syslist
    
    