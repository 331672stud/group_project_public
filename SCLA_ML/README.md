# General information 
## Repository structure
```
|
|-- app
|-- model
|-- training model
  |-- existing_file_method
|-- SCLA_ML (venv)
```

### Directory overview
1. `app` - contains `SCLA_ML_vuln_scanner_client.py` and `requirements.txt`
2. `model` - directory for the .gguf file of the model
3. `training model` - directory with legacy files used to create and test model


## Setup
1. Make sure to have sufficient disk storage for the repository, .gguf file and subseqent image + container. In total, may take up to 20 GB.
2. After cloning the repo, copy the `SCLA_ML_model.gguf` file from this link: [SharePoint directory](https://wutwaw-my.sharepoint.com/:u:/g/personal/01178864_pw_edu_pl/IQAgiglWKyQVT525uEowGY8NAU912FRRSOnNOsu9VeZfqVU?e=PImNfK) into the `/model` directory of the repository.
3. Run `docker compose up` - the image and container creation may take a while (~10 minutes), due to downloading and initializing the Ollama model and image. 
4. Warning - after setup, the LLM will be kept in VRAM to provide quick and successful query result without delay, regardless of time in-between queries. The average query return latency is 350ms.
 

## Utility
The trained .gguf file in the link above contains data on the LLM, which can detect the following vulnerabilites:
- SQL Injection (Python, Java)
- Cross-Site Scripting (Python, HTML)
- Buffer Overflow (C)
- Command Injection (Java)
- Path Traversal (Java, low score on tests)
- Insecure Deserialization (Java) 

## Usage
`app/SCLA_ML_vuln_scanner_client` has functions to automatically query and return the values from the LLM in the container. 
The contrainer is set up to forward 11434:11434, so the LLM API is visible on localhost. The client code helps provide a clear
connection through python.

Example usage is in the `connection_example.py` file.

When querying a singe string of code to the LLM, use `analyze` function.
When querying several strings of code at once, use `analyze_batch`.
When querying from a file, use `analyze_file`. The content of the file should be the code.

When writing own API code or posting to ollama directly, make sure to follow an instruction skeleton similar to example below:

```    
'''Analyze the following code and determine whether it contains a security vulnerability. 
If a vulnerability is present, state its exact type from this list: 
SQL Injection, Cross-Site Scripting (XSS), Command Injection, Path Traversal, 
Buffer Overflow, Insecure Deserialization. 
If no vulnerability is present, respond with: No Vulnerability.
Code: *paste_code_here* 
'''
```