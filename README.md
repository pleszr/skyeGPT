# Purpose

SkyeGPT is an agentic RAG application for the talk to your document use-case. It will use the imported documentation to answer the questions. It aims to spare time for the user by finding and reporting information quickly and efficiently.

The application has two major components:

- a data digestor which allows the admins to download documentation from various places (current supports public confluence spaces and markdowns stored in S3 bucket). This is today taylor-made to work with documents related to Innoveo Skye.
- the agentic RAG itself, which is documentation-agnostic and will work with any documents uploaded. 

# Behind the scenes

## Exec summary

- Backend is written in python
  - uses Pydantic AI for LLM management
  - uses FastAPI (with OpenAPI documentation) for APIs
  - uses DeepEval for LLM and response quality evaluator
  - uses ChromaDB for vector db and mongo for document db
- Frontend
  - Simple lightweight Next.js app

## How to use

### Run locally

- there is a docker-compose on the root
- the backend has a .env.example file in backend root, make sure all are filled

### Once it runs

The recommended way is to use /docs (likely at [http://localhost:8000](http://localhost:8000/)) to communicate with the app. Recommended sequence is to 

1. /setup/data/skye-documentation to download Skye documentation
2. /setup/data/innoveo-partner-hub to download Innoveo Partner Hub content
3. /setup/import to import downloaded content to vector db
4. For response generation, use
   1. /ask/response/stream for stream
   2. /evaluate/response for non-stream (this also returns the returned context from the tool)

# Roadmap

Issues and plans can be tracked at https://github.com/users/pleszr/projects/4
