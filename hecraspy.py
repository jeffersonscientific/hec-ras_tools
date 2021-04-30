
import numpy
import scipy
import pylab as plt
import datetime as datetime
import matplotlib as mpl
#import matplotlib.datetime as mpd
#
import h5py
import sys
import os
#import shutil
#
class HEC_RAS_unsteady(object):
    def __init__(self, project_name=None, geom_index=None, plan_index=None, **kwargs):
        #
        if project_name is None or project_name.strip()=='':
            raise Exception("Valid project name required.")\
        #
        # TODO: more rigorous validation on indices...
        if (geom_index is None and plan_index is None):
            raise Exception("Valid geom_index and/or plan_index required.")
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
        self.__dict__.update({ky:vl for ky,vl in locals().items() if not ky in ('self', '__class__')})
        #
    def fix_text_files(self):
        # for now, assume text files are small, so we can just read() them
        #  if we want.
        #
        # TODO: write backups of these text files...
        #
        with open(self.b_fname, 'r') as fin:
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
        #with open(self.b_fname, 'w') as fout:
        #    fout.write(b_text)
        #
        with open(self.x_fname, 'r') as fin:
            x+text = fin.read().replace('{}{}'.format(chr(13), chr(10)), chr(10))
        #
        #with open(self.x_fname, 'w') as fout:
        #    fout.write(x_text)
        print('*** {}'.format(b_text))
        
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
        prams['geom_index'] = argv[2]
    if len(argv) >= 4 and not '=' in argv[3]:
        # TODO: handle empty case...
        prams['plan_index'] = argv[3]
    prams.update(dict([av.replace(chr(32), '').split('=') for av in sys.argv[1:] if '=' in av]) )
    #
    # we need three values, we can iner one:
    # 1) project name
    # 2) geometry_index
    # 3) plan_index (2 or 3 can default one from the other; it makes more sense
    #   to have multiple plans for a given geometry).
    # TODO: add a dict to map common names to a given name, ie:
    # {'geom_index':'geometry_index', ...} or {'geometry_index':['geom_index', 'g_index', ...], ... }
    #
    HR = HEC_RAS_unsteady(**prams)
    #
    print('*** HR: ', HR.__dict__)
    HR.fix_text_files()

