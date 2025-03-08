# SemanticSearch


<img width="1680" alt="Screenshot 2025-03-09 at 2 41 51 AM" src="https://github.com/user-attachments/assets/b11a61ab-b41d-4551-84a0-1bc4026c7685" />





**TRY IT OUT HERE!! 🚀**


***[SemanticSearch Live](http://50.17.56.119:3000/)***


SemanticSearch is an AI-driven research assistant that aggregates, processes, and semantically indexes over **2,000 research documents**. It leverages advanced NLP techniques—such as Sentence Transformer embeddings and FAISS-based vector search—to quickly retrieve relevant papers. The backend is built with FastAPI and deployed via Docker on AWS ECS Fargate (with AWS Keyspaces for data storage), while the frontend is a React application styled with Tailwind CSS.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Backend](#backend)
  - [Data Preprocessing](#data-preprocessing)
  - [Embeddings & FAISS](#embeddings--faiss)
  - [Cassandra (AWS Keyspaces)](#cassandra-aws-keyspaces)
  - [Retrieval-Augmented Generation (RAG)](#retrieval-augmented-generation-rag)
- [Deployment on AWS](#deployment-on-aws)
  - [Docker, ECS Fargate & ALB](#docker-ecs-fargate--alb)
- [Frontend](#frontend)
- [Tech Stack](#tech-stack)
- [Project Setup](#project-setup)
- [Usage](#usage)

## Overview

SemanticSearch enables users to search for research papers by leveraging semantic similarity. It preprocesses data, generates embeddings with Sentence Transformers, and indexes them using FAISS to deliver fast, relevant results without scanning the entire database on every query.


## Architecture



![SemanticSearch](https://github.com/user-attachments/assets/cbb9e359-e88a-4f0e-a366-0f52dc6d7ecb)




  - **Backend:** FastAPI REST API that processes user queries, generates embeddings, and retrieves document metadata.
  - **Data Processing:** Preprocessed research documents stored in AWS S3 and indexed in AWS Keyspaces (Cassandra).
  - **Vector Search:** FAISS indexes normalized embeddings for efficient nearest-neighbor lookup.
  - **Deployment:** Dockerized backend deployed on AWS ECS Fargate behind an Application Load Balancer (ALB).
  - **Frontend:** React application styled with Tailwind CSS provides a responsive search interface.


## Backend

### Data Preprocessing

  - Aggregates research papers, patents, and technical documents.
  - Raw data stored in Amazon S3; processed metadata stored in AWS Keyspaces.

### Embeddings & FAISS

  - **Embeddings:** Generated using the pre-trained Sentence Transformer model (`all-MiniLM-L6-v2`).
  - **FAISS Index:** Efficient vector search to retrieve the top-**k** similar documents, reducing latency by 70%.

### Cassandra (AWS Keyspaces)

  - Stores document metadata and embedding blobs.
  - schema:
    ```
    CREATE TABLE research_data.document_embeddings (
        id text,
        source text,
        embedding blob,
        PRIMARY KEY (source, id)
    );
    ```

  - To Insert data in openalex table:
    ```
    INSERT INTO research_data.openalex (id, title, abstract, publication_year)
        VALUES (?, ?, ?, ?)
    ```

### Retrieval-Augmented Generation (RAG)

  - **Retrieval:** The backend embeds the user query and uses FAISS to retrieve relevant documents.
  - **Lookup:** Full document details (title, abstract, authors) are fetched from Cassandra.
  - **Response:** Returns a JSON payload with non-null document details.


## Deployment on AWS

### Docker, ECS Fargate & ALB

  - **Docker:** The backend is containerized and pushed to AWS ECR.
  - **ECS Fargate:** The service runs continuously as a Fargate task in us-east-2, ensuring low latency with Keyspaces.
  - **Application Load Balancer (ALB):** Routes external traffic to your ECS service, exposing a public URL.


## Frontend

  - **React Application:** Built with React and styled with Tailwind CSS for a modern, responsive UI.
  - **User Interface:** Provides a search bar and an optional number input (defaulting to 5 results). Results are displayed as cards showing title, abstract, and authors.
  - **Integration:** Communicates with the backend API to fetch and display search results dynamically.


## Tech Stack

  - **Cloud & Infrastructure:** AWS (ECS Fargate, ECR, Keyspaces, S3, Route53, ALB, CloudWatch)
  - **Backend:** Python, FastAPI, Docker, Boto3, Cassandra-driver
  - **Data & AI:** Apache Cassandra (AWS Keyspaces), Sentence Transformers, FAISS, NumPy, Pandas
  - **Frontend:** React, Tailwind CSS, React Icons
  - **Tools:** Git, Linux, AWS CLI


## Project Setup

1. **Clone the Repository:**
     ```bash
     git clone https://github.com/Eldrago12/SemanticSearch.git
     cd SemanticSearch
     ```

2. **Backend Setup:**

  - Build the Docker image:
   ```bash
   docker build --platform linux/amd64 -t semanticsearch-backend .
   ```

  - Push the image to AWS ECR.

  - Register an ECS task definition and deploy on ECS Fargate as `ECS Service` with ALB.

  - Ensure environment variables (`KEYSPACES_ENDPOINT`, `SERVICE_USERNAME`, `SERVICE_PASSWORD`, `CERT_PATH`) are correctly set.

3. **Frontend Setup:**

  - Navigate to the frontend directory:
   ```bash
   cd frontend
   yarn install
   yarn start
   ```

  - Build for production:
   ```bash
   yarn run build
   ```


## Usage

  - Querying:
    Access the frontend at the live website, enter your query (e.g., `TLB attacks`), and specify the number of papers (default is 5 if omitted).
    The backend processes the query, retrieves relevant documents using `FAISS`, performs metadata lookups, and returns a JSON response with document details (omitting null fields).

  - Example Request:
    ```
    {
        "query": "Translation lookaside buffer",
        "k": 7
    }
    ```

  - Example Response:
    ```
    {
        "results": [
            {
                "paperid": "dd6c63dc5176f0f7f218d64ceff055a6295edfb0",
                "title": "TLBshield: A Low-Cost Secure Reinforce on Translation Lookaside Buffer to Mitigate the Speculative Attacks",
                "abstract": "Although hardware defenses against speculative attacks have been widely studied, the security of Translation Lookaside Buffer has seldom been studied. In this paper, we propose TLBshield to mitigate Spectre attack on TLB, and evaluates it on a XuanTie C910 RISC-V SOC on FPGA. Linux OS including filesystem and shell is also mounted in the RISC-V core. TLBshield automatically switches on and off the writeback channel from Page Table Walker to the second-level TLB, and increase the security level with almost no performance loss. The performance overhead of TLBshield under SPEC2017 benchmark is negligible, where the maximum performance loss is only 1.77%. Compared with the original RISC-V core, the success rate for attack is reduced from 100% to 55.7%.",
                "authors": "Yuyang Liu, Runye Ding, Yujie Chen, Pujin Xie, Yao Liu, Zhiyi Yu"
            },
            {
                "paperid": "fc64b7b13cac2d2ef02ab9e9d52fd799276f5018",
                "title": "Inferring TLB Configuration with Performance Tools",
                "abstract": "Modern computing systems are primarily designed for maximum performance, which inadvertently introduces vulnerabilities at the micro-architecture level. While cache side-channel analysis has received significant attention, other Central Processing Units (CPUs) components like the Translation Lookaside Buffer (TLB) can also be exploited to leak sensitive information. This paper focuses on the TLB, a micro-architecture component that is vulnerable to side-channel attacks. Despite the coarse granularity at the page level, advancements in tools and techniques have made TLB information leakage feasible. The primary goal of this study is not to demonstrate the potential for information leakage from the TLB but to establish a comprehensive framework to reverse engineer the TLB configuration, a critical aspect of side-channel analysis attacks that have previously succeeded in extracting sensitive data. The methodology involves detailed reverse engineering efforts on Intel CPUs, complemented by analytical tools to support TLB reverse engineering. This study successfully reverse-engineered the TLB configurations for Intel CPUs and introduced visual tools for further analysis. These results can be used to explore TLB vulnerabilities in greater depth. However, when attempting to apply the same methodology to the IBM Power9, it became clear that the methodology was not transferable, as mapping functions and performance counters vary across different vendors.",
                "authors": "Cristian Agredo, Tor J. Langehaug, Scott R. Graham"
            },
            {
                "paperid": "3e4451a8455a0b06ddea464a83a01f99d9c22309",
                "title": "Countering code injection attacks with TLB and I/O monitoring",
                "abstract": "This paper presents a software-transparent protection against binary code injection attacks. With a TLB (Translation Lookahead Buffer) that is usually split between data (DTLB) and instructions (ITLB) as found in modern processors, a simple protection can be developed based on an observation that activating an injected code causes a data TLB hit under ITLB miss with dirty bit set in the hit TLB entry. However, such a protection is not applicable in practice unless the system does not allow runtime code injections, while modern systems utilize runtime generated code rather extensively. The protection presented distinguishes an activation of a legitimated runtime generated codes from binary code injection attacks at an ITLB miss. The protection monitors not only address translation requests coming to TLB but also the address of the buffer used for I/O operations. This allows information flow tracking that filters out illegitimate code injection. The protection blocks an activation of the code injected via an I/O operation by analyzing TLB flags and the translation request profile. To evaluate our idea, we have revised the address translation function in Bochs x86 simulator and conducted code injection attacks available over the Internet to see how many code injections our idea can detect. The experimental results show that the proposed protection can detect all the code injection attacks tested without revising the operating system.",
                "authors": "Dongkyun Ahn, Gyungho Lee"
            },
            {
                "id": "https://openalex.org/W2077901430",
                "title": "Countering code injection attacks with TLB and I/O monitoring",
                "abstract": "This paper presents a software-transparent protection against binary code injection attacks. With a TLB (Translation Lookahead Buffer) that is usually split between data (DTLB) and instructions (ITLB) as found in modern processors, a simple protection can be developed based on an observation that activating an injected code causes a data TLB hit under ITLB miss with dirty bit set in the hit TLB entry. However, such a protection is not applicable in practice unless the system does not allow runtime code injections, while modern systems utilize runtime generated code rather extensively. The protection presented distinguishes an activation of a legitimated runtime generated codes from binary code injection attacks at an ITLB miss. The protection monitors not only address translation requests coming to TLB but also the address of the buffer used for I/O operations. This allows information flow tracking that filters out illegitimate code injection. The protection blocks an activation of the code injected via an I/O operation by analyzing TLB flags and the translation request profile. To evaluate our idea, we have revised the address translation function in Bochs x86 simulator and conducted code injection attacks available over the Internet to see how many code injections our idea can detect. The experimental results show that the proposed protection can detect all the code injection attacks tested without revising the operating system."
            },
            {
                "id": "https://openalex.org/W2767982226",
                "title": "Neural machine translation for low-resource languages without parallel corpora",
                "abstract": "The problem of a total absence of parallel data is present for a large number of language pairs and can severely detriment the quality of machine translation. We describe a language-independent method to enable machine translation between a low-resource language (LRL) and a third language, e.g. English. We deal with cases of LRLs for which there is no readily available parallel data between the low-resource language and any other language, but there is ample training data between a closely-related high-resource language (HRL) and the third language. We take advantage of the similarities between the HRL and the LRL in order to transform the HRL data into data similar to the LRL using transliteration. The transliteration models are trained on transliteration pairs extracted from Wikipedia article titles. Then, we automatically back-translate monolingual LRL data with the models trained on the transliterated HRL data and use the resulting parallel corpus to train our final models. Our method achieves significant improvements in translation quality, close to the results that can be achieved by a general purpose neural machine translation system trained on a significant amount of parallel data. Moreover, the method does not rely on the existence of any parallel data for training, but attempts to bootstrap already existing resources in a related language."
            },
            {
                "paperid": "d9a8a841d3e8d2c33b663d6f87bd3f8ec48bee1e",
                "title": "Translation Leak-aside Buffer: Defeating Cache Side-channel Protections with TLB Attacks",
                "abstract": "To stop side channel attacks on CPU caches that have allowed attackers to leak secret information and break basic security mechanisms, the security community has developed a variety of powerful defenses that effectively isolate the security domains. Of course, other shared hardware resources exist, but the assumption is that unlike cache side channels, any channel offered by these resources is insufficiently reliable and too coarse-grained to leak general-purpose information. This is no longer true. In this paper, we revisit this assumption and show for the first time that hardware translation lookaside buffers (TLBs) can be abused to leak fine-grained information about a victim's activity even when CPU cache activity is guarded by state-of-the-art cache side-channel protections, such as CAT and TSX. However, exploiting the TLB channel is challenging, due to unknown addressing functions inside the TLB and the attacker's limited monitoring capabilities which, at best, cover only the victim's coarse-grained data accesses. To address the former, we reverse engineer the previously unknown addressing function in recent Intel processors. To address the latter, we devise a machine learning strategy that exploits high-resolution temporal features about a victim's memory activity. Our prototype implementation, TLBleed, can leak a 256-bit EdDSA secret key from a single capture after 17 seconds of computation time with a 98% success rate, even in presence of state-of-the-art cache isolation. Similarly, using a single capture, TLBleed reconstructs 92% of RSA keys from an implementation that is hardened against FLUSH+RELOAD attacks.",
                "authors": "Ben Gras, Kaveh Razavi, H. Bos, Cristiano Giuffrida"
            },
            {
                "id": "https://openalex.org/W2889508486",
                "title": "Translation leak-aside buffer : Defeating cache side-channel protections with TLB attacks",
                "abstract": "To stop side channel attacks on CPU caches that have allowed attackers to leak secret information and break basic security mechanisms, the security community has developed a variety of powerful defenses that effectively isolate the security domains. Of course, other shared hardware resources exist, but the assumption is that unlike cache side channels, any channel offered by these resources is insufficiently reliable and too coarse-grained to leak general-purpose information. This is no longer true. In this paper, we revisit this assumption and show for the first time that hardware translation lookaside buffers (TLBs) can be abused to leak fine-grained information about a victim's activity even when CPU cache activity is guarded by state-of-the-art cache side-channel protections, such as CAT and TSX. However, exploiting the TLB channel is challenging, due to unknown addressing functions inside the TLB and the attacker's limited monitoring capabilities which, at best, cover only the victim's coarse-grained data accesses. To address the former, we reverse engineer the previously unknown addressing function in recent Intel processors. To address the latter, we devise a machine learning strategy that exploits high-resolution temporal features about a victim's memory activity. Our prototype implementation, TLBleed, can leak a 256-bit EdDSA secret key from a single capture after 17 seconds of computation time with a 98% success rate, even in presence of state-of-the-art cache isolation. Similarly, using a single capture, TLBleed reconstructs 92% of RSA keys from an implementation that is hardened against FLUSH+RELOAD attacks."
            }
        ]
    }
    ```


## Contribute & Connect

If you find any improvements or have better approaches, feel free to contribute! 🚀

Let's connect and discuss further optimization of this project:

- **LinkedIn**: [Sirshak Dolai](https://www.linkedin.com/in/sirshak-dolai)
- **LinkedIn**: [Ananya Tiwari](https://linkedin.com/in/ananya-tiw)


⭐️ **If you find this repo helpful, consider giving it a star!** ⭐️
