import argparse
import os
import logging
import subprocess
from pathlib import Path

import pandas as pd

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

parser = argparse.ArgumentParser()

parser.add_argument('maf', type=str,
    help='Filepath of inputs vcf.')

parser.add_argument('bam', type=str,
    help='Filepath of input BAM for HLA typing')

parser.add_argument('--input-type', type=str, default='dna',
    help='"rna" if RNA input, "dna" if dna input. Default is dna')

parser.add_argument('--bed', type=str,
    help='Input proteome bed file')

parser.add_argument('--ref-dir', type=str,
    help='Directory with reference files')

parser.add_argument('--out-dir', type=str, default='output',
    help='output directory')

parser.add_argument('--log-dir', type=str, default='logs',
    help='log directory')

parser.add_argument('--neoscan-dir', type=str,
    help='root of neoscan src code')

parser.add_argument('--optitype-script', type=str,
    help='location of optitype script')

args = parser.parse_args()


def preprocess_maf(maf, snp_vcf_fp, indel_vcf_fp):
    maf = pd.read_csv('/data/sandbox/test.maf', sep='\t', header=1)

    valid = ['SNP']
    snp = maf[[True if s in valid else False
              for s in maf['Variant_Type']]]
    snp = snp[['Chromosome', 'Start_Position', 'Reference_Allele',
               'Tumor_Seq_Allele2', 'Hugo_Symbol', 'HGVSp_Short']]
    snp['type'] = 'Somatic'
    logging.info(f'SNP vcf input has shape {snp.shape}')

    valid = ['INS', 'DEL']
    indel = maf[[True if s in valid else False
                for s in maf['Variant_Type']]]
    indel = indel[['Chromosome', 'Start_Position', 'Reference_Allele',
                   'Tumor_Seq_Allele2', 'Hugo_Symbol', 'HGVSp_Short']]
    indel['type'] = 'Somatic'
    logging.info(f'INDEL vcf input has shape {indel.shape}')

    snp.to_csv(snp_vcf_fp, sep='\t', index=False, header=False)
    indel.to_csv(indel_vcf_fp, sep='\t', index=False, header=False)


def setup_run(maf, out_dir):
    """
    Setup directory structure that neoscan expects.

    Also preprocessing on snp and indel vcf files
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    input_dir = os.path.join(out_dir, 'sample')
    Path(input_dir).mkdir(parents=True, exist_ok=True)

    snp_vcf_fp = os.path.join(input_dir, 'sample.snp.vcf')
    indel_vcf_fp = os.path.join(input_dir, 'sample.indel.vcf')
    preprocess_maf(maf, snp_vcf_fp, indel_vcf_fp)

    return snp_vcf_fp, indel_vcf_fp


def neoscan_commands(out_dir, log_dir, bam, input_type, bed, ref_dir,
                     optitype_script):
    cmds = []
    rna = '1' if input_type == 'rna' else '0'
    for step in range(1, 6):
        pieces = [
            f'perl neoscan.pl',
            f'--rdir {out_dir}',
            f'--log {log_dir}',
            f'--bamfq {bam}',
            f'--bed {bed}',
            f'--rna {rna}',
            f'--refdir {ref_dir}',
            f'--optitype {optitype_script}',
            f'--step {step}',
        ]
        cmd = ' '.join(pieces)
        cmds.append(cmd)
    return cmds


def run_neoscan(out_dir, log_dir, maf, bam, input_type, bed, ref_dir,
                optitype_script, neoscan_dir):
    logging.info('preparing input dir')
    snp_vcf_fp, indel_vcf_fp = setup_run(maf, out_dir)

    Path(log_dir).mkdir(parents=True, exist_ok=True)

    cmds = neoscan_commands(
        out_dir, log_dir, bam, input_type, bed, ref_dir,
        optitype_script)

    # change cwd so neoscan works
    old_cwd = os.getcwd()
    os.chdir(neoscan_dir)

    for i, cmd in enumerate(cmds):
        logging.info(f'step {i}')
        logging.info(f'executing command: {cmd}')
        output = subprocess.check_output(cmd, shell=True)
        logging.info(f'step output: {output}')

    os.chdir(old_cwd)


def main():
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    run_neoscan(
        args.out_dir, args.log_dir, args.maf, args.bam,
        args.input_type, args.bed, args.ref_dir, args.optitype_script,
        args.neoscan_dir)


if __name__ == '__main__':
    main()
