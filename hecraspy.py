
import numpy
import scipy
import pylab as plt
import datetime as datetime
import matplotlib as mpl
import glob
#import matplotlib.datetime as mpd
#
import h5py
import sys
import os
import shutil
import subprocess
#
# TODO: Most geometries for PescaderoButano give an error, more or less:
# "weir elevation lower than the cells they are connected to"
# Here is some help:
# http://hec-ras-help.1091112.n5.nabble.com/Problem-with-dam-simulation-td6596.html
# Hannah Hampson has suggested a few geometry/plan combos that should run, but they don't Some just throw an error on the wier thing, and then die.
#  others seem to try to soldier on and then segfault. For the PescaderoButano sets, geom=1, plan=1 seems to run.
#
class HEC_RAS_unsteady(object):
    def __init__(self, project_name=None, geom_index=None, plan_index=None,
    working_dir=None, input_dir=None, do_backup=None, do_fix_files=True, do_execute=False, exe_stdout=None, exe_stderr=None, **kwargs):
        '''
        # @project_name: filename prefix that nominally describes the project. Example: for the
        #  the plan file, SMC_010.b06, project_name=SMC_010; plan_index=6 (see below)
        # @geom_index: index of geometry files. submit as an integer; zero-packing will be done.
        # @plan_index: index of plan files. submit as integer.
        # @do_backup: backup files that are modified. This will keep making more backups, so be careful...
        # @working_dir: Optional. A working directory. Only missing files will be (re-)coied, so to totally
        #  start over, nuke working_dir first.
        # NOTE: required input files: *.c{k}, *.x{k}, *.g{k}.hdf, *.b{k}, *.p{k}.tmp.hdf
        '''
        #
        do_backup, do_fix_files, do_execute = [my_bool(x) for x in (do_backup, do_fix_files, do_execute)]
        if project_name is None or project_name.strip()=='':
            raise Exception("Valid project name required.")
        #
        # TODO: more rigorous validation on indices...
        if (geom_index is None and plan_index is None):
            raise Exception("Valid geom_index and/or plan_index required.")
        #
        # If working_dir is provided, create a working directory and copy relevant
        #  files to that location for... working on. If working_dir is provided, the default
        #  value of do_backups if False, otherwise its default is True.
        if input_dir is None:
            input_dir = os.getcwd()
        if working_dir is None:
            working_dir = input_dir
        working_dir = os.path.abspath(working_dir)
        input_dir = os.path.abspath(input_dir)
        #
        if geom_index is None:
            geom_index = plan_index
        if plan_index is None:
            plan_index = geom_index
        #
        geom_index = int(geom_index)
        geom_index_str = '00{}'.format(geom_index)[-2:]
        plan_index = int(plan_index)
        plan_index_str = '00{}'.format(plan_index)[-2:]
        #
        # Construct filenames:
        # plan:
        plan_h5_fname = '{}.p{}.hdf'.format(project_name, plan_index_str)
        plan_h5_tmp_fname='{}.p{}.tmp.hdf'.format(project_name, plan_index_str)
        b_fname = '{}.b{}'.format(project_name, plan_index_str)
        #
        # geometry:
        c_fname = '{}.c{}'.format(project_name, geom_index_str)
        x_fname = '{}.x{}'.format(project_name, geom_index_str)
        g_hdf5 = '{}.g{}.hdf'.format(project_name, geom_index_str)
        #
        # files to copy. Note, we'll handl ethe plan HDF5 (plan_h5_tmp_fname) differently.
        files_to_copy =[c_fname, x_fname, g_hdf5, b_fname]
        #
        self.__dict__.update({ky:vl for ky,vl in locals().items() if not ky in ('self', '__class__')})
        #
        # NOTE: this does not correct the case working_dir exists, but is not a directory. For
        #  now, we want this to error off.
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)
        if not os.path.isdir(working_dir):
            raise Exception('ERROR: working_dir: {} is not a directory.')
        #
        # if working_dir and input_dir are the same, default to no backup otherwise default to do backup.
        if working_dir == input_dir and do_backup is None:
            do_backup = True
        if working_dir != input_dir:
            # working_dir stuf:
            # - default do_backup value,
            # - copy files, etc.
            if do_backup is None:
                do_backup = False
            #
            # get dir of working_dir (will be abs paths):
            #fls_in_wd = glob.glob(os.path.join(working_dir, "*"))
            # TODO: make this list more robust by applying abspath()?
            for fl in files_to_copy:
                if not os.path.exists(self.working_path(fl)):
                    shutil.copy(self.input_path(fl), self.working_path(fl) )
                #
            #
        #
        #
        if do_fix_files:
            self.fix_text_files(do_backup=do_backup)
            self.fix_plan_hdf(do_backup=do_backup)
        #
        self.__dict__.update({ky:vl for ky,vl in locals().items() if not ky in ('self', '__class__')})
        #
        if do_execute:
            #
            exe_return = self.execute_hecras()
        #
    def execute_hecras(self, exe_stdout=None, exe_stderr=None):
        #
        exe_stdout = exe_stdout or self.exe_stdout
        exe_stderr = exe_stderr or self.exe_stderr
        exe_stdout = exe_stdout or sys.stdout
        exe_stderr = exe_stderr or sys.stderr
        #
        this_dir = os.getcwd()
        os.chdir(self.working_dir)
        #
        exe_str = f'ulimit -s unlimited; {os.environ["HECRAS_EXE"]} {self.c_fname} b{self.plan_index_str}'
        print('*** exe_str: ', exe_str)
        #r_val = subprocess.run([os.environ['HECRAS_EXE'], self.c_fname, f'b{self.plan_index_str}'], stdout=exe_stdout, stderr=exe_stderr)
        r_val = subprocess.run(exe_str, shell=True, stdout=exe_stdout, stderr=exe_stderr)
        #
        os.chdir(this_dir)
        return r_val
    #
    def working_path(self, fname):
        '''
        # appends self.working_dir to fname
        '''
        return os.path.join(self.working_dir, fname)
    def input_path(self, fname):
        '''
        # appends self.input_dir to fname
        '''
        return os.path.join(self.input_dir, fname)
    #
    def fix_plan_hdf(self, do_backup=None):
        # remove {results:} group from the plan hdf5. Two approaches:
        # 1) move (or copy and backup) plan_h5 -> plan_h5.tmp, remove {results: } group from plan_h5.tmp
        # 2) Create a new file plan_h5.tmp, copy contents (except {results:}) from
        #    plan_h5, delete (or backup-copy) planh_5)
        #  both approaches should be equivalent; 1) should be faster for large geometries with small results, and possibly more robust (can we miss elements of the HDF5 object?); 2) will likely be faster for files with large results groups.
        #
        # note that then (as I understand it), all the work gets done in the .tmp
        #  file, which in fact does not get renamed.
        if do_backup is None:
            do_backup = self.do_backup
        if do_backup is None:
            do_backup = True
        #
        if do_backup and os.path.exists(self.working_path(self.plan_h5_fname)):
            self.hdf_p_bkp_name = self.backup_file(self.working_path(self.plan_h5_fname))
        #
        with h5py.File(self.working_path(self.plan_h5_tmp_fname), 'w') as fout,\
                h5py.File(self.input_path(self.plan_h5_fname), 'r') as fin:
            for fattr in fin.attrs.keys():
                # note: be sure the syntax forces a copy of values, not a reff. or replacement
                fout.attrs[fattr] = fin.attrs.get(fattr, None)[:]
            for fg in fin.keys():
                if fg == 'Results': continue
                # note: there are multiple syntax options here as well. I think also,
                # fout[fg][:] = fin[fg][:]
                fin.copy( fg, fout )
            #
        #
        return 0
    #
    def fix_text_files(self, do_backup=None):
        # for now, assume text files are small, so we can just read() them
        #  if we want.
        #
        if do_backup is None:
            do_backup = self.do_backup
        if do_backup is None:
            do_backup = True
        #
        # TODO: write backups of these text files...
        #
        if do_backup:
            self.b_bkp_name = self.backup_file(self.working_path(self.b_fname) )
            self.x_bkp_name = self.backup_file(self.input_path(self.x_fname))
        #
        # NOTE: it would also make sense to read from self.input_dir and write to
        #   self.working_dir, and we cold skip the os filecopy step... except that
        #
        with open(self.working_path(self.b_fname), 'r') as fin:
            b_text = fin.read().replace('{}{}'.format(chr(13), chr(10)), chr(10))
            #
            for rw in b_text.split('\n'):
                #
                # TODO: not quite right here...
                # or ":"+chr(92)
                if rw[1:3]==":\\":
                    #print('*** Found filename.')
                    #fname_rw = rw
                    #fname = fname_rw.split('\\')
                    b_text = b_text.replace(rw, rw.split('\\')[-1])
                    break
                #
            #
        #
        with open(self.working_path(self.b_fname), 'w') as fout:
            fout.write(b_text)
        #
        # x-text:
        with open(self.working_path(self.x_fname), 'r') as fin:
            x_text = fin.read().replace('{}{}'.format(chr(13), chr(10)), chr(10))
        #
        with open(self.working_path(self.x_fname), 'w') as fout:
            fout.write(x_text)
        #print('*** {}'.format(b_text))
    #
    def backup_file(self, fname):
        k_index=0
        for k,fl in enumerate(glob.glob(f'{fname}.bkp_*')):
            # NOTE: let's force the *_{index} notation, just to simplify our code.
            k_index = max( int(fl.split('_')[-1]), k_index) + 1
        foutname = f'{fname}.bkp_{f"000{k_index}"[-4:]}'
        shutil.copy(fname, foutname )
        #
        return foutname
