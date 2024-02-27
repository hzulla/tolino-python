#!/usr/bin/env python3

# tolino cloud command line client
# call without parameters for a brief help message
# you can use a ".tolinoclientrc" config file

import configparser
import argparse
import sys
import datetime
import logging
from os.path import expanduser
import getpass

from tolinocloud import TolinoCloud


class PasswordPromptAction(argparse.Action):
    '''
    class to prompt for password if none is specified on the command line
    '''
    def __call__(self, parser, args, values, option_string=None):
        # If no value is given on the commandline prompt for password.
        if values:
            # Ideally a security warning could be generated here.
            setattr(args, self.dest, values)
        else:
            setattr(args, self.dest, getpass.getpass())


def inventory(args):
    c = TolinoCloud(args.partner)
    c.login(args.user, args.password)
    c.register()
    inv = c.inventory()
    c.unregister()
    c.logout()
    print('{} document{} stored in tolino cloud account {}'.format(len(inv), 's' if len(inv) > 1 else '', args.user))
    for i in inv:
        print('')
        print('id        : {}'.format(i['id']))
        print('title     : {}'.format(i['title']))
        print('subtitle  : {}'.format(i['subtitle']))
        for a in i['author']:
            if a:
                print('author    : {}'.format(a))
        print('mimetype  : {}'.format(i['mime']))
        print('type      : {} / {}'.format(i['type'], {
                'edata' : 'user storage area',
                'ebook' : 'tolino storage area'
            }.get(i['type'], i['type'])
        ))
        if 'issued' in i:
            print('issued    : {}'.format(datetime.datetime.fromtimestamp(i['issued']/1000.0).strftime('%c')))
        print('purchased : {}'.format(datetime.datetime.fromtimestamp(i['purchased']/1000.0).strftime('%c')))
        print('partner   : {} / {}'.format(i['partner'], TolinoCloud.partner_name[i['partner']]))


def devices(args):
    c = TolinoCloud(args.partner)
    c.login(args.user, args.password)
    devs = c.devices()
    c.logout()
    print('{} device{} connected to tolino cloud account {}'.format(len(devs), 's' if len(devs) > 1 else '', args.user))
    for d in devs:
        print('')
        print('device    : {}'.format(d['id']))
        print('type      : {}'.format(d['type']))
        print('name      : {}'.format(d['name']))
        print('partner   : {} / {}'.format(d['partner'], TolinoCloud.partner_name[d['partner']]))
        print('registered: {}'.format(datetime.datetime.fromtimestamp(d['registered']/1000.0).strftime('%c')))
        print('last use  : {}'.format(datetime.datetime.fromtimestamp(d['lastusage']/1000.0).strftime('%c')))

def unregister(args):
    c = TolinoCloud(args.partner)
    c.login(args.user, args.password)
    c.unregister(args.device_id)
    c.logout()
    print('unregistered device {} from tolino cloud.'.format(args.device_id))

def upload(args):
    c = TolinoCloud(args.partner)
    c.login(args.user, args.password)
    c.register()
    document_id = c.upload(args.filename, args.name)
    c.unregister()
    c.logout()
    print('uploaded {} to tolino cloud as {}.'.format(args.filename, document_id))

def download(args):
    c = TolinoCloud(args.partner)
    c.login(args.user, args.password)
    c.register()
    fn = c.download(None, args.document_id)
    c.unregister()
    c.logout()
    print('downloaded {} from tolino cloud to {}.'.format(args.document_id, fn))

def delete(args):
    c = TolinoCloud(args.partner)
    c.login(args.user, args.password)
    c.register()
    c.delete(args.document_id)
    c.unregister()
    c.logout()
    print('deleted {} from tolino cloud.'.format(args.document_id))


def list_partners(args):
    print('List of partner ids available:')
    for partner_id in sorted(TolinoCloud.partner_settings.keys()):
        print('{} : {}'.format(partner_id, TolinoCloud.partner_name[partner_id]))
    sys.exit(0)

parser = argparse.ArgumentParser(
    description='cmd line client to access personal tolino cloud storage space.'
)
parser.add_argument('--config', metavar='FILE', default='~/.tolinoclientrc', help='config file (default: .tolinoclientrc)')
args, remaining_argv = parser.parse_known_args()

if args.config:
    c = configparser.ConfigParser()
    c.read([expanduser(args.config)])
    if c.has_section('Defaults'):
        defaults = dict(c.items('Defaults'))
        parser.set_defaults(**defaults)

parser.add_argument('--user', '-u', type=str, help='username (usually an email address)')
parser.add_argument('--password', '-p', action=PasswordPromptAction, type=str, help='password. Leave empty for a password prompt', nargs='?')
parser.add_argument('--partner', type=int, help='shop / partner id')
parser.add_argument('--debug', action="store_true", help='log additional debugging info')

subparsers = parser.add_subparsers()

s = subparsers.add_parser('inventory', help='fetch and print inventory')
s.set_defaults(func=inventory)

s = subparsers.add_parser('upload', help='upload a file (must be either .pdf or .epub)')
s.add_argument('filename', metavar='FILE')
s.add_argument('--name', help='specify an alternative name')
s.set_defaults(func=upload)

s = subparsers.add_parser('download', help='download a document')
s.add_argument('document_id')
s.set_defaults(func=download)

s = subparsers.add_parser('delete', help='delete a document (be careful!)')
s.add_argument('document_id')
s.set_defaults(func=delete)

s = subparsers.add_parser('devices', help='list devices registered to cloud account')
s.set_defaults(func=devices)

s = subparsers.add_parser('unregister', help='unregister device from cloud account (be careful!)')
s.add_argument('device_id')
s.set_defaults(func=unregister)

s = subparsers.add_parser('list-partners', help='list devices registered to cloud account')
s.set_defaults(func=list_partners)

args = parser.parse_args(remaining_argv)

if args.debug:
    logging.basicConfig(level=logging.DEBUG)

if (not args.user) or (not args.password):
    print('Login credentials user/password required.')
    parser.print_help()
    sys.exit(1)

if not hasattr(args, 'func'):
    parser.print_help()
    sys.exit(1)

user = args.user
password = args.password
partner = args.partner
args.func(args)
