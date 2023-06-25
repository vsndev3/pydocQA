# docQA
Question Answering of private documents using open source LLM running localy.

NOTE: <i>This software is in very early stages of development!</i>
## Quick start
* Install [podman](https://podman.io/docs/installation) (for [macOS see here](https://github.com/containers/podman/blob/main/docs/tutorials/mac_win_client.md)) and [initialize](https://github.com/containers/podman/blob/main/docs/tutorials/podman-for-windows.md) it. i.e make sure <i>podman ps</i> command works in your terminal
* Start the container mounting your document directory and vectorDB directory
   * Run ingest documents by running: ``` podman run -it -v /mnt/c/Temp/books/:/docQA/docs -v /mnt/c/Temp/vecdb/:/docQA/vecdb docker.io/vsndev3/docqa_v1_mpt7b:latest /docQA/docQA.py import-pdfs --dir /docQA/docs```
   * Run the above command with different PDF directories to have a combined vector DB at the given directory
* Start the container in interactive mode
   * Chat with your documents by running:
    ```podman run -it -v /mnt/c/Temp/vecdb/:/docQA/vecdb docker.io/vsndev3/docqa_v1_mpt7b:latest```
* enjoy :sparkler::cocktail:

![image](https://github.com/vsndev3/docQA/assets/63557727/2db6b9f0-5274-4428-8eb7-69cfa0794ee0)

## Running locally
Clone this repo using below command and install the python requiremens and run it!

<details>
<summary><B>Base tools installation</B></summary>

If you are not having python and git but you want to run from source then install below:
 * Python for your operating system from https://www.python.org/downloads/
 * Git for your operating system from https://git-scm.com/downloads
</details>


```
git clone https://github.com/vsndev3/docQA.git
pip3 install -r requirements.txt

cd src
mkdir docs vecdb
# copy PDFs to docs directory

python3 docQA.py import_pdfs --dir ./docs 
python3 docQA.py question

<Ctl+c> to quit once done
```

<details>
<summary><B>Preparing docker image</B></summary>

## Creating Docker image
Creating container image packs models and python dependecies into single image, so that its easier to spin up and running even inside wallgardend enviroments. To build a docker image use the following command
* Install podman (if you are not using docker) and optionaly podman desktop from https://podman.io/
* Customize the Dockerfile to your needs, for example you can preload PDF files and models files as needed. It is not required to load source documents or models as they can be mounted when container is started
* <i>podman build -f Dockerfile -t my_docqa_container</i>
* Once podman build is successful run it <i>podman.exe run -it localhost/my_docqa_container</i>
</details>

<details>
<summary><B>Use cases</B></summary>

## Adding documents
Start the application with <i>import_pdfs</i> option with the directory containing the PDF files. This is needed one time for scanning and creating vector database. There after this directory need not be specified or mounted (in case of container usage)

```
Assuming /dir/doc_folder_1 and /dir/doc_folder_2 has PDF files, then run one by one as below:

docQA.py import-pdfs --dir /dir/doc_folder_1
docQA.py import-pdfs --dir /dir/doc_folder_2 
```
## Searching for data
Start the application with <i>question</i> option and in the prompt enter your question that could be retrieved from the documents you have already provided

> To search start the application as below, after doing adding of documents at least one time.
> ```
>docQA.py question
>```

>To start search with different threads:
>```
>docQA.py question --threads 12
>```

>To start the answering less rigid way, start with higher temperature
>```
>docQA.py question --temperature 0.8
>```

Check the available parameters for tuning using <i>docQA.py question --help</i>

## Deleting the data
At this moment parital delete is not implemented. To delete vector database created from the documents, delete the contents of <i>vecdb</i> directory
</details>
