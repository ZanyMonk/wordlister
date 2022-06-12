# wordlister
A tiny tool to help maintaining wordlists of all kinds

## Usage
```
Usage: wordlister.py [OPTIONS] COMMAND [ARGS]...

Options:
  -w, -o, --wordlist TEXT  The wordlist to read from/write to
  -u, --username           Use/ignore usernames (ie. ^[^:]*:)
  --help                   Show this message and exit.

Commands:
  add       Add new words
  extract   Extract from the arborescence of the given directory, or the...
  show      Print all words in the list
  truncate  Permanently delete the list
```
