from __future__ import division, print_function, absolute_import

import inspect

from dipy.workflows.combined_workflow import CombinedWorkflow
from dipy.workflows.denoise import NLMeansFlow
from dipy.workflows.reconst import ReconstDtiFlow
from dipy.workflows.reconst import ReconstCSAFlow, ReconstCSDFlow
from dipy.workflows.fsl_bet import BrainExtraction
from dipy.workflows.io import ConvertDicomFlow, ExtractGradientInfoFlow


class FODFPipelineFSL(CombinedWorkflow):

    def _get_sub_flows(self):
        return [
            BrainExtraction,
            NLMeansFlow,
            ReconstDtiFlow,
            ReconstCSAFlow,
            ReconstCSDFlow
        ]

    def run(self, input_files, bvalues, bvectors, out_dir=''):
        """ A simple dwi processing pipeline with the following steps:
            -Denoising
            -Masking
            -DTI reconstruction
            -HARDI recontruction
            -Deterministic tracking
            -Tracts metrics

        Parameters
        ----------
        input_files : string
            Path to the dwi volumes. This path may contain wildcards to process
            multiple inputs at once.
        bvalues : string
            Path to the bvalues files. This path may contain wildcards to use
            multiple bvalues files at once.
        bvectors : string
            Path to the bvalues files. This path may contain wildcards to use
            multiple bvalues files at once.
        out_dir : string, optional
            Working directory (default input file directory)
        """
        io_it = self.get_io_iterator()

        flow_base_params = {
            'output_strategy': self._output_strategy,
            'mix_names': self._mix_names,
            'force': self._force_overwrite
        }

        for dwi, bval, bvec in io_it:
            # Masking
            be_flow = BrainExtraction(**flow_base_params)
            self.run_sub_flow(be_flow, dwi, out_dir=out_dir)
            dwi_mask = be_flow.last_generated_outputs['out_mask']

            # Denoising
            skip_denoise = False
            nl_flow = NLMeansFlow(output_strategy=self._output_strategy,
                                  mix_names=self._mix_names,
                                  force=self._force_overwrite,
                                  skip=skip_denoise)

            self.run_sub_flow(nl_flow, dwi, out_dir=out_dir)
            denoised = nl_flow.last_generated_outputs['out_denoised']

            # DTI reconstruction
            dti_flow = ReconstDtiFlow(output_strategy='append',
                                      mix_names=self._mix_names,
                                      force=self._force_overwrite)

            self.run_sub_flow(dti_flow, denoised, bval, bvec, dwi_mask,
                              out_dir='metrics')

            # CSD Reconstruction
            csd_flow = ReconstCSDFlow(output_strategy='append',
                                      mix_names=self._mix_names,
                                      force=self._force_overwrite)

            self.run_sub_flow(csd_flow, denoised, bval, bvec, dwi_mask,
                              out_dir='peaks_csd', extract_pam_values=True)

            # CSA reconstruction
            csa_flow = ReconstCSAFlow(output_strategy='append',
                                      mix_names=self._mix_names,
                                      force=self._force_overwrite)
            self.run_sub_flow(csa_flow, denoised, bval, bvec, dwi_mask,
                              out_dir='peaks_csa', extract_pam_values=True)


class DICOMFODFPipelineFSL(CombinedWorkflow):

    def _get_sub_flows(self):
        return [
            ConvertDicomFlow,
            ExtractGradientInfoFlow,
            BrainExtraction,
            NLMeansFlow,
            ReconstDtiFlow,
            ReconstCSAFlow,
            ReconstCSDFlow
        ]

    def run(self, input_files, tag='', out_dir=''):
        """ A simple dwi processing pipeline with the following steps:
            -Denoising
            -Masking
            -DTI reconstruction
            -HARDI recontruction
            -Deterministic tracking
            -Tracts metrics

        Parameters
        ----------
        input_files : string
            Path to the dicom dwi. This path may contain wildcards to process
            multiple inputs at once.
        tag : string optional
            Tag to find if there is multiple series in the dicom. (default '')
        out_dir : string, optional
            Working directory (default input file directory)
        """
        io_it = self.get_io_iterator()

        flow_base_params = {
            'output_strategy': self._output_strategy,
            'mix_names': self._mix_names,
            'force': self._force_overwrite
        }

        for dicom_dwi in io_it:
            dicom_dwi = dicom_dwi[0]

            # Volume conversion
            dicom_flow = ConvertDicomFlow(**flow_base_params)
            self.run_sub_flow(dicom_flow, dicom_dwi, tag=tag, out_dir=out_dir)
            dwi = dicom_flow.last_generated_outputs['out_file']

            # Gradients Extraction
            gradients_flow = ExtractGradientInfoFlow(**flow_base_params)
            self.run_sub_flow(gradients_flow, dicom_dwi, tag=tag, out_dir=out_dir)
            bval = gradients_flow.last_generated_outputs['out_bval']
            bvec = gradients_flow.last_generated_outputs['out_bvec']

            # Masking
            be_flow = BrainExtraction(**flow_base_params)
            self.run_sub_flow(be_flow, dwi, out_dir=out_dir)
            dwi_mask = be_flow.last_generated_outputs['out_mask']

            # Denoising
            skip_denoise = True
            nl_flow = NLMeansFlow(output_strategy=self._output_strategy,
                                  mix_names=self._mix_names,
                                  force=self._force_overwrite,
                                  skip=skip_denoise)

            self.run_sub_flow(nl_flow, dwi, out_dir=out_dir)
            denoised = nl_flow.last_generated_outputs['out_denoised']

            # DTI reconstruction
            dti_flow = ReconstDtiFlow(output_strategy='append',
                                      mix_names=self._mix_names,
                                      force=self._force_overwrite)

            self.run_sub_flow(dti_flow, denoised, bval, bvec, dwi_mask,
                              out_dir='metrics')

            # CSD Reconstruction
            csd_flow = ReconstCSDFlow(output_strategy='append',
                                      mix_names=self._mix_names,
                                      force=self._force_overwrite)

            self.run_sub_flow(csd_flow, denoised, bval, bvec, dwi_mask,
                              out_dir='peaks_csd', extract_pam_values=True)

            # CSA reconstruction
            csa_flow = ReconstCSAFlow(output_strategy='append',
                                      mix_names=self._mix_names,
                                      force=self._force_overwrite)
            self.run_sub_flow(csa_flow, denoised, bval, bvec, dwi_mask,
                              out_dir='peaks_csa', extract_pam_values=True)
