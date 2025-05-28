import glob
import csv
import os
import json
import statistics
from typing import Any
from datetime import datetime


def rename_deepeval_output_to_json() -> str:
    results_dir = os.getenv("DEEPEVAL_RESULTS_FOLDER", "./evaluator/deepeval_results")
    latest_file = _find_latest_file_in_directory(results_dir)
    new_path = _generate_new_report_name(results_dir)

    os.rename(latest_file, new_path)
    print(f"Results file renamed from {latest_file} to {new_path}")

    return new_path


def _find_latest_file_in_directory(directory: str) -> str:
    all_files = _scan_directory_for_files(directory)
    latest_file = _find_latest_file(all_files)
    return latest_file


def _scan_directory_for_files(directory: str) -> list[str]:
    all_files = glob.glob(f"{directory}/*")
    if not all_files:
        raise Exception(f"Error: No files found in {directory}")
    return all_files


def _find_latest_file(files: list[str]) -> str:
    latest_file = max(files, key=os.path.getctime)
    if not os.path.isfile(latest_file):
        raise Exception("Latest file is not a file")
    return latest_file


def _generate_new_report_name(directory: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d--%H-%M")
    new_file_name = f"deepeval_result_{timestamp}.json"
    return os.path.join(directory, new_file_name)


def create_dict_from_csv(folder_path: str, file_name: str) -> list[dict[str, str]]:
    file_path = os.path.join(folder_path, file_name)
    dict_from_csv = []

    with open(file_path, "r", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            dict_from_csv.append(dict(row))

    print(f"Successfully loaded {len(dict_from_csv)} rows from {file_path} file.")
    return dict_from_csv


def aggregate_test_metrics(file_path: str) -> None:
    test_cases = _extract_test_results_from_file(file_path)
    aggregated_metrics = _prepare_aggregated_metrics(test_cases)
    _save_results_to_file(aggregated_metrics, file_path)


def _extract_test_results_from_file(file_path: str) -> list[dict[str, Any]]:
    with open(file_path, "r") as f:
        data = json.load(f)
    return data.get("testCases", [])


def _prepare_aggregated_metrics(test_cases: list[dict[str, Any]]) -> dict:
    overall_success_rate = _calculate_overall_success_rate(test_cases)
    metrics = _gather_metric_names_and_scores(test_cases)
    aggregated_metrics = _calculate_aggregated_metric_scores(metrics)
    return merge_results(overall_success_rate, aggregated_metrics)


def _calculate_overall_success_rate(test_cases: list[dict[str, Any]]) -> dict:
    successful_tests = sum(1 for test in test_cases if test.get("success", False))
    number_of_tests = len(test_cases)
    overall_cost = sum(test_case.get("evaluationCost", 0) for test_case in test_cases)
    return {
        "number_of_tests": number_of_tests,
        "successful_tests": successful_tests,
        "failed_tests": number_of_tests - successful_tests,
        "overall_cost": overall_cost,
    }


def _gather_metric_names_and_scores(test_cases: list[dict[str, Any]]) -> dict:
    metrics = {}
    for test in test_cases:
        for metric in test.get("metricsData", []):
            metric_name = metric.get("name", "")
            if metric_name not in metrics:
                metrics[metric_name] = []

            metrics[metric_name].append({"score": metric.get("score", 0), "success": metric.get("success", False)})
    return metrics


def _calculate_aggregated_metric_scores(metrics: dict) -> dict:
    results = {"metrics": {}}
    for metric_name, metric_results in metrics.items():
        total_metric_tests = len(metric_results)
        successful_metric_tests = sum(1 for metric_result in metric_results if metric_result.get("success", False))

        scores = [metric_result.get("score", 0) for metric_result in metric_results]
        average_score = statistics.mean(scores) if scores else 0

        results["metrics"][metric_name] = {
            "aggregated_ratio": round(average_score, 2),
            "success_rate": f"{successful_metric_tests}/{total_metric_tests}",
        }
    return results


def merge_results(overall_success_rate: dict, aggregated_metrics: dict) -> dict:
    return {**overall_success_rate, **aggregated_metrics}


def _save_results_to_file(results: dict, file_path: str) -> None:
    output_path = _generate_new_file_name(file_path)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output_path}")


def _generate_new_file_name(file_path: str) -> str:
    file_name_parts = file_path.rsplit(".", 1)
    if len(file_name_parts) > 1:
        return f"{file_name_parts[0]}_aggregated.{file_name_parts[1]}"
    else:
        return f"{file_path}_aggregated"
