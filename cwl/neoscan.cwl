arguments:
- position: 0
  prefix: --out-dir
  valueFrom: output
- position: 0
  prefix: --log-dir
  valueFrom: logs
- position: 0
  prefix: --neoscan-dir
  valueFrom: /pecgs-neoscan/src/neoscan
- position: 0
  prefix: --optitype-script
  valueFrom: /usr/local/bin/OptiType/OptiTypePipeline.py
- position: 0
  prefix: --f-opti-config
  valueFrom: /pecgs-neoscan/src/neoscan/config.ini
- position: 0
  prefix: --netmhc
  valueFrom: /pecgs-neoscan/src/netmhc/netMHC-4.0/netMHC
- position: 0
  prefix: --f-allele
  valueFrom: /pecgs-neoscan/src/netmhc/netMHC-4.0/data/allelelist
baseCommand:
- /usr/bin/python
- /pecgs-neoscan/src/neoscan.py
class: CommandLineTool
cwlVersion: v1.0
id: neoscan
inputs:
- id: maf
  inputBinding:
    position: '1'
  type: File
- id: bam
  inputBinding:
    position: '2'
  secondaryFiles:
  - $(self.basename).bai
  type: File
- id: ref_dir
  inputBinding:
    position: '0'
    prefix: --ref-dir
  type: Directory
- id: bed
  inputBinding:
    position: '0'
    prefix: --bed
  type: File
- default: dna
  id: input_type
  inputBinding:
    position: '0'
    prefix: --input-type
  type: string?
- default: /usr/local/bin/OptiType:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/conda/bin:/home/biodocker/bin:/miniconda/envs/neoscan/bin:/miniconda/bin:$PATH
  id: environ_PATH
  type: string?
label: neoscan
outputs:
- id: snv_summary
  outputBinding:
    glob: output/sample/sample.neo.snv.summary
  type: File
- id: indel_summary
  outputBinding:
    glob: output/sample/sample.neo.indel.summary
  type: File
requirements:
- class: DockerRequirement
  dockerPull: estorrs/pecgs-neoscan:0.0.1
- class: ResourceRequirement
  coresMin: 4
  ramMin: 100000
- class: EnvVarRequirement
  envDef:
    PATH: $(inputs.environ_PATH)
