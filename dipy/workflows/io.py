import re
import inspect
import logging
import os
import subprocess

from dipy.workflows.workflow import Workflow


def get_dicom_index(image_path, requested_tag):
    command = 'mrinfo {0}'.format(image_path)
    command_list = command.split(' ')

    proc = subprocess.Popen(command_list, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    _, stdout = proc.communicate(input='q')

    dicom_idx = None
    tags_regex = re.compile(r'(\d+)\s+-.*:\d\d (' + requested_tag + r') \(\*')
    for idx, tag in tags_regex.findall(stdout):
        if tag == requested_tag:
            dicom_idx = idx
            break

    return dicom_idx


def convert_dicom(dicom_path, dicom_index, out_path):
    command = 'mrconvert {0} {1} -datatype uint16 -force'.format(dicom_path, out_path)
    command_list = command.split(' ')

    proc = subprocess.Popen(command_list, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stderr, stdout = proc.communicate(input=str(dicom_index))
    print stderr
    print stdout

class ConvertDicomFlow(Workflow):
    @classmethod
    def get_short_name(cls):
        return 'convert_dicom'

    def run(self, input_files, tag='ep2d_diff_mddw_20_p2', out_dir='', out_file='dwi.nii.gz'):
        """ Workflow for converting dicom files to nifti.

        Parameters
        ----------
        input_files : string
            Path to the input volumes. This path may contain wildcards to
            process multiple inputs at once.
        tag : string optional
            Tag to find in the mrconvert output (default ep2d_diff_mddw_20_p2)
        out_dir : string, optional
            Output directory (default input file directory)
        out_file : string, optional
            Output file to be converted.
        """

        io_it = self.get_io_iterator()

        for vol, out_file in io_it:
            dicom_idx = get_dicom_index(vol, tag)
            convert_dicom(vol, dicom_idx, out_file)

