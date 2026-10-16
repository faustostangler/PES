"""Unit tests for YouTube cookie extraction adapter and CLI subcommand."""

from __future__ import annotations

import http.cookiejar
import io
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, call, patch

from cresmo.infrastructure.adapters import cookie_extractor
from cresmo.infrastructure.adapters.cookie_extractor import (
    AUTH_COOKIE_NAMES,
    COOKIE_NAME_REGEX,
    COOKIE_VALUE_REGEX,
    DEFAULT_TARGET_DOMAINS,
    IGNORED_SUBDOMAINS,
    MAX_COOKIE_EXPIRY,
    MAX_COOKIE_NAME_LENGTH,
    MAX_COOKIE_VALUE_LENGTH,
    MIN_COOKIE_FILE_BYTES,
    SUPPORTED_BROWSERS,
    _extract_raw_cookies,
    _is_valid_cookie,
    _sanitize_cookie,
    ensure_cookies_file,
    export_cookies_auto,
    export_cookies_from_browser,
    has_valid_auth_cookies,
)
from cresmo.presentation.cli import main
from cresmo.presentation.exit_codes import EXIT_INGESTION_ERROR, EXIT_SUCCESS


def make_cookie(
    name: str = "SID",
    value: str = "sample_session_token_123",
    domain: str = ".youtube.com",
    expires: int | None = 2147483647,
    path: str = "/",
) -> http.cookiejar.Cookie:
    """Helper to instantiate valid http.cookiejar.Cookie instances."""
    return http.cookiejar.Cookie(
        version=0,
        name=name,
        value=value,
        port=None,
        port_specified=False,
        domain=domain,
        domain_specified=True,
        domain_initial_dot=domain.startswith("."),
        path=path,
        path_specified=True,
        secure=True,
        expires=expires,
        discard=False,
        comment=None,
        comment_url=None,
        rest={},
    )


class TestCookieExtractorConstants:
    """Verifies invariant security and formatting limits in cookie_extractor."""

    def test_constants_values(self) -> None:
        assert MIN_COOKIE_FILE_BYTES == 50
        assert MAX_COOKIE_NAME_LENGTH == 200
        assert MAX_COOKIE_VALUE_LENGTH == 2000
        assert MAX_COOKIE_EXPIRY == 2147483647
        assert DEFAULT_TARGET_DOMAINS == ("youtube.com", "google.com", "ytimg.com")
        assert "firefox" in SUPPORTED_BROWSERS
        assert "takeout" in IGNORED_SUBDOMAINS
        assert "SID" in AUTH_COOKIE_NAMES
        assert bool(COOKIE_NAME_REGEX.match("VALID-NAME_1"))
        assert not bool(COOKIE_NAME_REGEX.match("INVALID NAME"))
        assert bool(COOKIE_VALUE_REGEX.match("VALID VALUE 123"))
        assert not bool(COOKIE_VALUE_REGEX.match("INVALID\nVALUE"))


