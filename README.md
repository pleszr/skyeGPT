tbd

# Run locally
cd skyegpt-backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
PYTHONPATH=. python3 main.py

# Purpose
This application takes a set of documentation and creates an online chatbot which can answer based on the documentation. For demonstration and not for production purposes.

# Behavior
The application can consume documentation (currently from public confluance spaces and local markdown files) and provides a chatbot which will answer the questions using the provided documentations as context. For context lookup and conversation management there are two possible options, one which uses a locally hosted semantic database and one which relies on the v2 Assistant API from OpenAI.

## Differences
### Diagram
![Alt text](readme_resources/difference.png?raw=true "Difference between Chroma and Assistant option")
### Detailed differences
-  With Assistant, OpenAI stores your documents and does the search on it as a black box, while with Chroma you are doing the lookup yourself (therefor it can be fine-tuned for your needs, based on your documentation). 
- With Assistant, OpenAI handles the conversation-management for you and, while remaining within a thread, keeps the context up-to-date. With Chroma, you have to do this manually with prompt-engineering.
- Speed. Assistant is considerably a lot slower than the Chroma lookup. *Detailed analysis is work in progress.*
- Readiness: assistant is in beta and is discouraged to rely on it on production. Backward compatibility is promised, but not committed. 
- Debugging options: if the search is not performing as expected, due to the black box nature of Assistant your debugging options are limited. With Chroma, you can verify what are the relevant documents you feed to OpenAI for answer generation.

## Chroma
Chroma uses a locally hosted semantic vector db (Chroma) to identify the top 3 "closest neighbor" and feeds it to OpenAI's chat completion API. The application supports markdown files in the /content folder and can automatically split it to smaller texts multiple way.
### Key details
- Context lookup is happening locally. The application converts the question's semantic to a vector and looks up which document in the database is the closest (this is what we call neighbor). This is fast and can be optimized for your needs/documents.
- The text generation to OpenAI is stateless, the full conversation history needs to be sent to OpenAI's every request. This is managed in the backend, the frontend asks for a new conversation_id at every refresh.
### Technical details
There are two major workflows, the Setup and the Asker. Setup needs to ran only 1x post deployment or can be used to change the defined parameters. Asker is where workflow for asking questions.
#### Diagram
![Alt text](readme_resources/chroma.png?raw=true "Chroma Architecture & Workflow")
#### Parameters explained
|  Parameter| Purpose  |
|--|--|
| collection_name | Defines the name of your collection. For now, keep it as SkyeDoc, later it will allow supporting multiple parallel collections.
 should_import | can be true/false. If true, when the setup request is sent, it will scan the folders and import. Be careful, one file can be imported multiple times and that can cause issues with the closest neighbor! Setting it to false prevents this. Use this if you want to change another parameter without triggering re-import.
