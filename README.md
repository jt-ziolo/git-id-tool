# git-id-tool

Work in progress.

Consider setting up a git alias for easier cli access, like this:

```txt
  [alias]
    id = "!git-id-tool"
```

## Commands

### show

### write {git-dir}

- Will write the minimum set of git, gpg, and ssh identifying information in json format for the repo located at `{git-dir}` (or at the given path) to stdout
- The intent is that you can save the output to a json file and then edit it prior to passing it as an argument to `git-id-tool use`

Output format:

```json
{
  "name": "John Doe",
  "email": "johndoe@email.com",
  "signingkey": "ABCDEFGHIJKLMNOP",
  "remotes": {
    "example_remote_A": "example-hostname.top-level-domain",
    "example_remote_B": "github.com",
    "example_remote_C": "bitbucket.org",
  }
}
```

### use {git-dir} {json-input} -r/--recursive

Interactively sets your ssh, gpg, and local git configuration to match json input provided in the format produced by `write`.

- Based on the provided json input or .json file path:
  - Applies configuration changes to the git repo at `{git-dir}` so that the user name, email, and signing key (if valid) match the json input. If -r/--recursive is set, then applies these changes to nested repos as well.
  - Checks that each remote's hostname will result in the use of a valid ssh identity file (i.e. that the identity file's email will match the git repo's user email). If not, the tool will prompt you with the following options for each invalid remote (when valid):
    - Sort `~/.ssh/config` entries matching the hostname, reordering them so that the entries which are valid will appear first among entries with that same hostname when reading the ssh config file from top to bottom
    - Edit an existing public key file for a `~/.ssh/config` entry which matches the hostname, changing the email in the file to match the git repo's user email, then sort the config entries like done for the previous option.
    - Generate a new ssh key pair for the hostname, where the email will be pre-filled to match the git repo's user name. The key will be added to the ssh config file at the top.
    - Disable the invalid remote by deleting its URL, while keeping all other remote settings the same
    - Remove (delete) the invalid remote
    - Quit, also cancelling any changes this command would have made
  - Checks that the provided signing key matches an existing gpg public key whose uid's name and email match the git repo's user name and email. If multiple keys match, the tool will exit and print an error. If the provided signing key does not match any existing gpg public key, the tool will prompt you with the following options (when valid):
    - Change the repo signing key to match an existing gpg public key whose uid's name and email match the git repo's user name and email. An option will appear in the prompt for each valid choice. Choosing this option will also update the json file to match your choice, if a file path was passed to this command. If not, the command will write the modified json input to stdout.
    - Edit the gpg public key associated with the git repo's signing key, adding a new uid to it which matches your git repo's user name and email while deleting the old uid.
    - Generate a new gpg key pair, where the uid information will be pre-filled to match the git repo's user name and email. Choosing this option will also update the json file to replace the git repo's signingkey with the public key, if a file path was passed to this command. If not, the command will write the modified json input to stdout.
    - Quit, also cancelling any changes this command would have made
- If the command does not finish running in full, no changes will be made