class TestCookieExtractorValidation:
    """Validate Netscape cookie validation and extraction behavior."""

    def test_has_valid_auth_cookies_returns_false_for_missing_or_empty_file(
        self, tmp_path: Path
    ) -> None:
        missing_file = tmp_path / "non_existent.txt"
        assert not has_valid_auth_cookies(missing_file)

        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("too short")
        assert not has_valid_auth_cookies(empty_file)

    def test_has_valid_auth_cookies_threshold_and_tokens(self, tmp_path: Path) -> None:
        # File with exact boundary: 49 bytes with auth token fails minimum bytes check
        short_file = tmp_path / "short.txt"
        short_file.write_text(".youtube.com\tTRUE\t/\tTRUE\t2147483647\tSID\t123456789")
        assert len(short_file.read_bytes()) < MIN_COOKIE_FILE_BYTES
        assert not has_valid_auth_cookies(short_file)

        # File with exactly 50 bytes and auth token
        exact_50_file = tmp_path / "exact_50.txt"
        content_50 = "A" * (50 - len("\tSID\t")) + "\tSID\t"
        exact_50_file.write_text(content_50)
        assert len(exact_50_file.read_bytes()) == 50
        assert has_valid_auth_cookies(exact_50_file)

        # Verify read_text call kwargs with exact utf-8 and ignore
        class MockCookieFile:
            def exists(self) -> bool:
                return True

            def stat(self) -> Any:
                m = MagicMock()
                m.st_size = 100
                return m

            def read_text(self, *args: Any, **kwargs: Any) -> str:
                assert kwargs.get("encoding") == "utf-8"
                assert kwargs.get("errors") == "ignore"
                return "\tSID\t"

        assert has_valid_auth_cookies(MockCookieFile())  # type: ignore[arg-type]

        # File with > 50 bytes and token
        valid_file = tmp_path / "valid.txt"
        header = "# Netscape HTTP Cookie File\n"
        row = ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tSID\tsample_session_token\n"
        valid_file.write_text(header + row)
        assert len(valid_file.read_bytes()) >= MIN_COOKIE_FILE_BYTES
        assert has_valid_auth_cookies(valid_file)

        # Verify token matching at the end of file (endswith \tTOKEN)
        end_token_file = tmp_path / "end_token.txt"
        end_content = header + ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tLOGIN_INFO"
        end_token_file.write_text(end_content)
        assert has_valid_auth_cookies(end_token_file)

        # Verify each auth token in AUTH_COOKIE_NAMES
        for token in AUTH_COOKIE_NAMES:
            t_file = tmp_path / f"token_{token}.txt"
            t_file.write_text(header + f".youtube.com\tTRUE\t/\tTRUE\t2147483647\t{token}\tval\n")
            assert has_valid_auth_cookies(t_file), f"Expected token {token} to be valid"

    def test_has_valid_auth_cookies_returns_false_if_no_auth_tokens(self, tmp_path: Path) -> None:
        guest_cookie_file = tmp_path / "guest_cookies.txt"
        lines = [
            "# Netscape HTTP Cookie File",
            ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tPREF\tf1=50000000",
            ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tYSC\txyz12345",
        ]
        guest_cookie_file.write_text("\n".join(lines))
        assert not has_valid_auth_cookies(guest_cookie_file)

    def test_has_valid_auth_cookies_handles_oserror(self, tmp_path: Path) -> None:
        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text("x" * 100)
        with patch.object(Path, "read_text", side_effect=OSError("Read error")):
            assert not has_valid_auth_cookies(cookie_file)

    def test_is_valid_cookie_filters(self) -> None:
        domains = ("youtube.com", "google.com")

        # Valid cookie
        c_ok = make_cookie(name="SID", value="valid", domain=".youtube.com")
        assert _is_valid_cookie(c_ok, domains)

        # Domain not ending with allowed domains
        c_bad_domain = make_cookie(name="SID", value="valid", domain=".attacker.com")
        assert not _is_valid_cookie(c_bad_domain, domains)

        # None domain
        c_none_domain = make_cookie(name="SID", value="valid", domain="")
        c_none_domain.domain = None  # type: ignore[assignment]
        assert not _is_valid_cookie(c_none_domain, ("xxxx", "youtube.com"))

        # Ignored subdomain (docs.google.com, mail.google.com)
        c_docs = make_cookie(name="SID", value="valid", domain="docs.google.com")
        assert not _is_valid_cookie(c_docs, domains)

        # Missing name or value
        c_no_name = make_cookie(name="", value="val")
        assert not _is_valid_cookie(c_no_name, domains)

        c_no_val = make_cookie(name="SID", value="")
        assert not _is_valid_cookie(c_no_val, domains)

        c_none_val = make_cookie(name="SID", value="dummy")
        c_none_val.value = None  # type: ignore[assignment]
        assert not _is_valid_cookie(c_none_val, domains)

        c_ws_val = make_cookie(name="SID", value="   ")
        assert not _is_valid_cookie(c_ws_val, domains)

        # Name length boundary (200 ok, 201 too long)
        c_name_200 = make_cookie(name="A" * 200, value="val")
        assert _is_valid_cookie(c_name_200, domains)

        c_name_201 = make_cookie(name="A" * 201, value="val")
        assert not _is_valid_cookie(c_name_201, domains)

        # Value length boundary (2000 ok, 2001 too long)
        c_val_2000 = make_cookie(name="SID", value="V" * 2000)
        assert _is_valid_cookie(c_val_2000, domains)

        c_val_2001 = make_cookie(name="SID", value="V" * 2001)
        assert not _is_valid_cookie(c_val_2001, domains)

        # Regex mismatch on name or value
        c_bad_name_regex = make_cookie(name="NAME WITH SPACE", value="val")
        assert not _is_valid_cookie(c_bad_name_regex, domains)

        c_bad_val_regex = make_cookie(name="SID", value="VAL\nNEWLINE")
        assert not _is_valid_cookie(c_bad_val_regex, domains)

    def test_sanitize_cookie_expiry(self) -> None:
        c1 = make_cookie(expires=MAX_COOKIE_EXPIRY + 100)
        _sanitize_cookie(c1)
        assert c1.expires == MAX_COOKIE_EXPIRY

        c2 = make_cookie(expires=MAX_COOKIE_EXPIRY)
        _sanitize_cookie(c2)
        assert c2.expires == MAX_COOKIE_EXPIRY

        c3 = make_cookie(expires=1000)
        _sanitize_cookie(c3)
        assert c3.expires == 1000

        c4 = make_cookie(expires=None)
        _sanitize_cookie(c4)
        assert c4.expires is None

    def test_extract_raw_cookies_scenarios(self) -> None:
        # 1. yt_dlp is None
        with (
            patch.object(cookie_extractor, "yt_dlp", None),
            patch("sys.stderr", new_callable=io.StringIO) as mock_stderr,
        ):
            assert _extract_raw_cookies("firefox", verbose=True) is None
            assert mock_stderr.getvalue() == "yt-dlp is not installed; cannot extract cookies.\n"

            mock_stderr.truncate(0)
            mock_stderr.seek(0)
            assert _extract_raw_cookies("firefox", verbose=False) is None
            assert mock_stderr.getvalue() == ""

        # 2. yt_dlp extraction succeeds
        mock_ytdlp = MagicMock()
        mock_ytdlp.cookies.extract_cookies_from_browser.return_value = ["dummy_cookie"]
        with patch.object(cookie_extractor, "yt_dlp", mock_ytdlp):
            res = _extract_raw_cookies("chrome", verbose=False)
            assert res == ["dummy_cookie"]
            mock_ytdlp.cookies.extract_cookies_from_browser.assert_called_once_with("chrome")

        # 3. yt_dlp extraction raises exception
        mock_ytdlp_err = MagicMock()
        mock_ytdlp_err.cookies.extract_cookies_from_browser.side_effect = RuntimeError("Locked")
        with (
            patch.object(cookie_extractor, "yt_dlp", mock_ytdlp_err),
            patch("sys.stderr", new_callable=io.StringIO) as mock_stderr,
        ):
            assert _extract_raw_cookies("brave", verbose=True) is None
            assert "Could not read cookies from 'brave': Locked\n" == mock_stderr.getvalue()

            mock_stderr.truncate(0)
            mock_stderr.seek(0)
            assert _extract_raw_cookies("brave", verbose=False) is None
            assert mock_stderr.getvalue() == ""


