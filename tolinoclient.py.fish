#!/usr/bin/env fish
#
# Commandline completion in fish for tolinoclient.py
#
# Author: Wolfgang Pappa
# Date: June 2018

set PROG 'tolinoclient.py'

# Check whether a subcommand is still needed.
function __fish_tolino_needs_command
    set -l cmd (commandline -opc)
    if [ (count $cmd) -eq 1 -a $cmd[1] = $PROG ]
        return 0
    end
    return 1
end

# Check whether any of the given subcommands has been entered.
function __fish_tolino_uses_command
  set cmd (commandline -opc)
  if [ (count $cmd) -gt 1 ]
    # Check if any of the arguments is a subcommand
    for a in $argv
      if [ $a = $cmd[2] ]
        return 0 # subcommand found!
      end
    end
  end
  return 1 # no success
end

# List possible partners IDs.
# A tab separates the arguments from the description.
function __fish_tolino_partners
  echo "0	List partners"
  echo "3	thalia.de"
  echo "6	buch.de"
  echo "8 book.ch / orellfuessli.ch"
  echo "13	hugendubel.de"
end

# Init
complete -c $PROG --erase # deletes any other completion
complete -c $PROG --no-files

# Subcommands
complete -c $PROG -n '__fish_tolino_needs_command' -a 'inventory'  -d 'Fetch and print inventory'
complete -c $PROG -n '__fish_tolino_needs_command' -a 'meta'       -d 'Update meta data of a book'
complete -c $PROG -n '__fish_tolino_needs_command' -a 'cover'      -d 'Update cover of a book'
complete -c $PROG -n '__fish_tolino_needs_command' -a 'upload'     -d 'Upload a file (must be either .pdf or .epub)'
complete -c $PROG -n '__fish_tolino_needs_command' -a 'download'   -d 'Download a document'
complete -c $PROG -n '__fish_tolino_needs_command' -a 'delete'     -d 'Delete a document (be careful!)'
complete -c $PROG -n '__fish_tolino_needs_command' -a 'devices'    -d 'List devices registered to cloud account'
complete -c $PROG -n '__fish_tolino_needs_command' -a 'unregister' -d 'Unregister device from cloud account (be careful!)'

# Options and flags
complete -c $PROG -s h -l help -d 'Show help message and exit'
complete -c $PROG -l user      -d 'username (usually an email address)' -x
complete -c $PROG -l config    -d 'config file (default: .tolinoclientrc)' -r
complete -c $PROG -l password  -d 'password' -x
complete -c $PROG -l partner   -d 'shop/partner ID' -x -a "(__fish_tolino_partners)"
complete -c $PROG -l debug     -d 'Log additional debugging info'

# Completion for parameters and subcommands
complete -c $PROG -n '__fish_tolino_uses_command upload' -a "(__fish_complete_path)" -x
