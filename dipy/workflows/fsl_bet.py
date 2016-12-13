from __future__ import division, print_function, absolute_import

import os
import logging
import inspect
import subprocess
import shutil

from os import path


from dipy.workflows.workflow import Workflow


class BrainExtraction(Workflow):
    @classmethod
    def get_short_name(cls):
        return 'bet'

    def run(self, input_files, save_masked=False, out_dir='',
            out_mask='brain_mask.nii.gz', out_masked='brain_masked.nii.gz'):
        """ Workflow wrapping the fsl bet executable.

        Applies fsl bet on each file found by 'globing'
        ``input_files`` and saves the results in a directory specified by
        ``out_dir``.

        Parameters
        ----------
        input_files : string
            Path to the input volumes. This path may contain wildcards to
            process multiple inputs at once.
        save_masked : bool optional
            Save mask (default False)
        out_dir : string, optional
            Output directory (default input file directory)
        out_mask : string, optional
            Name of the mask volume to be saved (default 'brain_mask.nii.gz')
        out_masked : string, optional
            Name of the masked volume to be saved (default 'dwi_masked.nii.gz')
        """
        io_it = self.get_io_iterator()

        for fpath, mask_out_path, masked_out_path in io_it:
            logging.info('Calling fsl bet on {0}'.format(fpath))

            bet_command = 'fsl5.0-bet {0} {1} -m'.format(fpath, masked_out_path)
            subprocess.call(bet_command.split(' '))
            real_out_dir = path.dirname(masked_out_path)
            bname, ext = path.splitext(path.basename(masked_out_path))
            if '.gz' in ext:
                bname, ext = path.splitext(bname)

            mask_tmp_out = path.join(real_out_dir, bname + '_mask.nii.gz')
            shutil.move(mask_tmp_out, mask_out_path)

            if not save_masked:
                os.remove(masked_out_path)

        return io_it
