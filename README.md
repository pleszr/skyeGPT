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

## Workflow

![Agentic RAG - SkyeGPT](https://raw.githubusercontent.com/pleszr/skyeGPT/refs/heads/main/readme_resources/agentic_rag_skyegpt.png)

For simplification, the workflow doesn't show but the conversations are stored and loaded from a document DB. The users can give feedback on the frontend which will be stored (and be queried) within the conversation documents

## Frontend

![SkyeGPT Frontend]([https://raw.githubusercontent.com/pleszr/skyeGPT/docs/%2363-rewrite-documentation-for-agentic-setup/readme_resources/skyegpt_frontend.png](https://github.com/pleszr/skyeGPT/blob/main/readme_resources/agentic_rag_skyegpt.png))

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

# Design considerations

- Follows standard layered architecture, API layer talks to services layer, which orcastrates the rest of functions which are divided by domain
- Every vendor is encapsulated as a separate layer, so changing Chroma or Mongo or even Pydantic-AI is easy
- For now, its two single-agent flow with both having single tools. The main LLM will receive few more tools. Plan is to migrate to a multi-agent solution (like LangGraph or crewAI) is once we reach 3-4 tools

# Roadmap

Issues and plans can be tracked at https://github.com/users/pleszr/projects/4
