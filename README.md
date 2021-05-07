# hec-ras_tools
HEC-RAS tools. Namely, tools to use the Linux HEC-RAS implemenatation

HEC-RAS can be obtained here:
https://www.hec.usace.army.mil/software/hec-ras/download.aspx

Documentation to run the Linux version is here:
https://www.hec.usace.army.mil/software/hec-ras/documentation/HEC-RAS_507_Unsteady.pdf

In this repo, we will be building some tools to automate the good counsel provided in these release notes. A few salient points, in summary:
- Input files include "plan" and "geometry" components. Plans and geometries can be mixed.
- The plan output includes an HDF file, like `{plan_name}.p{plan index}.hdf`. We do a funny dance, whereby we run the plan on a "tmp" version of  this file, and then rename the "tmp" back to not-tmp. We'll make the point that a given geometry might have multiple plans by assuming the plan index, `kp=1` and the geometry index, `kg=2` so something like:
    - `mv project.p01.hdf project.p01.tmp.hdf`
    - `remove_results_group('project.po1.tmp.hdf')`
    - `hecras_exe project_name.c02 b01`
    - `mv project.p01.tmp.hdf project.p01.hdf`
- Some text files might require their line termination to be fixed -- ie, changed from CRLF to CR (or LF).

Note that the release notes/docs sggest a script in which the HDF5 file _contents_, except for the `results` group, are copied from the primary to the `.tmp.hdf5`. However, unless there are other extraneous elements, it might be simpler and more efficient to perform an OS level filecopy, and then simply remove the `results` group.

## Example:

The Python interface can be run from a Python command line, like:

```
    (base) [myoder96@sh01-ln02 login /scratch/users/myoder96/hecras]$ ipython
    Python 3.8.5 (default, Sep  4 2020, 07:30:14) 
    Type 'copyright', 'credits' or 'license' for more information
    IPython 7.19.0 -- An enhanced Interactive Python. Type '?' for help.

    In [1]: import hecraspy

    In [2]: HR = hecraspy.HEC_RAS_unsteady(project_name='SMC_010', geom_index=2, plan_index=2, working_dir='work_demo_0202', inpu
       ...: t_dir='PescaderoButano_original', do_execute=True))
``` 

The `hecraspy` module can also be run from the OS command line. A few parameters are directly handled; other parameters are handled as `**kwargs` and then passed to the `HEC_RAS_unsteady()` class object. Generally, input parameters can be identified from `HEC_RAS_unsteady.__init__()`. For example,

    $ python hecraspy.py SMC_010 2 3 working_dir=work_demo_0202 input_dir=PescaderoButano_original do_execute=True
or

    $ python hecraspy.py project_name=SMC_010 geometry_index=2 plan_index=3 working_dir=work_demo_0202 input_dir=PescaderoButano_original do_execute=True

See also the sample batch script, `hecras_sample_batch.sh`. Note that this script is intended specifically to run on Stanford's Sherlock HPC, and in fact uses some modules that are particular to the School of Earth setup, but the basic principles apply to any HPC.
