# Linux Basics — Cheat Sheet

_Absolute beginner reference. Everything you need to move around a Linux/macOS terminal and not get lost._

## The shell in one idea

You type a **command**, press **Enter**, it runs, it prints a result, you get a fresh prompt. A command is usually `program [options] [arguments]`, e.g. `ls -l /etc`. Options start with `-` (short) or `--` (long).

## Where am I? Paths

| Symbol | Means |
|---|---|
| `/` | the **root** of the whole filesystem (top of everything) |
| `~` | your **home** directory (`/home/you` or `/Users/you`) |
| `.` | the **current** directory |
| `..` | the **parent** directory (one level up) |
| `-` | (with `cd`) the **previous** directory you were in |

**Absolute path** starts at `/` → `/etc/hosts` (same everywhere). **Relative path** starts from where you are → `dept/hr.html`.

## Moving and looking around

| Command | What it does | Example |
|---|---|---|
| `pwd` | print working directory (where am I?) | `pwd` |
| `ls` | list files | `ls` |
| `ls -l` | long list: permissions, size, date | `ls -l` |
| `ls -la` | long list **including hidden** (dotfiles) | `ls -la ~` |
| `ls -lh` | human-readable sizes (K, M, G) | `ls -lh` |
| `cd DIR` | change directory | `cd /var/log` |
| `cd` or `cd ~` | go home | `cd` |
| `cd ..` | go up one level | `cd ..` |
| `cd -` | go back to previous dir | `cd -` |
| `tree` | show the folder tree | `tree -L 2` |

## Creating, copying, moving, deleting

| Command | What it does | Example |
|---|---|---|
| `mkdir DIR` | make a directory | `mkdir project` |
| `mkdir -p a/b/c` | make nested dirs in one go | `mkdir -p case/notes` |
| `touch FILE` | create an empty file / update its date | `touch todo.txt` |
| `cp SRC DST` | copy a file | `cp a.txt b.txt` |
| `cp -r SRC DST` | copy a directory (recursive) | `cp -r dir/ backup/` |
| `mv SRC DST` | move **or rename** | `mv old.txt new.txt` |
| `rm FILE` | delete a file (**no trash, forever**) | `rm junk.log` |
| `rm -r DIR` | delete a directory and its contents | `rm -r tmp/` |
| `rmdir DIR` | delete an **empty** directory | `rmdir empty/` |

> **Danger.** `rm` does not ask and does not undo. Double-check before `rm -r`. Never run `rm -rf /`.

## Reading files

| Command | What it does | Example |
|---|---|---|
| `cat FILE` | print the whole file | `cat notes.md` |
| `less FILE` | scroll a file (q to quit, / to search) | `less big.log` |
| `head FILE` | first 10 lines | `head -n 20 data.csv` |
| `tail FILE` | last 10 lines | `tail -n 50 app.log` |
| `tail -f FILE` | follow a file live (logs) | `tail -f app.log` |
| `wc -l FILE` | count lines | `wc -l users.csv` |

## Finding things

| Command | What it does | Example |
|---|---|---|
| `find PATH -name PAT` | find files by name | `find . -name "*.jpg"` |
| `find PATH -type d` | find directories | `find /etc -type d` |
| `grep PAT FILE` | find lines containing a pattern | `grep "error" app.log` |
| `grep -r PAT DIR` | search recursively in a folder | `grep -r "TODO" src/` |
| `grep -i PAT FILE` | case-insensitive | `grep -i admin users.csv` |
| `which CMD` | where is this program? | `which python3` |

## Redirection and pipes (the superpower)

| Symbol | Means | Example |
|---|---|---|
| `\|` | send output of one command **into** another | `cat f \| grep x` |
| `>` | write output to a file (**overwrite**) | `ls > list.txt` |
| `>>` | **append** output to a file | `echo hi >> log.txt` |
| `<` | read input from a file | `sort < names.txt` |
| `2>` | redirect **errors** only | `cmd 2> errors.txt` |
| `&>` | redirect output **and** errors | `cmd &> all.txt` |

Chained example: `cat access.log | grep 404 | wc -l` → count the 404 errors.

## Wildcards (globs)

| Glob | Matches | Example |
|---|---|---|
| `*` | any characters | `ls *.txt` |
| `?` | exactly one character | `ls file?.log` |
| `[abc]` | one of a, b, c | `ls img[12].png` |
| `{a,b}` | a or b | `cp file.{txt,bak}` |

## Permissions (reading `ls -l`)

```
-rwxr-xr--  1 user group  4096 Sep 16 10:00 script.sh
```
- First char: `-` file, `d` directory, `l` link.
- Then three groups of `rwx` = **owner**, **group**, **others**. `r` read, `w` write, `x` execute.

| Command | What it does | Example |
|---|---|---|
| `chmod +x FILE` | make a script executable | `chmod +x run.sh` |
| `chmod 644 FILE` | rw for owner, r for others | `chmod 644 note.txt` |
| `chmod 755 FILE` | rwx owner, rx others | `chmod 755 run.sh` |
| `chown USER FILE` | change owner (often needs sudo) | `sudo chown me file` |
| `sudo CMD` | run a command as administrator | `sudo apt update` |

## Processes

| Command | What it does |
|---|---|
| `ps aux` | list all running processes |
| `top` / `htop` | live process monitor (q to quit) |
| `cmd &` | run a command in the background |
| `jobs` | list background jobs of this shell |
| `fg` / `bg` | bring a job to foreground / background |
| `kill PID` | stop a process by its number |
| `kill -9 PID` | force-kill (last resort) |

## Archives & compression

| Command | What it does |
|---|---|
| `tar -czf out.tgz DIR/` | create a gzip tarball |
| `tar -xzf out.tgz` | extract a gzip tarball |
| `tar -tzf out.tgz` | list contents without extracting |
| `zip -r out.zip DIR/` | create a zip |
| `unzip out.zip` | extract a zip |
| `gzip FILE` / `gunzip FILE.gz` | compress / decompress one file |

## Network & system (quick)

| Command | What it does |
|---|---|
| `ip a` (or `ifconfig`) | show your network interfaces / IPs |
| `ping HOST` | test reachability (Ctrl+C to stop) |
| `curl -s URL` | fetch a URL (silent) |
| `wget URL` | download a file |
| `df -h` | disk space, human-readable |
| `du -sh DIR` | size of a folder |
| `uname -a` | kernel / system info |
| `whoami` | your username |

## Package management (Debian/Kali)

| Command | What it does |
|---|---|
| `sudo apt update` | refresh the package list |
| `sudo apt install NAME` | install a program |
| `sudo apt remove NAME` | uninstall |
| `apt search TERM` | search for a package |

## Getting help

| Command | What it does |
|---|---|
| `man CMD` | full manual (q to quit, / to search) |
| `CMD --help` | quick usage summary |
| `tldr CMD` | practical examples (install: `pip install tldr`) |
| `type CMD` | is it a program, alias or builtin? |

## Keyboard shortcuts (save minutes every day)

| Keys | Action |
|---|---|
| `Tab` | auto-complete a command or filename |
| `↑` / `↓` | previous / next command in history |
| `Ctrl+R` | search command history (type to filter) |
| `Ctrl+C` | stop the running command |
| `Ctrl+D` | end of input / logout |
| `Ctrl+L` | clear the screen (same as `clear`) |
| `Ctrl+A` / `Ctrl+E` | jump to start / end of line |
| `Ctrl+U` / `Ctrl+K` | delete to start / end of line |

> **Golden rules.** Quote paths with spaces (`cd "My Folder"`). Read before you `rm`. When stuck, `man` it or add `--help`.
