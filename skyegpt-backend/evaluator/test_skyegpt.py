from typing import List, Dict
import pytest
import json
import deepeval
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import (
    GEval,
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    BaseMetric
)
from deepeval.dataset import EvaluationDataset
from dotenv import load_dotenv
from evaluator import evaluator_utils
from evaluator.llm_wrapper import query_llm

LLM_ENDPOINT: str = 'http://localhost:8000/test_askPydantic'
DATA_DIRECTORY: str = 'evaluator/test_data'
QUESTION_BANK_FILE: str = 'QuestionBank.csv'
GPT_MODEL: str = 'gpt-4o'

RELEVANCY_THRESHOLD: float = 0.5
FAITHFULNESS_THRESHOLD: float = 0.7
ACTUAL_EXPECTED_OUTPUT_QUALITY_THRESHOLD: float = 0.6
CONTEXT_RELEVANCY_THRESHOLD: float = 0.5


def create_dataset() -> EvaluationDataset:
    load_dotenv()

    raw_test_cases = load_raw_dataset()
    prepared_test_cases = []
    for raw_test_case in raw_test_cases:
        prepared_test_case = prepare_test_case_with_llm_response(raw_test_case)
        prepared_test_cases.append(prepared_test_case)
    return EvaluationDataset(test_cases=prepared_test_cases)


def load_raw_dataset() -> List[Dict[str, str]]:
    return evaluator_utils.create_dict_from_csv(DATA_DIRECTORY, QUESTION_BANK_FILE)


def prepare_test_case_with_llm_response(test_case_data: Dict[str, str]) -> LLMTestCase:
    question = test_case_data["question"]
    expected_output = test_case_data["reference_answer"]

    api_response = query_llm(LLM_ENDPOINT, question)
    test_case = LLMTestCase(
        input=question,
        context=test_case_data["reference_context"].split('§§'),
        actual_output=api_response.get("generated_answer"),
        expected_output=expected_output,
        retrieval_context=convert_context_to_list_str(api_response.get('curr_context'))
    )
    return test_case


def convert_context_to_list_str(curr_context: dict) -> list[str]:
    if not curr_context or not isinstance(curr_context, dict):
        print("Warning: convert_context_to_list_str received None or invalid input.")
        return []
    result_list = []
    tool_args = json.loads(curr_context["tool_args"])
    result_list.append(f"Query: {tool_args.get('query', '')}")

    tool_result = json.loads(curr_context["tool_result"])

    for doc in tool_result.get("documents", [[]])[0]:
        result_list.append(f"Document: {doc}")

    for meta in tool_result.get("metadatas", [[]])[0]:
        link = meta.get("documentation_link")
        if link:
            result_list.append(f"Link: {link}")
    return result_list


def create_evaluation_metrics() -> List[BaseMetric]:
    return [
        FaithfulnessMetric(
            threshold=FAITHFULNESS_THRESHOLD,
            model=GPT_MODEL,
            include_reason=True
        ),
        AnswerRelevancyMetric(
            threshold=RELEVANCY_THRESHOLD,
            model=GPT_MODEL
        ),
        GEval(
            name="Context Relevancy",
            criteria=(
                "You are testing the retriever part of the application. "
                "CONTEXT contains the reference context for the application, "
                "RETRIEVAL_CONTEXT contains the actual context. "
                "RETRIEVAL_CONTEXT will contain significantly more information which is not a problem."
                "RETRIEVAL_CONTEXT is expected to contain a link"
            ),
            evaluation_params=[LLMTestCaseParams.CONTEXT, LLMTestCaseParams.RETRIEVAL_CONTEXT],
            threshold=CONTEXT_RELEVANCY_THRESHOLD,
            model=GPT_MODEL
        ),
        GEval(
            name="Actual output/expected output quality",
            criteria=(
                "Determine how close the ACTUAL OUTPUT is to the EXPECTED OUTPUT"
                "ACTUAL OUTPUT is expected to share a link to documentation"
                "Having more information is acceptable. Having contradicting information is NOT acceptable"
            ),
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
            threshold=ACTUAL_EXPECTED_OUTPUT_QUALITY_THRESHOLD,
            model=GPT_MODEL
        )
    ]


dataset = create_dataset()
evaluation_metrics = create_evaluation_metrics()


@pytest.mark.parametrize("test_case", dataset)
def test_customer_chatbot(test_case: LLMTestCase) -> None:
    assert_test(test_case, evaluation_metrics)


@deepeval.on_test_run_end
def function_to_be_called_after_test_run() -> None:
    print("Test finished!")
    result_file = evaluator_utils.rename_deepeval_output_to_json()
    if result_file is not None:
        evaluator_utils.aggregate_test_metrics(result_file)
