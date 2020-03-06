import os
import time
import shutil

THREADS = 6
SPECIES = 'gencode.v33.pc_transcripts' #'gencode.vM24.transcripts'
rootdir = '/your_dir/Docker_kallisto'

Condir = '/tmp/wk'

# docker version
Kallisto_ver = '0.46.1--h4f7b962_0'
para_fastq_dump_ver = '0.6.5--py_0'
fastp_ver = '0.20.0--hdbcaa40_0'
seqtk_ver = 'v1.3-1-deb_cv1'


## Make kallisto index
if not os.path.exists('kallisto_idx'):
    os.mkdir('kallisto_idx')
if os.path.exists(os.path.join('kallisto_idx/'+SPECIES+'_index')):
    print('Index file found.')
else:
    cmd = 'wget ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_33/gencode.v33.pc_transcripts.fa.gz' 
    os.system(cmd)
    cmd = 'gzip -d gencode.v33.pc_transcripts.fa.gz'
    os.system(cmd)
    cmd = 'mv gencode.v33.pc_transcripts.fa %s/kallisto_idx/' % (rootdir)
    os.system()

    cmd = 'docker run --rm -v %s:%s/ -w=%s quay.io/biocontainers/kallisto:%s kallisto index -i kallisto_idx/%s_index kallisto_idx/%s.fa' % (rootdir,Condir,Condir,Kallisto_ver,SPECIES,SPECIES)
    print(cmd)
    os.system(cmd)

## Get sampleID
fr = open('fastq_files.txt','r').readlines()
for line in fr:
    line = line.replace('\n','')
    lst = line.split(',')
    filename = lst[0]
    samplename = filename
    if not os.path.exists('output'):
        os.mkdir('output')
    if not os.path.exists(os.path.join('output/',samplename)):
        os.mkdir(os.path.join('output/',samplename))

## Download SRA
    if not os.path.exists('input'):
        os.mkdir('input')
    cmd = 'docker run --rm -v %s/input:/root/ncbi/public/sra inutano/sra-toolkit prefetch %s' % (rootdir,samplename)
    os.system(cmd)

## SRA to FASTQ (Use parallel-fastq-dump) 
    cmd = 'docker run --rm -v %s:%s -w=%s quay.io/biocontainers/parallel-fastq-dump:%s parallel-fastq-dump --sra-id input/%s.sra --threads %d --split-files --gzip' % (rootdir,Condir,Condir,para_fastq_dump_ver,samplename,THREADS)
    os.system(cmd)
    if not os.path.exists(os.path.join('output/',samplename)):
        os.mkdir(os.path.join('output/',samplename))

#    shutil.move(os.path.join(samplename+'_1.fastq.gz'),os.path.join('output/'+samplename))

    cmd = 'mv %s_*.fastq.gz output/%s' % (samplename,samplename)
    os.system(cmd)



## Trimmming (Use fastp)
    out_name = os.path.join('output/'+samplename+'/'+samplename)

    cmd = 'docker run --rm -v %s:%s -w=%s quay.io/biocontainers/fastp:%s fastp -w %d -h %s.html -j %s.json -i %s_1.fastq.gz -I %s_2.fastq.gz -o %s_trim_paired_1.fastq.gz -O %s_trim_paired_2.fastq.gz' % (rootdir,Condir,Condir,fastp_ver,THREADS,out_name,out_name,out_name,out_name,out_name,out_name)
    print(cmd)
    os.system(cmd)


## Mapping (Use kallisto)
    if not os.path.exists('k_results'):
        os.mkdir('k_results_sub')

    cmd = 'docker run --rm -v %s:%s -w=%s quay.io/biocontainers/kallisto:%s kallisto quant -t %d -i kallisto_idx/%s_index -o k_results/%s -b 100 %s_trim_paired_1.fastq.gz %s_trim_paired_2.fastq.gz' %(rootdir,Condir,Condir,Kallisto_ver,THREADS,SPECIES,samplename,out_name,out_name)
    print(cmd)
    os.system(cmd)

