# Use official miniconda3
FROM continuumio/miniconda3
CMD ["/bin/bash"]

MAINTAINER Thurston Sexton <thurston.sexton@nist.gov>

USER root

RUN conda config --set ssl_verify no
# RUN conda install --quiet --yes 'pip' && conda clean -tipsy
RUN pip install --upgrade pip

RUN mkdir /home/code
WORKDIR /home/code
ADD . /home/code

EXPOSE 5000
EXPOSE 5006

RUN apt-get clean
RUN apt-get update
RUN apt-get -y install gcc

RUN pip install .[dash]
ENTRYPOINT ["/bin/sh", "-c", "nestor-dash"]