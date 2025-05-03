from fastapi import APIRouter, Body
import agentic.RagPipeline as RagPipeline
import agentic.PydanticAi as PydanticAi

test_apis_router = APIRouter()


@test_apis_router.post("/test_askPydantic")
async def test_ask_pydantic(request: dict = Body(...)):
    conversation_id = request["conversation_id"]
    question = request["question"]

    full_response = ""
    async for chunk in PydanticAi.ask_gemini(question, conversation_id):
        full_response += chunk

    nested_context = PydanticAi.current_context_store.get(conversation_id)

    response = {"generated_answer": full_response,
                "curr_context": nested_context
                }
    print(f"response: {response}")
    return response


@test_apis_router.post("/test_askChroma")
async def test_ask_chroma(request: dict = Body(...)):
    conversation_id = request["conversation_id"]
    question = request["question"]

    full_response = ""
    for chunk in RagPipeline.ask_gpt_using_rag_pipeline(question, conversation_id):
        full_response += chunk
    nested_context = RagPipeline.current_context_store[conversation_id]["documents"]
    flattened_context = []
    if nested_context and isinstance(nested_context, list):
        # Extract all strings from the nested structure
        for sublist in nested_context:
            if isinstance(sublist, list):
                flattened_context.extend(sublist)
            else:
                flattened_context.append(sublist)

    response = {"generated_answer": full_response,
                "curr_context": flattened_context
                }
    print(f"response: {response}")
    return response


@test_apis_router.post("/playground")
async def ask_chroma(request: dict = Body(...)):
    question = request["question"]
    conversation_id = request["conversation_id"]
    response = ''
    generator = PydanticAi.ask_gemini(question, conversation_id)
    async for token in generator:
        response += token
    return response