class TestExportCookiesFromBrowser:
    """Validate export_cookies_from_browser logic and output file handling."""

    def test_export_cookies_from_browser_defaults_and_temp_file(self, tmp_path: Path) -> None:
        out_file = tmp_path / "default_args.txt"
        guest_cookie = make_cookie(name="PREF", value="f1=123", domain=".youtube.com")
        orig_save = http.cookiejar.MozillaCookieJar.save
        save_kwargs: dict[str, Any] = {}

        def spy_save(self: Any, *args: Any, **kwargs: Any) -> Any:
            save_kwargs.update(kwargs)
            return orig_save(self, *args, **kwargs)

        with (
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor._extract_raw_cookies",
                return_value=[guest_cookie],
            ),
            patch("sys.stdout", new_callable=io.StringIO) as mock_stdout,
            patch.object(http.cookiejar.MozillaCookieJar, "save", spy_save),
        ):
            # Call without require_auth or verbose
            assert export_cookies_from_browser("firefox", out_file)
            assert out_file.exists()
            assert mock_stdout.getvalue() == ""  # verbose defaulted to False
            assert save_kwargs == {"ignore_discard": True, "ignore_expires": True}

    def test_export_cookies_from_browser_handles_raw_extraction_failure(
        self, tmp_path: Path
    ) -> None:
        out_file = tmp_path / "extracted.txt"
        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor._extract_raw_cookies",
            return_value=None,
        ):
            assert not export_cookies_from_browser("firefox", out_file)
            assert not out_file.exists()

    def test_export_cookies_from_browser_no_valid_cookies(self, tmp_path: Path) -> None:
        out_file = tmp_path / "extracted.txt"
        invalid_cookie = make_cookie(name="bad name with spaces", value="val")
        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor._extract_raw_cookies",
            return_value=[invalid_cookie],
        ):
            assert not export_cookies_from_browser("firefox", out_file)
            assert not out_file.exists()

    def test_export_cookies_from_browser_require_auth_fails_if_only_guest(
        self, tmp_path: Path
    ) -> None:
        out_file = tmp_path / "extracted.txt"
        guest_cookie = make_cookie(name="PREF", value="f1=123", domain=".youtube.com")
        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor._extract_raw_cookies",
            return_value=[guest_cookie],
        ):
            assert not export_cookies_from_browser("firefox", out_file, require_auth=True)
            assert not out_file.exists()

    def test_export_cookies_from_browser_guest_succeeds_when_not_requiring_auth(
        self, tmp_path: Path
    ) -> None:
        out_file = tmp_path / "guest.txt"
        guest_cookie = make_cookie(name="PREF", value="f1=123", domain=".youtube.com")
        with (
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor._extract_raw_cookies",
                return_value=[guest_cookie],
            ),
            patch("sys.stdout", new_callable=io.StringIO) as mock_stdout,
        ):
            assert export_cookies_from_browser(
                "firefox", out_file, require_auth=False, verbose=True
            )
            assert out_file.exists()
            expected_msg = f"[cookies] Saved 1 active cookies (1 YouTube-specific [Guest/Unauthenticated]) from 'firefox' -> {out_file.name}\n"
            assert mock_stdout.getvalue() == expected_msg

    def test_export_cookies_from_browser_auth_succeeds(self, tmp_path: Path) -> None:
        out_file = tmp_path / "auth.txt"
        auth_cookie = make_cookie(name="LOGIN_INFO", value="abc_token", domain=".youtube.com")
        google_cookie = make_cookie(name="NID", value="google_token", domain=".google.com")
        with (
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor._extract_raw_cookies",
                return_value=[auth_cookie, google_cookie],
            ),
            patch("sys.stdout", new_callable=io.StringIO) as mock_stdout,
        ):
            assert export_cookies_from_browser("chrome", out_file, require_auth=True, verbose=True)
            assert out_file.exists()
            expected_msg = f"[cookies] Saved 2 active cookies (1 YouTube-specific [Authenticated Session]) from 'chrome' -> {out_file.name}\n"
            assert mock_stdout.getvalue() == expected_msg
            content = out_file.read_text()
            assert "LOGIN_INFO" in content
            assert "NID" in content

    def test_export_cookies_from_browser_creates_parent_directories(self, tmp_path: Path) -> None:
        deep_out = tmp_path / "deep" / "nested" / "cookies.txt"
        valid_cookie = make_cookie(name="PREF", value="val", domain=".youtube.com")
        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor._extract_raw_cookies",
            return_value=[valid_cookie],
        ):
            assert export_cookies_from_browser("firefox", deep_out)
            assert deep_out.exists()

    def test_export_cookies_from_browser_uses_exact_tmp_suffix(self, tmp_path: Path) -> None:
        out_file = tmp_path / "test_suffix.txt"
        valid_cookie = make_cookie(name="PREF", value="val", domain=".youtube.com")
        with (
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor._extract_raw_cookies",
                return_value=[valid_cookie],
            ) as mock_extract,
            patch("http.cookiejar.MozillaCookieJar.__init__", return_value=None) as mock_jar_init,
            patch("http.cookiejar.MozillaCookieJar.set_cookie"),
            patch("http.cookiejar.MozillaCookieJar.save"),
            patch.object(Path, "replace"),
        ):
            assert export_cookies_from_browser("chrome", out_file, verbose=True)
            mock_extract.assert_called_once_with("chrome", True)
            mock_jar_init.assert_called_once()
            filename_arg = mock_jar_init.call_args[0][0]
            assert filename_arg.endswith(".tmp")

    def test_export_cookies_from_browser_skips_invalid_cookie_and_continues(
        self, tmp_path: Path
    ) -> None:
        out_file = tmp_path / "skip_invalid.txt"
        invalid_cookie = make_cookie(name="BAD NAME WITH SPACE", value="val")
        valid_cookie = make_cookie(name="PREF", value="val", domain=".youtube.com")
        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor._extract_raw_cookies",
            return_value=[invalid_cookie, valid_cookie],
        ):
            assert export_cookies_from_browser("firefox", out_file)
            assert out_file.exists()

    def test_export_cookies_from_browser_counts_multiple_youtube_cookies(
        self, tmp_path: Path
    ) -> None:
        out_file = tmp_path / "yt_multiple.txt"
        yt1 = make_cookie(name="PREF", value="val1", domain=".youtube.com")
        yt2 = make_cookie(name="YSC", value="val2", domain=".youtube.com")
        with (
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor._extract_raw_cookies",
                return_value=[yt1, yt2],
            ),
            patch("sys.stdout", new_callable=io.StringIO) as mock_stdout,
        ):
            assert export_cookies_from_browser("firefox", out_file, verbose=True)
            assert "(2 YouTube-specific" in mock_stdout.getvalue()


