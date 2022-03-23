FROM fred2/optitype
#FROM ubuntu:18.04

USER root
RUN apt-get update && apt-get install -y vim wget curl git

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.3-Linux-x86_64.sh -O ~/miniconda.sh
RUN bash ~/miniconda.sh -b -p /miniconda

ARG OG_PATH="$PATH"
RUN echo $OG_PATH
ENV PATH="/miniconda/bin:$PATH"

# get env file seperately so it doesn't reinstall every time
COPY ./env.yaml /pecgs-neoscan/env.yaml
RUN conda env create --file /pecgs-neoscan/env.yaml 

COPY . /pecgs-neoscan

ENV PATH="$OG_PATH:/miniconda/envs/neoscan/bin:/miniconda/bin"

#CMD /bin/bash
ENTRYPOINT ["/bin/bash", "-c"]
