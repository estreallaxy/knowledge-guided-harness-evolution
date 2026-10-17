# Exact source anchors

## Selected mechanism

Execute and score computer-use security tasks in isolated vulnerable web environments with explicit success checks.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | framework |
| Experimental setup | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | experiments |
| Results and ablations | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | results |
| Limitations or failure conditions | PDF p.5; `paper/paper-iclr2026.txt` marker `===== PDF p.5 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/desktop_env/evaluators/metrics/pdf.py:9` | `check_pdf_pages` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/pdf.py:17` | `extract_answers_from_pdf` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/libreoffice.py:16` | `check_libre_locale` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/basic_os.py:1` | `check_gnome_favorite_apps` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/basic_os.py:17` | `is_utc_0` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/basic_os.py:37` | `check_text_enlarged` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/others.py:18` | `process_epub` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/others.py:60` | `compare_epub` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/others.py:77` | `check_mp3_meta` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/__init__.py:157` | `infeasible` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/thunderbird.py:17` | `check_thunderbird_prefs` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/thunderbird.py:76` | `check_thunderbird_filter` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/thunderbird.py:138` | `check_thunderbird_folder` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/vscode.py:9` | `check_json_keybindings` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/vscode.py:49` | `check_json_settings` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/vscode.py:73` | `compare_text_file` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/chrome.py:16` | `is_expected_active_tab` | Pinned implementation entry for the selected mechanism. |
| `official-code/desktop_env/evaluators/metrics/chrome.py:40` | `is_expected_url_pattern_match` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `7eddbe396d2adb3042482134fd08508e8ea21a3f`. Paper page numbers refer to the fixed local proceedings PDF.
