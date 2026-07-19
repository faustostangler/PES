import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Since pytest will run from the root directory, let's ensure we can import downloader and sync_channels.
# The pyproject.toml adds 'playground/isb.ai' to pyright extraPaths, and we should be able to import directly
# if the current working directory includes it or if we append it to sys.path.
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import downloader
import sync_channels

@patch("downloader.yt_dlp.YoutubeDL")
def test_extract_video_metadata_success_without_cookies(mock_ytdl_class):
    """Should successfully fetch metadata on the first try without using cookies."""
    mock_instance = MagicMock()
    mock_ytdl_class.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = {"id": "test_id", "title": "Test Title"}

    url = "https://www.youtube.com/watch?v=test_id"
    result = downloader.extract_video_metadata(url)

    assert result == {"id": "test_id", "title": "Test Title"}
    # Verify YoutubeDL was instantiated only once and without cookies
    mock_ytdl_class.assert_called_once()
    opts = mock_ytdl_class.call_args[0][0]
    assert "cookiesfrombrowser" not in opts

@patch("downloader.yt_dlp.YoutubeDL")
def test_extract_video_metadata_fallback_to_cookies(mock_ytdl_class):
    """Should fallback to using cookies when the first attempt without cookies fails."""
    mock_instance_no_cookies = MagicMock()
    mock_instance_no_cookies.extract_info.side_effect = Exception("HTTP Error 403: Forbidden")
    
    mock_instance_with_cookies = MagicMock()
    mock_instance_with_cookies.extract_info.return_value = {"id": "test_id", "title": "Test Title"}
    
    # Configure the mock to return different instances/contexts for successive calls
    mock_ytdl_class.return_value.__enter__.side_effect = [
        mock_instance_no_cookies,
        mock_instance_with_cookies
    ]

    url = "https://www.youtube.com/watch?v=test_id"
    result = downloader.extract_video_metadata(url)

    assert result == {"id": "test_id", "title": "Test Title"}
    
    # Assert YoutubeDL was instantiated exactly twice
    assert mock_ytdl_class.call_count == 2
    
    # First call: no cookies
    first_opts = mock_ytdl_class.call_args_list[0][0][0]
    assert "cookiesfrombrowser" not in first_opts
    
    # Second call: Chrome cookies enabled
    second_opts = mock_ytdl_class.call_args_list[1][0][0]
    assert second_opts["cookiesfrombrowser"] == ("chrome",)

@patch("downloader.yt_dlp.YoutubeDL")
def test_extract_video_metadata_ultimate_failure(mock_ytdl_class):
    """Should raise the exception if both attempts (without and with cookies) fail."""
    mock_instance = MagicMock()
    mock_instance.extract_info.side_effect = Exception("Network Error")
    mock_ytdl_class.return_value.__enter__.return_value = mock_instance

    url = "https://www.youtube.com/watch?v=test_id"
    with pytest.raises(Exception, match="Network Error"):
        downloader.extract_video_metadata(url)
        
    assert mock_ytdl_class.call_count == 2

@patch("downloader.yt_dlp.YoutubeDL")
def test_download_audio_as_ogg_fallback_to_cookies(mock_ytdl_class):
    """Should fallback to Chrome cookies if download fails without them."""
    mock_instance_no_cookies = MagicMock()
    mock_instance_no_cookies.extract_info.side_effect = Exception("Sign in required")
    
    mock_instance_with_cookies = MagicMock()
    
    mock_ytdl_class.return_value.__enter__.side_effect = [
        mock_instance_no_cookies,
        mock_instance_with_cookies
    ]

    url = "https://www.youtube.com/watch?v=test_id"
    output_dir = Path("/tmp")
    video_id = "test_id"
    
    result = downloader.download_audio_as_ogg(url, output_dir, video_id)
    
    assert result == Path("/tmp/test_id.ogg").resolve()
    assert mock_ytdl_class.call_count == 2
    
    # Assert second attempt used cookies
    second_opts = mock_ytdl_class.call_args_list[1][0][0]
    assert second_opts["cookiesfrombrowser"] == ("chrome",)

@patch("sync_channels.yt_dlp.YoutubeDL")
def test_fetch_channel_recent_videos_fallback_to_cookies(mock_ytdl_class):
    """Should fallback to Chrome cookies if channel video list extraction fails without them."""
    mock_instance_no_cookies = MagicMock()
    mock_instance_no_cookies.extract_info.side_effect = Exception("Blocked by YouTube")
    
    mock_instance_with_cookies = MagicMock()
    mock_instance_with_cookies.extract_info.return_value = {
        "entries": [{"id": "vid1", "url": "url1"}]
    }
    
    mock_ytdl_class.return_value.__enter__.side_effect = [
        mock_instance_no_cookies,
        mock_instance_with_cookies
    ]
    
    result = sync_channels.fetch_channel_recent_videos("UC12345", limit=5)
    
    assert len(result) == 1
    assert result[0]["id"] == "vid1"
    assert mock_ytdl_class.call_count == 2
    
    # Assert second attempt used cookies
    second_opts = mock_ytdl_class.call_args_list[1][0][0]
    assert second_opts["cookiesfrombrowser"] == ("chrome",)
