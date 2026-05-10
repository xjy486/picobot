"""Session 模块单元测试。"""
from __future__ import annotations

from pathlib import Path

from session.manager import Session, SessionManager


def test_get_history_truncates_to_max_messages():
    session = Session(key="cli:direct")
    session.messages = [{"role": "user", "content": str(i)} for i in range(10)]
    history = session.get_history(max_messages=3)
    assert len(history) == 3
    assert history[0]["content"] == "7"


def test_get_history_aligns_to_first_user_role():
    session = Session(
        key="cli:direct",
        messages=[
            {"role": "tool", "tool_call_id": "x", "content": "tool result"},
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"},
        ],
    )
    history = session.get_history(max_messages=10)
    assert history[0]["role"] == "user"
    assert len(history) == 2


def test_session_manager_persists_and_reloads(tmp_path: Path):
    manager = SessionManager(tmp_path)
    session = manager.get_or_create("cli:direct")
    session.messages = [{"role": "user", "content": "你好"}]
    manager.save(session)

    fresh = SessionManager(tmp_path)
    reloaded = fresh.get_or_create("cli:direct")
    assert reloaded.messages == [{"role": "user", "content": "你好"}]


def test_session_manager_caches_in_memory(tmp_path: Path):
    manager = SessionManager(tmp_path)
    a = manager.get_or_create("cli:direct")
    b = manager.get_or_create("cli:direct")
    assert a is b


def test_session_key_with_colon_safely_persisted(tmp_path: Path):
    manager = SessionManager(tmp_path)
    session = manager.get_or_create("telegram:1234")
    session.messages = [{"role": "user", "content": "x"}]
    manager.save(session)
    files = list((tmp_path / "sessions").iterdir())
    assert all(":" not in f.name for f in files)
    assert any("telegram_1234" in f.name for f in files)
