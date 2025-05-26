import pytest
from agentic.conversation import Conversation
from tests import sample_objects
from datetime import datetime, timezone
from common import constants, message_bundle
from agentic.feedback import Feedback
from pydantic_ai.messages import ModelRequest

def test_create_copy_generates_new_id_but_preserves_content_and_feedback():
    # setup static data
    original = sample_objects.sample_conversation

    # act
    copy = original.create_copy()

    # assert result
    assert copy.conversation_id != original.conversation_id
    assert copy.contents == original.contents
    assert copy.feedbacks == original.feedbacks


def test_get_content_as_list_returns_copy():
    # setup static data
    original = sample_objects.sample_conversation

    # act
    content_list = original.get_content_as_list()

    # assert result
    assert isinstance(content_list, list)
    assert content_list == original.contents
    content_list.append("dummy")
    assert content_list != original.contents


def test_extend_appends_content_and_updates_last_modified():
    # setup static data
    original_content = list(sample_objects.sample_conversation.contents)
    ts_before = datetime(2025, 1, 1, tzinfo=timezone.utc)

    base = sample_objects.sample_conversation.model_copy(update={
        "contents": original_content,
        "last_modified": ts_before
    })
    incoming = sample_objects.sample_conversation.model_copy(update={
        "contents": list(sample_objects.sample_conversation.contents)
    })

    # act
    len_before = len(base.contents)
    last_mod_before = base.last_modified
    base.extend(incoming)

    # assert result
    assert len(base.contents) == len_before + len(incoming.contents)
    assert base.last_modified > last_mod_before


def test_extend_trims_when_exceeding_max_length(monkeypatch):
    # setup static data
    monkeypatch.setattr(constants, "MAX_CONVERSATION_LENGTH", 2)
    ts_before = datetime(2025, 1, 1, tzinfo=timezone.utc)

    base = sample_objects.sample_conversation.model_copy(update={
        "contents": list(sample_objects.sample_conversation.contents),
        "last_modified": ts_before
    })

    incoming = sample_objects.sample_conversation.model_copy(update={
        "contents": list(sample_objects.sample_conversation.contents)
    })

    # act
    base.extend(incoming)

    # assert result
    assert len(base.contents) == constants.MAX_CONVERSATION_LENGTH


def test_add_feedback_appends_to_list():
    # setup static data
    conv = Conversation(feedbacks=[])
    fb = Feedback(vote="positive", comment="Looks good")

    # act
    conv.add_feedback(fb)

    # assert result
    assert conv.feedbacks == [fb]


ARCHIVED = {"tool_output": "content archived for space saving purposes"}


def make_content(parts, usage=None):
    c = {"parts": parts.copy()}
    if usage is not None:
        c["usage"] = usage.copy()
    return c


def test_trim_conversation_content_archives_tool_output():
    # create static objects
    test_conversation = sample_objects.sample_conversation
    # assert setup
    assert hasattr(test_conversation.contents[2], "parts")
    assert hasattr(test_conversation.contents[2].parts[0], "tool_name")
    assert hasattr(test_conversation.contents[2].parts[0], "content")
    assert test_conversation.contents[2].parts[0].content != message_bundle.CONTENT_ARCHIVED_MESSAGE
    # act
    test_conversation.archive_tool_output()
    # assert result
    assert test_conversation.contents[2].parts[0].content == message_bundle.CONTENT_ARCHIVED_MESSAGE






