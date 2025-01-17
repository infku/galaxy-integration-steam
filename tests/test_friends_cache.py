from unittest.mock import MagicMock

import pytest

from protocol.consts import EPersonaState
from protocol.types import UserInfo
from friends_cache import FriendsCache


@pytest.fixture
def cache():
    return FriendsCache()


@pytest.fixture
def added_handler(cache):
    mock = MagicMock()
    cache.added_handler = mock
    return mock


@pytest.fixture
def removed_handler(cache):
    mock = MagicMock()
    cache.removed_handler = mock
    return mock


@pytest.fixture
def updated_handler(cache):
    mock = MagicMock()
    cache.updated_handler = mock
    return mock


def test_empty(cache):
    assert not cache.ready
    assert list(cache) == []


def test_add_user(cache, added_handler):
    user_id = 1423
    cache.add(user_id)
    assert not cache.ready
    assert user_id in cache
    assert list(cache) == [(user_id, UserInfo())]
    added_handler.assert_not_called()


def test_update_user_not_ready(cache, added_handler, updated_handler):
    user_id = 1423
    user_info = UserInfo("Jan")
    cache.add(user_id)
    cache.update_info(user_id, user_info)
    assert not cache.ready
    assert list(cache) == [(user_id, user_info)]
    added_handler.assert_not_called()
    updated_handler.assert_not_called()


def test_update_user_ready(cache, added_handler, updated_handler):
    user_id = 1423
    expected_user_info = UserInfo(name="Jan", state=EPersonaState.Offline)
    cache.add(user_id)
    cache.update_info(user_id, UserInfo(name="Jan"))
    cache.update_info(user_id, UserInfo(state=EPersonaState.Offline))
    assert cache.ready
    assert list(cache) == [(user_id, expected_user_info)]
    added_handler.assert_called_with(user_id, expected_user_info)
    updated_handler.assert_not_called()


def test_update_user_all_data(cache, added_handler, updated_handler):
    user_id = 1423
    user_info = UserInfo(name="Jan", state=EPersonaState.Offline)
    cache.add(user_id)
    cache.update_info(user_id, user_info)
    assert cache.ready
    assert list(cache) == [(user_id, user_info)]
    added_handler.assert_called_with(user_id, user_info)
    updated_handler.assert_not_called()


def test_remove_not_ready_user(cache, removed_handler):
    user_id = 1423
    cache.add(user_id)
    cache.remove(user_id)
    assert cache.ready
    assert list(cache) == []
    removed_handler.assert_not_called()


def test_remove_ready_user(cache, removed_handler):
    user_id = 1423
    user_info = UserInfo(name="Jan", state=EPersonaState.Offline)
    cache.add(user_id)
    cache.update_info(user_id, user_info)
    cache.remove(user_id)
    assert list(cache) == []
    removed_handler.assert_called_once_with(user_id)


def test_reset_empty(cache):
    cache.reset([])
    assert cache.ready
    assert list(cache) == []


def test_reset_mixed(cache, removed_handler):
    cache.add(15)
    cache.update_info(15, UserInfo(name="Jan", state=EPersonaState.Offline))

    cache.add(17)
    cache.update_info(17, UserInfo(name="Ula", state=EPersonaState.Offline))

    cache.reset([17, 29])
    removed_handler.assert_called_once_with(15)
    assert not cache.ready
