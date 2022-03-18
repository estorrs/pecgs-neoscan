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
  valueFrom: /miniconda/envs/neoscan/bin/OptiPathPipeline.py
- position: 0
  prefix: --f-opti-config
  valueFrom: /pecgs-neoscan/src/neoscan/config.ini
baseCommand:
- python
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
- id: f_allele
  inputBinding:
    position: '0'
    prefix: --f-allele
  type: File
- id: netmhc
  inputBinding:
    position: '0'
    prefix: --netmhc
  type: File
- default: dna
  id: input_type
  inputBinding:
    position: '0'
    prefix: --input-type
  type: string?
- default: /miniconda/envs/neoscan/bin:$PATH
  id: environ_PATH
  type: string?
label: neoscan
outputs:
- id: snv_summary
  outputBinding:
    glob: output/sample.neo.snv.summary
  type: File
- id: indel_summary
  outputBinding:
    glob: output/sample.neo.indel.summary
  type: File
requirements:
- class: DockerRequirement
  dockerPull: estorrs/pecgs-neoscan:0.0.1
- class: ResourceRequirement
  ramMin: 28000
- class: EnvVarRequirement
  envDef:
    PATH: $(inputs.environ_PATH)