folder_path | The path to the folder where the markdown files are stored. Use skyedoc to set documentation source to Skye which is required to generate links.
k_nearest_neighbors | Defines how much of the closest neighbors from the vector db will be sent to ChatGPT as relevant documentation. Is one of the fine/tuning options for better outputs.
markdown_split_headers | The application splits the markdown files to smaller/bigger chunks based on headers. Possible values are ["#"], ["#","##"], ["#","##","###"] and they define which level of headers is being used for splitting (as an example, ["#"] splits the files only based on first headers, ["#","##","###"] splits them based on the first three headers. The smaller the pieces the less precise the answer is, and more tokens are used for each call, but higher chance of ChatGPT not being aware of the necessary context.
 gpt-model| Defines which ChatGPT model should be used.
 gpt_temperature| Defines ChatGPT's temperature - controls how predictable or creative the responses will be. Can be be set between 0.1 and 10, the smaller the number the less creative the response will be.
 gpt_developer_prompt|Defines what system context chatgpt will receive in every prompt. In general, prompt hierarchy is system > developer > assistant
 documentation_selector: s3 | Defines if files should be downloaded from s3 bucket. More details in documentation_sources. Needs following environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
 documentation_selector: innoveo_partner_hub | Defines if the content of Innoveo partner hub should be downloaded. *Currently disabled. Track it [here](https://github.com/pleszr/skyeGPT/issues/14).*
 s3_bucket| Name of the s3 bucket
s3_folder_prefix| Name of the folder inside the s3 bucket
s3_local_folder| Folder path where you want to save the files to.
api_endpoint| Defines the Confluence REST API endpoint to fetch content. For Innoveo Partner Hub, it should be set to "https://innoveo.atlassian.net/wiki/rest/api/content".
space_key| Specifies the Confluence space key from which to download content. For Innoveo Partner Hub, set this to "IPH".
save_path| Specifies the local folder path where the downloaded Innoveo Partner Hub content will be stored. For example, "content/innoveo-partner-hub". Use innoveo-partner-hub to set documentation source to iph which is required to generate links.
 

#### Sample json

```json 

```
### Asker{
   "chroma_parameters":{
      "collection_name":"SkyeDoc",
      "should_import":true,
      "folder_path":"content",
      "k_nearest_neighbors":4,
      "markdown_split_headers":[
         "#"
      ]
   },
   "gpt_parameters":{
      "gpt_model":"gpt-4o-mini",
      "gpt_temperature":0.1,
      "gpt_developer_prompt":"You are a support person working for a product organization called Innoveo. You are providing technical support to developers who are using a no-code platform called Innoveo Skye. You have access to manual of the product in the upcoming developer prompts. Your job is to help them find the relevant documentation by providing links to the documentation. If there are multiple relevant options, give multiple options. Only go above 200 tokens for an option when you are quoting the documentation. Refer everything from the lookup files, only refer to items which you are highly confident that it is accurate."
   },
   "documentation_selector":{
      "s3":false,
      "innoveo_partner_hub":false
   },
   "documentation_sources":{
      "s3":{
         "s3_bucket":"skyedoc",
         "s3_folder_prefix":"skye-10.0.0/",
         "s3_local_folder":"content/skyedoc"
      },
      "confluence":{
         "api_endpoint":"https://innoveo.atlassian.net/wiki/rest/api/content",
         "space_key":"IPH",
         "save_path":"content/innoveo-partner-hub"
      }
   }
}

## Assistant
The Assistant mode uses OpenAI's Assistant product. There are two major functions:
### Key details
- No need to implement conversation history or context management.
- Context lookup happens via OpenAI.
   - Pro: no need to implement it, works out of the box.
   - Con: it works as a blackbox, no way of fine-tuning it in case the results are dissatisfactory.
### Technical details
There are two major workflows, the Setup and the Asker. Setup needs to ran only 1x post deployment or can be used to change the defined parameters. Asker is where workflow for asking questions.
#### Diagram
![Alt text](readme_resources/assistant.png?raw=true "OpenAI Assistant Architecture & Workflow")
#### Parameters explained
|  Parameter| Purpose  |
|--|--|
assistant_name | Name of the assistant. If the assistant already exists, it will be used, otherwise a new assistant with this will be created.
assistant_instructions| With assistant, the instructions are given once for the assistant. This is very similar to the developer instructions in Chroma options. The weight is system prompt > assistant prompt > question prompt.
 gpt-model| Defines which ChatGPT model should be used.
existing_vector_store_id| Optional. If you want to re-use an existing vector_store_id (because you don't want to upload all files again) then set it, otherwise leave it empty.
new_vector_store_name| Name of the vector_store if you are creating a new. 
folder_path|the folder the application should scan for files to import. Use skyedoc to set documentation source to Skye which is required to generate links.
 file_extension| The extension of the files the application should find at during scanning.
  documentation_selector: s3 | Defines if files should be downloaded from s3 bucket. More details in documentation_sources. Needs following environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
 documentation_selector: innoveo_partner_hub | Defines if the content of Innoveo partner hub should be downloaded. *Currently disabled. Track it [here](https://github.com/pleszr/skyeGPT/issues/14).*
 s3_bucket| Name of the s3 bucket
s3_folder_prefix| Name of the folder inside the s3 bucket
s3_local_folder| Folder path where you want to save the files to. Use innoveo-partner-hub to set documentation source to iph which is required to generate links.

#### Sample JSON
```json 
{
   "assistant_properties":{
      "assistant_name":"SkyeGPT4",
      "assistant_instructions":"You are a support person working for a product organization called Innoveo. You are providing technical support to developers who are using a no-code platform called Innoveo Skye. Rely on the contextual files from the vector store for answers. Give short answers and always link the documentation where they can learn more. Refer everything from the lookup files, only refer to items which you are highly confident that it is accurate. If something is not answerable based on the documentation, don't hesitate to say that it is not possible according the documentation",
      "gpt-model":"gpt-4o-mini",
      "number_of_retries_for_assistant_answer":20,
      "temperature":0.1
   },
   "vector_store_properties":{
      "existing_vector_store_id":"vs_Uk6JClWkMHGgiwHOrCksGi4Q",
      "new_vector_store_name":"Skye 10 documentation",
      "folder_path":"content",
      "file_extension":"md"
   },
   "documentation_selector":{
      "s3":false,
      "innoveo_partner_hub":false
   },
   "documentation_sources":{
      "s3":{
         "s3_bucket":"skyedoc",
         "s3_folder_prefix":"skye-10.0.0/",
         "s3_local_folder":"content/skyedoc"
      },
      "confluence":{
         "api_endpoint":"https://innoveo.atlassian.net/wiki/rest/api/content",
         "space_key":"IPH",
         "save_path":"content/innoveo-partner-hub"
      }
   }
}
```


# How to host locally
1. check the /.env.example file and generate the /.env file based on it
2. go to root and execute docker-compose up

# Roadmap
Issues and plans can be tracked at https://github.com/users/pleszr/projects/4 

