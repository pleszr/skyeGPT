"""Launches SkyeGPT."""

from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
from apis import asker_apis_router  # noqa: E402
from apis import setup_apis_router  # noqa: E402
from apis import evaluator_apis_router  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
import signal  # noqa: E402


app = FastAPI(
    title="SkyeGPT API",
    description="SkyeGPT's backend APIs which allows to scrape information and upload to database and then query it",
    version="0.1.0",
)
app.include_router(asker_apis_router)
app.include_router(setup_apis_router)
app.include_router(evaluator_apis_router)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)


def _exit_gracefully(signum, _frame):
    print(f"Received signal {signum}, saving settings before exit...")
    exit(0)


signal.signal(signal.SIGTERM, _exit_gracefully)
signal.signal(signal.SIGINT, _exit_gracefully)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