#
def my_bool(s):
    if s is None:
        return None
    if isinstance(s, bool) or isinstance(s, int):
        return bool(s)
    #
    if s.lower() in ['false', 'f', '0']:
        return False
    return True
        
#
if __name__ == '__main__':
    # TODO: also, assume project_name, geom_index, plan_index as default.
    # then, override with **kwargs style.
    argv = sys.argv
    print('** argv: ', argv)
    prams={}
    #
    if not '=' in argv[1]:
        prams['project_name'] = argv[1]
    if not '=' in argv[2]:
        prams['geom_index'] = int(argv[2])
    if len(argv) >= 4 and not '=' in argv[3]:
        # TODO: handle empty case...
        prams['plan_index'] = int(argv[3])
    #
    prams.update(dict([av.replace(chr(32), '').split('=') for av in sys.argv[1:] if '=' in av]) )
    #
    # we need three values, we can inefr one:
    # 1) project name
    # 2) geometry_index
    # 3) plan_index (2 or 3 can default one from the other; it makes more sense
    #   to have multiple plans for a given geometry).
    # TODO: add a dict to map common names to a given name, ie:
    # {'geom_index':'geometry_index', ...} or {'geometry_index':['geom_index', 'g_index', ...], ... }
    #
    HR = HEC_RAS_unsteady(do_backup=False, **prams)
    #
    print('*** HR: ', HR.__dict__)
    #HR.fix_text_files()
    #HR.fix_plan_hdf()

