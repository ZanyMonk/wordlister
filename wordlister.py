#!/usr/bin/env python3
import os
import re
import sys
import glob
import click
import pathlib

STASH_PATH=None
ACCEPT_USERNAMES=None

def count_wordlist():
  try:
    return sum(1 for line in open(STASH_PATH))
  except FileNotFoundError:
    return 0

def sort_wordlist():
  if os.system(f'sort -u -o "{STASH_PATH}" "{STASH_PATH}"') == 1:
    click.echo('Use a proper operating system.')

def strip_username(word, inverse=False):
  if ACCEPT_USERNAMES and not inverse:
    return word

  sep_pos = word.find(':')

  if not inverse and sep_pos > -1:
    word = word[sep_pos+1:]

  return word

def save_word(word):
  global STASH_PATH

  word = strip_username(word)

  if len(word) == 0:
    return

  with open(STASH_PATH, 'a+') as f:
    print(word, file=f)
    f.close

  sort_wordlist()

def save_words(words):
  global STASH_PATH

  with open(STASH_PATH, 'a+') as f:
    for word in words:
      word = strip_username(word)

      if len(word) == 0:
        continue

      print(word, file=f)
    f.close

  sort_wordlist()
  
  return len(words)

def save_wordlist(wordlist):
  count = 0
  
  with open(STASH_PATH, 'a+') as f:
    with open(pathlib.Path(wordlist).resolve(), 'r') as i:
      rl = i.readlines()
      for word in rl:
        word = strip_username(word)

        if len(word) == 0:
          continue

        count = count + 1
        print(word, end='', file=f)
  
  sort_wordlist()

  return count


def extract_dir(path, max_depth, max_length, get_file_content, ext, keep_ext):
  words = set()

  for p in _extract_dir(path, max_depth, max_length, get_file_content, ext):
    if get_file_content or ext and p.find(ext) > -1:
      pass

    for w in p.split('/'):
      if w == '..' or w == '.':
        continue

      sep_pos = w.find('.')
      if not keep_ext and sep_pos > -1:
        w = w[:sep_pos]

      if len(w) > max_length:
        continue

      words.add(w)
  
  return words

def _extract_dir(path, max_depth, max_length, get_file_content, ext, all=set(), depth=0):
  for p in glob.glob(f'{path}/*'):
    if os.path.isdir(p) and depth < max_depth:
      _extract_dir(p, max_depth, max_length, get_file_content, ext, all, depth+1)
    elif os.path.isfile(p) and get_file_content and ext and p.find(ext) > -1:
      extract_file(p, max_length, all)
    else:
      all.add(p)
  return all

def extract_file(path, max_length, words=set()):
  try:
    with open(pathlib.Path(path).resolve(), 'r') as f:
      rl = f.readlines()
      for line in rl:
        for word in re.split(r'[^a-zA-Z0-9#~&@$_-]', line):
          length = len(word)
          if length and length <= max_length:
            words.add(word)
    return words
    
  except UnicodeDecodeError:
    return words
  except FileNotFoundError:
    click.echo('File not found.', err=True)

@click.group()
@click.option('--wordlist', '-w', '-o', default='~/.wordlist.lst', help='The wordlist to read from/write to')
@click.option('--username', '-u', is_flag=True, default=False, help='Use/ignore usernames (ie. ^[^:]*:)')
def cli(wordlist, username):
  global STASH_PATH
  global ACCEPT_USERNAMES

  STASH_PATH=pathlib.Path(os.path.expanduser(wordlist)).resolve()
  ACCEPT_USERNAMES=username

@cli.command(help='Permanently delete the list')
@click.option('--yes', '-y', is_flag=True, help='Don\'t ask for confirmation')
def truncate(yes):
  try:
    with open(STASH_PATH, 'r') as fp:
      count = sum(1 for line in fp)
      if yes or click.confirm(f'Do you really want to remove {count} words ?'):
        os.remove(STASH_PATH)
        click.echo('Wordlist has been removed.', err=True)
  except FileNotFoundError:
    click.echo('Wordlist is already empty.', err=True)

@cli.command('show', help='Print all words in the list')
def show():
  try:
    with open(STASH_PATH, 'rb') as f:
      print(f.read().decode('utf-8', 'replace'), end='')
  except FileNotFoundError:
    click.echo('Wordlist is empty.', err=True)

@cli.command(help='Add new words')
@click.pass_context
@click.argument('terms', nargs=-1)
@click.option('--file', '-f', help='Wordlist file')
def add(ctx, terms, file):
  count_before = count_wordlist()

  if (not terms and not file):
    click.echo('No word or file given.', err=True)
    ctx.exit(1)

  count = 0
  
  if (file):
    count = save_wordlist(file)
  else:
    for term in list(terms):
      count = count + 1
      save_word(term)

  new_words = count_wordlist() - count_before
  click.echo(f'Added {count} words (including {new_words} new words).', err=True)

@cli.command(help='Extract from the arborescence of the given directory, or the content of its files')
@click.argument('path', default='.')
@click.option('--depth', '-d', default=2, help='Maximum depth of extraction')
@click.option('--length', '-l', default=16, help='Maximum word length')
@click.option('--recurse', '-r', is_flag=True, default=False, help='Recursively extract files content')
@click.option('--ext', '-e', default=False, help='Extract only files with these extensions')
@click.option('--keep-ext', '-k', default=False, help='Keep file extension')
@click.option('--show', '-s', default=False, help='Show the extracted words instead of adding them')
def extract(path, depth, length, recurse, ext, keep_ext, show):
  count_before = count_wordlist() if not show else 0

  if os.path.isfile(path):
    words = extract_file(path, length)
  else:
    words = extract_dir(path, depth, length, recurse, ext, keep_ext)
  
  if show:
    for word in words:
      print(word)
  else:
    count = save_words(words)
    new_words = count_wordlist() - count_before
    print(f'Added {count} words (including {new_words} new words)')
  

if __name__ == '__main__':
  cli()