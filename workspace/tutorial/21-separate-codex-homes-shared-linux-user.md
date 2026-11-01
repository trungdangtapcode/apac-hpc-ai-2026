# Separate Codex environments under one Linux account

Written on 1 November 2026, Vietnam time (UTC+7). Local observations below concern Codex CLI 0.166.0 on this login host. Commands and database schemas can change between releases.

## Recovery status

The missing session list was repaired. All 230 indexed rollout paths were checked again during preparation of this guide and pointed to existing files. The previous interactive check displayed the GPU, HPC and forked research sessions. These counts include execution and subagent sessions, so the interactive picker normally displays fewer entries.

The separate `arg0` cleanup warning can still recur. Session recovery is verified; a permanent fix for that warning is not established. The detailed incident record is [Codex session recovery after moving CODEX_HOME](../notes/codex-home-session-recovery-20261101.md).

## What needs to be separated

`CODEX_HOME` selects the root of Codex's local state. By default it is `~/.codex`; the personal environment here uses `/home/apacsc42/.codex-tmp`. The spelling includes an underscore: `CODEXHOME` is a different variable and does not select the Codex home. See the official [environment variables](https://learn.chatgpt.com/docs/config-file/environment-variables) documentation.

| Layer | Purpose | Practical rule |
|---|---|---|
| Codex home | Configuration, saved sessions, logs, skills and other local state | Give each intended environment a distinct, stable directory. |
| SQLite location | Database-backed state and session indexing | Check `CODEX_SQLITE_HOME` and `sqlite_home` overrides as well as `CODEX_HOME`. |
| Launcher and executable | Chooses the Codex program and version | Check aliases, functions, PATH and symlinks independently of the state directory. |
| Server process | Hosts Codex when a shared background server is used | The existing personal launcher uses `--no-daemon` for the interactive CLI. |
| Working directory | Files the agent reads and edits | Separate Codex homes can still edit the same source files. Coordinate ownership and use worktrees or locks when appropriate. |
| Linux identity | File and process permissions | Separate Codex homes under the same UID provide operational separation, not a security boundary between people. |

