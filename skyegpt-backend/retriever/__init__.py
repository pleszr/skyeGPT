# Without this im getting this
# Traceback (most recent call last):
#   File "/mnt/c/Users/CsabaSallai/Desktop/new-skye-gpt/skyeGPT/skyegpt-backend/main.py", line 4, in <module>
#     from apis import asker_apis_router  # noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/mnt/c/Users/CsabaSallai/Desktop/new-skye-gpt/skyeGPT/skyegpt-backend/apis/__init__.py", line 1, in <module>
#     from .asker_apis import asker_apis_router
#   File "/mnt/c/Users/CsabaSallai/Desktop/new-skye-gpt/skyeGPT/skyegpt-backend/apis/asker_apis.py", line 6, in <module>
#     from dependencies import (AgentResponseStreamingService, get_agent_response_stream_service,
#   File "/mnt/c/Users/CsabaSallai/Desktop/new-skye-gpt/skyeGPT/skyegpt-backend/dependencies.py", line 1, in <module>
#     from services.setup_services import IngestionService, DatabaseService
#   File "/mnt/c/Users/CsabaSallai/Desktop/new-skye-gpt/skyeGPT/skyegpt-backend/services/setup_services.py", line 4, in <module>
#     from retriever import db_client
# ImportError: cannot import name 'db_client' from 'retriever' (/mnt/c/Users/CsabaSallai/Desktop/new-skye-gpt/skyeGPT/skyegpt-backend/retriever/__init__.py)

from .db import db_client