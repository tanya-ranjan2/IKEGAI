#Projects

  
  

#Platform

  

##IKE.GAI

# Introduction

Welcome to the IKE.GAI platform – an advanced No Code GEN AI platform designed to empower users to create multiple GENAI use cases quickly and easily. Our platform is built on powerful Large Language Models and uses multiple agents and tools to provide intelligent services around user data.

With multiple microservices, our platform offers the capability to override the use case template built with domain-specific knowledge base, which can be evaluated using multiple matrices. The built-in use cases can be tried and tested on the platform, allowing users to fine-tune their models to perfection.

At IKE.GAI, we also provide an option to expose your models via different mediums, such as API and containerization, ensuring that your models can be accessed and utilized by anyone. With our platform, you can create powerful and intelligent models without any coding experience, making it easy for you to turn your ideas into reality.

  
  

## QuickStart

  

For Development Environment

  

```python

python -m uvicorn main:app --reload

```

  

For Deployment Environment

  

```python

python -m uvicorn main:app --host 0.0.0.0 --port 8000

```

  
  

##  For Dev ENV

  

codes with `#<CODEBLOCk>` will be changed in the prod ENV

  

```python

#<CODEBLOCk> TODO -START

  

#<CODEBLOCk> END OF BLOCK

  

```

  

TO BE DELETED

- FOLDER:_temp

  
  

Functions used across would be placed in `utils`

- dbops.py : Database related functions
- llmops.py : any functions or classes related to LLM should be in this file
    - llmbuilder function: function for creating instances of the LLM caller
- parser.py : functions related to parsing