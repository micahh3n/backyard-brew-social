from unittest.mock import patch

import meta_client


def test_recent_page_posts_returns_messages_only():
    fake_response = {"data": [{"message": "Bingo's back!"}, {"id": "123"}, {"message": "Poker night."}]}
    with patch("meta_client._page_id", return_value="123"), \
         patch("meta_client._get", return_value=fake_response):
        result = meta_client.recent_page_posts(limit=6)
    assert result == ["Bingo's back!", "Poker night."]


def test_recent_page_posts_returns_empty_on_failure():
    with patch("meta_client._get", side_effect=meta_client.MetaError("boom")):
        result = meta_client.recent_page_posts(limit=6)
    assert result == []