class TestExportCookiesAuto:
    """Validate browser scanning and fallback passes in export_cookies_auto."""

    def test_export_cookies_auto_default_browser(self, tmp_path: Path) -> None:
        out_file = tmp_path / "auto_def.txt"
        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser"
        ) as mock_exp:
            mock_exp.return_value = True
            assert export_cookies_auto(out_file)
            mock_exp.assert_called_once_with(
                browser="firefox", output_file=out_file.resolve(), require_auth=True, verbose=False
            )

    def test_export_cookies_auto_preferred_browser_priority(self, tmp_path: Path) -> None:
        out_file = tmp_path / "auto.txt"
        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser"
        ) as mock_exp:
            mock_exp.return_value = True
            assert export_cookies_auto(out_file, preferred_browser="chrome", verbose=True)
            mock_exp.assert_called_once_with(
                browser="chrome", output_file=out_file.resolve(), require_auth=True, verbose=True
            )

    def test_export_cookies_auto_checks_all_browsers_in_order(self, tmp_path: Path) -> None:
        out_file = tmp_path / "auto_all.txt"
        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser",
            return_value=False,
        ) as mock_exp:
            assert not export_cookies_auto(out_file, preferred_browser=None)
            called_browsers_pass1 = [c.kwargs["browser"] for c in mock_exp.call_args_list[:5]]
            assert called_browsers_pass1 == ["firefox", "chrome", "chromium", "brave", "edge"]
            called_browsers_pass2 = [c.kwargs["browser"] for c in mock_exp.call_args_list[5:10]]
            assert called_browsers_pass2 == ["firefox", "chrome", "chromium", "brave", "edge"]

    def test_export_cookies_auto_unknown_browser_priority(self, tmp_path: Path) -> None:
        out_file = tmp_path / "auto.txt"
        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser"
        ) as mock_exp:
            mock_exp.side_effect = [False, True]
            assert export_cookies_auto(out_file, preferred_browser="unknown_browser")
            assert mock_exp.call_args_list[0] == call(
                browser="firefox", output_file=out_file.resolve(), require_auth=True, verbose=False
            )
            assert mock_exp.call_args_list[1] == call(
                browser="chrome", output_file=out_file.resolve(), require_auth=True, verbose=False
            )

    def test_export_cookies_auto_second_pass_fallback(self, tmp_path: Path) -> None:
        out_file = tmp_path / "auto.txt"
        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser"
        ) as mock_exp:
            mock_exp.side_effect = [False, False, False, False, False, True]
            assert export_cookies_auto(out_file, preferred_browser="firefox")
            assert mock_exp.call_count == 6
            assert mock_exp.call_args_list[5] == call(
                browser="firefox", output_file=out_file.resolve(), require_auth=False, verbose=False
            )


