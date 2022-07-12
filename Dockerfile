# FROM nvcr.io/nvidia/cuda:10.0-devel-centos7
FROM nvcr.io/nvidia/pytorch:22.06-py3
# Declare some ARGuments
# ARG PYTHON_VERSION=3.6
# FROM nvidia/cuda:9.0-cudnn7-runtime
# # Declare some ARGuments
# ARG PYTHON_VERSION=3.7


# ARG CONDA_VERSION=3
# ARG CONDA_PY_VERSION=4.5.11
# # Installation of some libraries / RUN some commands on the base image
# RUN apt-get update && \
#     DEBIAN_FRONTEND=noninteractive apt-get install -y — no-install-recommends python3-pip python3-dev wget \
#     bzip2 libopenblas-dev pbzip2 libgl1-mesa-glx && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*
# # INSTALLATION OF CONDA
# ENV PATH /opt/conda/bin:$PATH
# RUN wget — quiet https://repo.anaconda.com/miniconda/Miniconda$ CONDA_VERSION-$ CONDA_PY_VERSION-Linux-x86_64.sh -O ~/miniconda.sh && \
#     /bin/bash ~/miniconda.sh -b -p /opt/conda && \
#     rm ~/miniconda.sh && \
#     /opt/conda/bin/conda clean -tipsy && \
#     ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
#     echo “. /opt/conda/etc/profile.d/conda.sh” >> ~/.bashrc && \
#     echo “conda activate base” >> ~/.bashrc


RUN conda
RUN conda create -n myenv python=3.7.2 
RUN activate myenv

RUN pip install --user flair==0.7.0

COPY . /app
WORKDIR /app

RUN ls
RUN chmod +x /app/example.sh
CMD ./example.sh
