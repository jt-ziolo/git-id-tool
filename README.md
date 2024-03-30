# git-id-tool

Work in progress.

Consider setting up a git alias for easier cli access, like this:

```txt
  [alias]
    id = "!git-id-tool"
```

## Commands

### show

- Checks that your git repo, gpg, and ssh config are consistent.
- Running with 

### guard {git-command-and-args}

- Warns you and prompts you for confirmation prior to execution of the provided git command and args if there are inconsistencies in your id (between your current git repo, gpg, and ssh config)
- Format: `git-id-tool guard <args>`
- Examples:
  - `git-id-tool guard push (...)` => `git push (...)`
  - `git-id-tool guard commit (...)` => `git commit (...)`

Alias setup:

```txt
  [alias]
    push = "!git-id-tool guard push"
    commit = "!git-id-tool guard commit"
```