Authentication may use files in the Codex home or an OS credential store. A different home alone is not proof of a fully independent credential store. Use each environment's intended login flow; do not copy another person's authentication state. The official [state locations](https://learn.chatgpt.com/docs/config-file/config-advanced) describe this distinction.

The SQLite directory defaults to `CODEX_HOME`, but `CODEX_SQLITE_HOME` can override it and the `sqlite_home` configuration setting has higher precedence. An inherited override can accidentally make otherwise separate launchers use the same databases. During this check, `CODEX_SQLITE_HOME` was unset and no `sqlite_home` setting was found in the personal base configuration; profile and invocation overrides must still be considered when troubleshooting another launch.

## The launcher already configured here

The existing interactive Bash alias in `/home/apacsc42/.bashrc` is:

```bash
alias codex-tmp='CODEX_HOME="$HOME/.codex-tmp" "$HOME/.codex-tmp/packages/standalone/current/bin/codex" --no-daemon'
```

The assignment applies to that command and its children. It does not permanently export the personal home into every other command in the shell. Keeping the assignment inside a named launcher reduces accidental changes to other uses of the shared account.

The executable path is quoted, and the installer-managed `current` symlink chooses the installed standalone release. At verification it resolved to version 0.166.0. Updating that symlink can change the version without changing the alias. Pinning an exact release is an alternative when reproducing a version-specific issue; do not assume an old pinned release has the same flags or database compatibility as a newer one.

One important local detail: `/home/apacsc42/.local/bin/codex` also resolved to the standalone installation inside `.codex-tmp`. Therefore, bare `codex` can use the personal binary while still using the default `.codex` state directory if `CODEX_HOME` is unset. The binary path and the state path are separate choices. Do not change the shared `codex` symlink merely to fix a personal session list.

For a second environment, create its own home first, choose a distinct launcher name and explicitly select its home and an available executable. A separate binary installation is optional; explicit state selection is essential. These are configuration guidelines, not a claim that a second environment was installed during this repair.

The official [CLI reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli) defines `--no-daemon` as running the interactive CLI without the shared background server. It does not separate filesystem permissions or stop existing server processes. Check the actual version's help before using the flag with other commands.

## Everyday commands

```bash
# Run these from your normal interactive Bash shell.
type -a codex codex-tmp
codex-tmp --version
codex-tmp resume --help
codex-tmp resume --all
```

`resume --all` expands the picker beyond the current working directory inside the selected Codex home. It does not merge sessions from other homes. `resume all` instead asks for a session whose name or ID is literally `all`. When similarly named sessions exist, resume by the exact intended UUID.

An alias is normally unavailable in a non-interactive script. For a script, use the explicit equivalent:

```bash
CODEX_HOME="$HOME/.codex-tmp" \
  "$HOME/.codex-tmp/packages/standalone/current/bin/codex" \
  --no-daemon resume --all
```

Do not globally source a shared `.bashrc` just to test one alias: it may contain unrelated environment changes. Opening a new interactive shell or invoking the explicit command is sufficient.

## Why moving the home broke the session list

The transcript files had moved, but the copied SQLite session index retained absolute paths into the old home:

```text
Old indexed path: /home/apacsc42/.codex/sessions/.../rollout-....jsonl
Actual file:      /home/apacsc42/.codex-tmp/sessions/.../rollout-....jsonl
```

There were 230 thread records and 230 rollout files. Before repair, 213 indexed paths still used the old prefix and were missing; the other 17 paths existed. Each missing path had a corresponding file under the new home. The empty or incomplete picker therefore did not establish that conversations had been deleted.

The repair used SQLite's backup API to create a consistent private backup with mode 0600, then performed a short transaction. It changed only `threads.rollout_path` values where the old path was missing and the corresponding relocated file existed. Afterwards, `PRAGMA quick_check` returned `ok` and all 230 paths existed. Transcript contents, thread IDs, names and research payloads were preserved.

Do not replace a database or create a symlink from the shared `.codex` directory to the personal home as a generic workaround. A shared-home symlink would couple the environments again. This incident's repair was specific to the observed schema and verified relocation.

## Read-only diagnosis if sessions disappear again

First establish the launcher's home and executable. Check whether the picker is restricted to a working directory, whether a SQLite override is active, and whether transcript files still exist. Avoid printing complete configuration or authentication files into a shared terminal or report.

The following diagnostic reports counts only for the schema observed here. It does not modify the database. If a future version uses a different filename or schema, inspect that version before adapting it.

```bash
python3 - <<'PY'
from pathlib import Path
import sqlite3

codex_home = Path('/home/apacsc42/.codex-tmp')
database = codex_home / 'state_5.sqlite'
with sqlite3.connect(database.as_uri() + '?mode=ro', uri=True) as connection:
    rows = connection.execute('SELECT rollout_path FROM threads').fetchall()
print('Indexed sessions:', len(rows))
print('Existing rollout paths:', sum(Path(path).is_file() for (path,) in rows))
print('Rollout files in this home:', sum(1 for _ in (codex_home / 'sessions').rglob('*.jsonl')))
PY
```

If counts differ, inspect the actual missing paths privately before deciding what to repair. A missing transcript is different from a stale index, an archived session, a source filter or a different selected home. Do not bulk-rewrite unrelated paths, task working directories or historical transcript contents.

## Lessons for a future migration

1. Prefer a stable home path. Renaming a directory can leave absolute references in databases, launchers and helper symlinks.
2. Identify and close only the intended environment's writers before an offline migration. Do not use a blanket `pkill codex` on a shared account.
3. Preserve a private rollback copy. If writers are live, copying only a SQLite main file can miss changes in its write-ahead log; use SQLite's backup API for a consistent database backup. A live transcript tree also needs coordination for a coherent copy.
4. Move only the intended owner's state. Authenticate a newly independent environment through its intended login process rather than distributing credential files.
5. Check the new launcher's executable, home, SQLite overrides and actual indexed file paths. Merely finding files under `sessions/` is not enough.
6. Verify database integrity and open the picker. Resume an intended session only when ready to continue its work. Keep the rollback copy until the migration is verified.
7. Keep private session backups separate from sanitized documentation and code archives. Git publication of this guide does not back up the conversations or credentials.

## Interpreting the remaining terminal warning

The `arg0` warning was traced to cleanup attempting to rename an unlocked stale helper directory over a newly created empty destination. The filesystem returned `EEXIST`. Forty-nine unlocked helper directories were preserved in a private recovery directory and two locked directories were untouched. The warning later returned, so that cleanup did not establish a permanent fix. It did not prevent the verified resume picker from loading.

Do not delete the whole temporary tree while other sessions are active. A cleanup warning and a broken session index require separate evidence. The pasted `9;5:3u` resembles escaped terminal keyboard-protocol input; its precise cause was not reproduced and it is not evidence of transcript deletion.

## What this documentation change did

This guide records the already completed repair and the additional read-only path check. It does not install another Codex, change the existing alias, move credentials, stop other users' processes, start background Codex, or modify research jobs and budgets. Only sanitized Markdown and its navigation entries belong to the research archive.
