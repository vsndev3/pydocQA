FROM ubuntu:latest

# install python3 and pip3
RUN apt update &&                 \
    apt install python3 -y &&     \
    apt install python3-pip -y && \
    apt install git -y         && \
    apt install git-lfs -y     && \
    apt install wget -y

# make a room for application
RUN mkdir /docQA
RUN mkdir /docQA/models
RUN mkdir /docQA/docs
RUN mkdir /docQA/vecdb
COPY src/docQA.py /docQA/docQA.py
RUN chmod +x /docQA/docQA.py
COPY requirement.txt requirement.txt

# install pip3 packages required
RUN pip3 install -r requirement.txt

# This setp is only if model has to be packed within container
# the other way is to comment out here, and then mount the models
# directory with command line during runtime
WORKDIR /docQA/models
RUN git clone https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
RUN wget https://huggingface.co/TheBloke/MPT-7B-Instruct-GGML/resolve/main/mpt-7b-instruct.ggmlv3.q5_0.bin

# This setp is only if model has to be packed within container
# the other way is to comment out here, and then mount the models
# directory with command line during runtime
WORKDIR /docQA/docs

# setup workdir, note we use everything relative this directory
# mount /docQA/docs to mount host directory containing PDFs
# mount /docQA/models to mount host directory containing models
# Remember to run this container in interative mode :)
WORKDIR /docQA/
RUN ./docQA.py --install-completion bash
RUN echo "export PATH=$PATH:/docQA" >> ~/.bashrc
CMD ["/usr/bin/python3", "./docQA.py", "question"]
