from common import utils
import pytest
from tests import sample_objects, test_utils
from datetime import datetime, timezone, timedelta

from unittest.mock import patch

def test_convert_html_to_md_headings_and_paragraphs():
    # setup static data
    html = "<h1>Title</h1><p>First.</p><p>Second.</p>"
    # act
    md = utils.convert_html_to_md(html)
    # assert result
    lines = md.strip().splitlines()
    assert lines[0] == "# Title"
    assert any("First." in line for line in lines)
    assert any("Second." in line for line in lines)


def test_convert_html_to_md_formatting_and_links():
    # setup static data
    html = "<strong>Bold</strong> and <em>italic</em> with <a href=\"/link\">Link</a>"
    # act
    md = utils.convert_html_to_md(html)
    # assert result
    assert "**Bold**" in md
    assert "*italic*" in md
    assert "[Link](/link)" in md

def test_format_to_see_chunk():
    # setup static data
    raw_stream = sample_objects.raw_stream()
    # act
    formatted_stream_output = list(utils.format_stream_to_sse(raw_stream))
    # assert result
    expected = test_utils.convert_array_to_see(sample_objects.mock_chunks)
    assert formatted_stream_output==expected

@pytest.mark.asyncio
async def test_async_format_to_see_chunk():
    # setup static data
    raw_stream = sample_objects.async_raw_stream()
    # act
    actual = []
    formatted_stream=utils.async_format_to_sse(raw_stream)
    async for chunk in formatted_stream:
        actual.append(chunk)
    # assert result
    expected = test_utils.convert_array_to_see(sample_objects.mock_chunks)
    assert actual==expected

def test_replace_placeholders():
    # setup static
    template = "Hello, Mr. {{last_name}}"
    replace_values = {"last_name": "John"}
    # act
    expected_text = "Hello, Mr. John"
    actual_text = utils.replace_placeholders(template, replace_values)
    # assert result
    assert expected_text == actual_text



def test_folder_to_dict(tmp_path):

    # setup static data
    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()
    (tmp_path / "root.txt").write_text("hello root")
    (sub_dir / "inner.txt").write_text("hello inner")

    # act
    actual_tree = utils.folder_to_dict(str(tmp_path))

    # assert result
    expected_tree = {
        "name": tmp_path.name,
        "type": "folder",
        "children": [
            {
                "name": "sub",
                "type": "folder",
                "children": [
                    {"name": "inner.txt", "type": "file"},
                ],
            },
            {"name": "root.txt", "type": "file"},
        ],
    }
    #os.listdir doesn't have a guaranteed order. if you face issues with it sort the tree on both actual and expected
    assert test_utils._sort_tree(actual_tree) == test_utils._sort_tree(expected_tree)


def test_generate_local_folder_path_from_skye_version(monkeypatch):
    # setup static
    template = "/docs/v{{skye_major_version}}"
    # setup mock
    monkeypatch.setattr(utils.constants, "SKYE_DOC_LOCAL_FOLDER_LOCATION_TEMPLATE", template, raising=False)
    # act
    actual_path = utils.generate_local_folder_path_from_skye_version("5")
    # assert result
    expected_path = "/docs/v5"
    assert actual_path == expected_path


@patch("common.utils.datetime")
def test_calculate_utc_x_hours_ago(mock_datetime):
    # setup static
    x_hours = 3
    #setup mocks
    fixed_now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    mock_datetime.now.return_value = fixed_now
    mock_datetime.timezone = timezone  # ensure timezone attribute is available

    # act
    result = utils.calculate_utc_x_hours_ago(x_hours)

    # assert result
    expected = fixed_now - timedelta(hours=x_hours)
    assert result == expected
