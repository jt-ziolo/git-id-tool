# git-id-tool

## Todos

- [ ] show
- [ ] copy
- [ ] make-global
- [ ] use

## Commands

I recommend that you setup a git alias, like this: `id = "!git-id-tool"`

### show

- Shows the current git configuration for the `[user]` section
- Lists each git remote and which SSH host is currently set to be used for that remote based on that remote's url and the SSH configuration
- Will warn you if no gpg signing key has been set, and then provide you with instructions for how to set it using `git config --local user.signingkey {key}` or `git id copy {git-dir}`

#### GPG signing key information

- If passed the option `--check-gpg`, the output of `gpg --list-keys --keyid-format=long` will be used to determine the name and email attached to the repo's gpg signing key. Mismatches between the information attached to the signing key and the git repo configuration will be highlighted in the output.

### copy {git-dir}

- If running this command would not change the current git repo's configuration, then the program exits and nothing is changed
- Will copy the `[user]` section of the **target** repo's git configuration and overwrite the **current** git repo's `[user]` section with it
- Your old local git configuration will be backed up to `.git/config.backup.{timestamp}`

### make-global

- If running this command would not change your global git configuration, then the program exits and nothing is changed
- Will copy the `[user]` section of the **current** repo's git configuration and overwrite your global `[user]` section with it
- Your old global git configuration will be backed up to `.gitconfig.backup.{timestamp}`

### use {identity-file}

- Moves any `~/.ssh/config` entries matching the identity file pattern (regex) to the top of the file, prior to any other entries
- Then, it will set up the current repo's git configuration (`.git/config`) to match:
  - user.email = {email from SSH configuration entry}
  - user.name = {name from SSH configuration entry}
- Then, it will run the `show` command

#### When no arguments are given, or an invalid argument is given

- Lists the allowed values for identity files based on the contents of your user-level `.ssh` directory