class TestEnsureCookiesFile:
    """Validate ensure_cookies_file refresh conditions and file reusage."""

    def test_ensure_cookies_file_reuses_valid_fresh_file(self, tmp_path: Path) -> None:
        existing_file = tmp_path / "cookies.txt"
        lines = [
            "# Netscape HTTP Cookie File",
            ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tLOGIN_INFO\taf87d6fsd7f6s",
            ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tSID\tsample_session_token",
        ]
        existing_file.write_text("\n".join(lines))

        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser"
        ) as mock_exp:
            resolved = ensure_cookies_file(existing_file, browser="firefox", max_age_hours=24)
            assert resolved == existing_file
            mock_exp.assert_not_called()

    def test_ensure_cookies_file_default_age_boundary(self, tmp_path: Path) -> None:
        existing_file = tmp_path / "cookies.txt"
        lines = [
            "# Netscape HTTP Cookie File",
            ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tLOGIN_INFO\taf87d6fsd7f6s",
        ]
        existing_file.write_text("\n".join(lines))

        now = time.time()
        # Exactly 12 hours: age_seconds == max_age_hours * 3600 (not >): should NOT refresh
        stat_exact = MagicMock()
        stat_exact.st_size = 200
        stat_exact.st_mtime = now - 12 * 3600

        with (
            patch("time.time", return_value=now),
            patch.object(Path, "stat", return_value=stat_exact),
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser"
            ) as mock_exp,
        ):
            resolved = ensure_cookies_file(existing_file)
            assert resolved == existing_file
            mock_exp.assert_not_called()

        # 12.01 hours: age_seconds > max_age_hours * 3600: MUST refresh
        stat_over = MagicMock()
        stat_over.st_size = 200
        stat_over.st_mtime = now - (12.01 * 3600)

        with (
            patch("time.time", return_value=now),
            patch.object(Path, "stat", return_value=stat_over),
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser",
                return_value=True,
            ) as mock_exp,
        ):
            resolved = ensure_cookies_file(existing_file)
            assert resolved == existing_file
            mock_exp.assert_called_once_with(
                browser="firefox",
                output_file=existing_file.resolve(),
                require_auth=True,
                verbose=False,
            )

        # 12 hours + 0.5s: age_seconds > max_age_hours * 3600: MUST refresh (kills max_age_hours * 3601)
        stat_just_over = MagicMock()
        stat_just_over.st_size = 200
        stat_just_over.st_mtime = now - (12 * 3600 + 0.5)

        with (
            patch("time.time", return_value=now),
            patch.object(Path, "stat", return_value=stat_just_over),
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser",
                return_value=True,
            ) as mock_exp,
        ):
            resolved = ensure_cookies_file(existing_file)
            assert resolved == existing_file
            mock_exp.assert_called_once_with(
                browser="firefox",
                output_file=existing_file.resolve(),
                require_auth=True,
                verbose=False,
            )

    def test_ensure_cookies_file_guest_only_triggers_refresh(self, tmp_path: Path) -> None:
        guest_file = tmp_path / "guest_cookies.txt"
        lines = [
            "# Netscape HTTP Cookie File",
            ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tPREF\tf1=50000000",
            ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tYSC\txyz12345",
        ]
        guest_file.write_text("\n".join(lines))
        assert len(guest_file.read_bytes()) >= MIN_COOKIE_FILE_BYTES
        assert not has_valid_auth_cookies(guest_file)

        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser",
            return_value=True,
        ) as mock_exp:
            resolved = ensure_cookies_file(guest_file, browser="chrome")
            assert resolved == guest_file
            mock_exp.assert_called_once_with(
                browser="chrome", output_file=guest_file.resolve(), require_auth=True, verbose=False
            )

    def test_ensure_cookies_file_max_age_one_hour(self, tmp_path: Path) -> None:
        existing_file = tmp_path / "cookies.txt"
        lines = [
            "# Netscape HTTP Cookie File",
            ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tLOGIN_INFO\taf87d6fsd7f6s",
        ]
        existing_file.write_text("\n".join(lines))
        now = time.time()
        stat_over = MagicMock()
        stat_over.st_size = 200
        stat_over.st_mtime = now - 2 * 3600

        with (
            patch("time.time", return_value=now),
            patch.object(Path, "stat", return_value=stat_over),
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser",
                return_value=True,
            ) as mock_exp,
        ):
            resolved = ensure_cookies_file(existing_file, max_age_hours=1)
            assert resolved == existing_file
            mock_exp.assert_called_once()

    def test_ensure_cookies_file_size_boundary(self, tmp_path: Path) -> None:
        f50 = tmp_path / "c50.txt"
        content = "A" * (50 - len("\tSID\t")) + "\tSID\t"
        f50.write_text(content)
        assert len(f50.read_bytes()) == 50

        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser"
        ) as mock_exp:
            # Size 50 and valid auth cookies -> does NOT refresh
            resolved = ensure_cookies_file(f50, max_age_hours=0)
            assert resolved == f50
            mock_exp.assert_not_called()

        f49 = tmp_path / "c49.txt"
        f49.write_text("A" * (49 - len("\tSID\t")) + "\tSID\t")
        assert len(f49.read_bytes()) == 49

        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser",
            return_value=True,
        ) as mock_exp:
            # Size 49 -> MUST refresh even if max_age_hours=0
            resolved = ensure_cookies_file(f49, max_age_hours=0)
            assert resolved == f49
            mock_exp.assert_called_once()

    def test_ensure_cookies_file_max_age_hours_zero_skips_age_check(self, tmp_path: Path) -> None:
        valid_file = tmp_path / "cookies.txt"
        lines = [
            "# Netscape HTTP Cookie File",
            ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tLOGIN_INFO\taf87d6fsd7f6s",
        ]
        valid_file.write_text("\n".join(lines))
        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser"
        ) as mock_exp:
            resolved = ensure_cookies_file(valid_file, browser="firefox", max_age_hours=0)
            assert resolved == valid_file
            mock_exp.assert_not_called()

    def test_ensure_cookies_file_refreshes_missing_or_invalid_file(self, tmp_path: Path) -> None:
        out_file = tmp_path / "fresh.txt"
        with (
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser",
                return_value=False,
            ) as mock_browser,
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_auto",
                return_value=True,
            ) as mock_auto,
        ):
            out_file.write_text("dummy active cookies")
            resolved = ensure_cookies_file(out_file, browser="chrome")
            assert resolved == out_file
            mock_browser.assert_called_once_with(
                browser="chrome", output_file=out_file.resolve(), require_auth=True, verbose=False
            )
            mock_auto.assert_called_once_with(
                output_file=out_file.resolve(), preferred_browser="chrome", verbose=False
            )

    def test_ensure_cookies_file_no_browser_specified(self, tmp_path: Path) -> None:
        out_file = tmp_path / "no_browser.txt"
        out_file.write_text("dummy active cookies")
        with (
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser"
            ) as mock_browser,
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_auto",
                return_value=True,
            ) as mock_auto,
        ):
            resolved = ensure_cookies_file(out_file, browser=None)
            assert resolved == out_file
            mock_browser.assert_not_called()
            mock_auto.assert_called_once_with(
                output_file=out_file.resolve(), preferred_browser=None, verbose=False
            )

    def test_ensure_cookies_file_failed_refresh_size_boundaries(self, tmp_path: Path) -> None:
        # If refresh fails, and file exists with size 1 -> returns out_path
        f1 = tmp_path / "size1.txt"
        f1.write_text("x")
        with (
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser",
                return_value=False,
            ),
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_auto",
                return_value=False,
            ),
        ):
            assert ensure_cookies_file(f1, max_age_hours=0) == f1

        # If refresh fails and file exists with size 0 -> returns None
        f0 = tmp_path / "size0.txt"
        f0.touch()
        with (
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser",
                return_value=False,
            ),
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_auto",
                return_value=False,
            ),
        ):
            assert ensure_cookies_file(f0, max_age_hours=0) is None

        # If refresh fails and file does not exist -> returns None
        f_missing = tmp_path / "missing.txt"
        with (
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser",
                return_value=False,
            ),
            patch(
                "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_auto",
                return_value=False,
            ),
        ):
            assert ensure_cookies_file(f_missing, max_age_hours=0) is None

    def test_ensure_cookies_file_success_size_boundaries(self, tmp_path: Path) -> None:
        # If refresh succeeds, but resulting file has size 0 -> returns None
        f0 = tmp_path / "success_size0.txt"
        f0.touch()
        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser",
            return_value=True,
        ):
            assert ensure_cookies_file(f0) is None

        # If refresh succeeds and file has size 1 -> returns out_path
        f1 = tmp_path / "success_size1.txt"
        f1.write_text("x")
        with patch(
            "cresmo.infrastructure.adapters.cookie_extractor.export_cookies_from_browser",
            return_value=True,
        ):
            assert ensure_cookies_file(f1) == f1


class TestExportCookiesCLICommand:
    """Validate cresmo export-cookies CLI command."""

    def test_export_cookies_cli_success(self, tmp_path: Path) -> None:
        out_file = tmp_path / "test_cookies.txt"
        with patch(
            "cresmo.presentation.commands.export_cookies.export_cookies_from_browser",
            return_value=True,
        ) as mock_exp:
            exit_code = main(
                ["export-cookies", "--browser", "firefox", "--output", str(out_file), "--force"]
            )
            assert exit_code == EXIT_SUCCESS
            mock_exp.assert_called_once()

    def test_export_cookies_cli_failure_returns_ingestion_error(self, tmp_path: Path) -> None:
        out_file = tmp_path / "test_cookies.txt"
        with patch(
            "cresmo.presentation.commands.export_cookies.export_cookies_from_browser",
            return_value=False,
        ):
            exit_code = main(
                ["export-cookies", "--browser", "chrome", "--output", str(out_file), "--force"]
            )
            assert exit_code == EXIT_INGESTION_ERROR
