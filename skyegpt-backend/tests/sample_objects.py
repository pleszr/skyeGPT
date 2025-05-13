from agentic.feedback import Feedback
from agentic.conversation import Conversation
from datetime import datetime
import uuid

sample_uuid = uuid.UUID("db5008a7-432f-4b4e-985d-bdb07cdcc65e")

sample_conversation_feedback = Feedback(
    id=uuid.UUID("9ea036ea-d491-4987-ab89-d253cce78832"),
    vote="positive",
    comment="This was clearly false, the links are directing me to innoveo.skye.com/docs",
    created_at=datetime.fromisoformat("2025-05-12T18:15:19.104000")
)

sample_conversation_content = [
    {
        "parts": [
            {
                "content": "\n    You are an agent whose job is to answer questions based the documentation of the Innoveo Skye or related documents. \n    Use your tools to check the documentation. User's question: Does Skye support SOAP API?\n    ",
                "timestamp": "2025-05-12T18:11:14.135000",
                "part_kind": "user-prompt"
            }
        ],
        "instructions": "You are an agent - please keep going until the user’s query is completely resolved, \n                 before ending your turn and yielding back to the user. Only terminate your turn when you are sure \n                 that the problem is solved.\"\n                 You should ALWAYS use your tools to answer. Your job is to respond based on the files documentation \n                 you have access to via tools. do NOT guess or make up an answer.\n                 \n                 # Workflow\n\n                 ## High-Level Problem Solving Strategy\n                 \n                 1. Analyze the question the user asked. Carefully read the option and think through what is the intent \n                 behind the user's question. Check the message history for more context.\n                 2. Once you have a good understanding about the user's question and it's intent, review your tools \n                 and decide which tools to use and with what parameters.\n                 3. Use your tools.\n                 4. Evaluate if your the results that you got from your tools provide enough clarity for you to \n                 answer the question. \n                 5. Use your tools again if the results were not satisfactory.\n                 6. If none of your tools gave any response that is relevant to the user's question, admit that you did \n                 not find relevant documents. Do NOT guess or make up an answer.\n                 7. Answer the question. Be brief and aim to give a link to the documentation where the user can \n                 followup for more details.\n                 ",
        "kind": "request"
    },
    {
        "parts": [
            {
                "tool_name": "search_in_skye_documentation",
                "args": "{\"query\":\"Does Skye support SOAP API?\"}",
                "tool_call_id": "call_7GrxOBQ7b0eKgFVf9Hp45tn9",
                "part_kind": "tool-call"
            }
        ],
        "model_name": "gpt-4.1",
        "timestamp": "2025-05-12T18:11:15",
        "kind": "response"
    }]

sample_conversation = Conversation(
    conversation_id=sample_uuid,
    feedbacks=[sample_conversation_feedback],
    content=sample_conversation_content
)
