"""
neoscan.pl wrapper

UPDATE: converting to 2.7 so it works with optitype
"""
import argparse
import os
import logging
import subprocess

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

parser.add_argument('--f-allele', type=str,
    help='f allele list')

parser.add_argument('--netmhc', type=str,
    help='netMHC')

parser.add_argument('--f-opti-config', type=str,
    help='config opti')

args = parser.parse_args()


def preprocess_maf(maf_fp, snp_vcf_fp, indel_vcf_fp):
    maf = pd.read_csv(maf_fp, sep='\t', header=1)

    valid = ['SNP']
    snp = maf[[True if s in valid else False
              for s in maf['Variant_Type']]]
    snp = snp[['Chromosome', 'Start_Position', 'Reference_Allele',
               'Tumor_Seq_Allele2', 'Hugo_Symbol', 'HGVSp_Short']]
    snp['type'] = 'Somatic'
    logging.info('SNP vcf input has shape {s}'.format(s=snp.shape))

    valid = ['INS', 'DEL']
    indel = maf[[True if s in valid else False
                for s in maf['Variant_Type']]]
    indel = indel[['Chromosome', 'Start_Position', 'Reference_Allele',
                   'Tumor_Seq_Allele2', 'Hugo_Symbol', 'HGVSp_Short']]
    indel['type'] = 'Somatic'
    logging.info('INDEL vcf input has shape {s}'.format(s=indel.shape))

    snp.to_csv(snp_vcf_fp, sep='\t', index=False, header=False)
    indel.to_csv(indel_vcf_fp, sep='\t', index=False, header=False)


def setup_run(maf, bam, out_dir):
    """
    Setup directory structure that neoscan expects.

    Also preprocessing on snp and indel vcf files
    """
    # Path(out_dir).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    input_dir = os.path.join(out_dir, 'sample')
    # Path(input_dir).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)

    snp_vcf_fp = os.path.join(input_dir, 'sample.snp.vcf')
    indel_vcf_fp = os.path.join(input_dir, 'sample.indel.vcf')
    preprocess_maf(maf, snp_vcf_fp, indel_vcf_fp)

    # create sym links for bam
    os.symlink(bam, os.path.join(input_dir, 'sample.bam'))
    try:
        os.symlink('{b}.bai'.format(b=bam), os.path.join(input_dir, 'sample.bam.bai'))
    except:
        logging.info('could not symlink {b}.bai'.format(b=bam))

    return snp_vcf_fp, indel_vcf_fp


def neoscan_commands(
        out_dir, log_dir, input_type, bed, ref_dir,
        optitype_script, f_allele, netmhc, f_opti_config):
    cmds = []
    rna = '1' if input_type == 'rna' else '0'
    for step in range(1, 7):
        pieces = [
            'perl neoscan.pl',
            '--rdir {o}'.format(o=out_dir),
            '--bed {b}'.format(b=bed),
            '--refdir {r}'.format(r=ref_dir),
            '--optitype {o}'.format(o=optitype_script),
            '--fallele {f}'.format(f=f_allele),
            '--netmhc {n}'.format(n=netmhc),
            '--fopticonfig {f}'.format(f=f_opti_config),
            '--bam 1',
            '--rna {r}'.format(r=rna),
            '--log {lg}'.format(lg=log_dir),
            '--step {s}'.format(s=step),
        ]
        cmd = ' '.join(pieces)
        cmds.append(cmd)
    return cmds


def run_neoscan(out_dir, log_dir, maf, bam, input_type, bed, ref_dir,
                optitype_script, f_allele, netmhc, f_opti_config, neoscan_dir):
    logging.info('preparing input dir')
    snp_vcf_fp, indel_vcf_fp = setup_run(maf, bam, out_dir)

    cmds = neoscan_commands(
        out_dir, log_dir, input_type, bed, ref_dir,
        optitype_script, f_allele, netmhc, f_opti_config)

    # change cwd so neoscan works
    old_cwd = os.getcwd()
    os.chdir(neoscan_dir)

    for i, cmd in enumerate(cmds):
        logging.info('step {index}'.format(index=i + 1))
        logging.info('executing command: {c}'.format(c=cmd))
        output = subprocess.check_output(cmd, shell=True)
        logging.info('step output: {o}'.format(o=output))

    os.chdir(old_cwd)


def main():
    modified_out_dir, modified_log_dir = args.out_dir, args.log_dir
    if not os.path.isabs(args.out_dir):
        modified_out_dir = os.path.join(os.getcwd(), args.out_dir)
    if not os.path.isabs(args.log_dir):
        modified_log_dir = os.path.join(os.getcwd(), args.log_dir)
    # Path(modified_out_dir).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(modified_out_dir):
        os.makedirs(modified_out_dir)
    # Path(modified_log_dir).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(modified_log_dir):
        os.makedirs(modified_log_dir)
    run_neoscan(
        modified_out_dir, modified_log_dir, args.maf, args.bam,
        args.input_type, args.bed, args.ref_dir, args.optitype_script,
        args.f_allele, args.netmhc, args.f_opti_config,
        args.neoscan_dir)


if __name__ == '__main__':
    main()
