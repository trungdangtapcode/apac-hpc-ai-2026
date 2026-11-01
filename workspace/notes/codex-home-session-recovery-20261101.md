# Codex session recovery after moving CODEX_HOME

Verified on 1 November 2026 at 20:05–20:08 Vietnam time (UTC+7), on the login host, using Codex CLI 0.166.0. This maintenance session owns neither research track and made no scheduler, budget or submission changes.

The owner reported an empty resume list after separating their Codex home from the shared account's default home. The shell alias already used `CODEX_HOME="$HOME/.codex-tmp"` and the standalone `current/bin/codex` with `--no-daemon`. The supported environment variable is `CODEX_HOME`, including the underscore.

All 230 rollout files remained in `.codex-tmp/sessions`. The live `state_5.sqlite` contained 230 thread records, but 213 absolute `threads.rollout_path` values still referred to `.codex/sessions`; only 17 paths existed before repair. Each of the 213 missing paths had a corresponding file under the new home. Moving a home directory does not necessarily rewrite these persisted absolute paths.

Before repair, a consistent SQLite backup was created inside the private Codex home, with file mode 0600. A short transaction updated only missing old-prefix rollout paths whose corresponding new files existed. No transcript bytes, thread IDs, names, ownership, timestamps or research payloads were changed. SQLite `quick_check` returned `ok`; all 230 indexed rollout paths existed afterwards. An interactive `resume --all` picker visibly listed the GPU and HPC sessions and their forks, then was closed without resuming a research turn. The 230 records include execution and subagent sessions; the default interactive picker intentionally shows fewer entries.

Use `codex-tmp resume --all` to open the interactive picker across working directories. `codex-tmp resume all` instead supplies the literal session name `all`, consistent with the reported `No saved session found with ID all` error. The exact earlier invocation that produced that error was not observed. The alias and local `resume --help` both accept `--all` correctly. `--all` expands directory scope within the selected Codex home; it does not merge separate homes.

The separate warning `failed to clean up stale arg0 temp dirs: File exists (os error 17)` was traced with file-system-only `strace` during `--version`. Cleanup acquired an old directory's nonblocking exclusive lock, created an empty temporary destination, then failed to rename the stale directory over that destination with `EEXIST`. Forty-nine unlocked directories containing only the lock file and helper symlinks were preserved in a private recovery directory; two locked directories were left untouched. The warning recurred on a later invocation, so this cleanup is not a permanent fix for the CLI/filesystem interaction. The warning did not prevent the verified picker from loading. Do not delete whole temporary trees while other Codex processes are running.

The pasted `9;5:3u` resembles terminal keyboard-protocol input escaping into the shell after the TUI exits; its precise trigger was not reproduced. It is not evidence that session files were deleted.

Private SQLite backups, temporary recovery contents, transcripts, authentication state and terminal session data remain outside the research Git archive. Only this sanitized explanation and its index entry are captured.

Official references: [resume command](https://learn.chatgpt.com/docs/developer-commands?surface=cli) and [local state under CODEX_HOME](https://learn.chatgpt.com/docs/config-file/config-advanced).
