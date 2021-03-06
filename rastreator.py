#!/usr/bin/env python3


from argparse import ArgumentParser, RawTextHelpFormatter
from conf.constants import banner, parser as cparser
from conf.defaults import parser as dparser
from modules.controller import Terminal


if __name__ == '__main__':

    ap = ArgumentParser(
        description = f'{banner}',
        formatter_class=RawTextHelpFormatter
    )

    subparsers = ap.add_subparsers(required = True, dest = 'op_mode')
    sp = {}

    for op_mode in ['check', 'command', 'execute', 'interactive']:
        sp[op_mode] = subparsers.add_parser(
            op_mode,
            help = f'{op_mode.capitalize()} mode'
        )
        sp[op_mode].add_argument(
            '-v',
            dest = 'verbose_mode',
            default = dparser['verbose']['mode'],
            choices = cparser['choices']['verbose']['mode'],
            help = cparser['help']['verbose']['mode']
        )

    for op_mode in ['command', 'execute', 'interactive']:
        sp[op_mode].add_argument(
            '-H',
            dest = 'neo4j_host',
            default = dparser['neo4j']['host'],
            help = cparser['help']['neo4j']['host']
        )
        sp[op_mode].add_argument(
            '-P',
            dest = 'neo4j_port',
            default = dparser['neo4j']['port'],
            help = cparser['help']['neo4j']['port']
        )
        sp[op_mode].add_argument(
            '-u',
            dest = 'neo4j_username',
            default = dparser['neo4j']['username'],
            help = cparser['help']['neo4j']['username']
        )
        sp[op_mode].add_argument(
            '-p',
            dest = 'neo4j_password',
            default = dparser['neo4j']['password'],
            help = cparser['help']['neo4j']['password']
        )
        sp[op_mode].add_argument(
            '-e',
            dest = 'neo4j_encrypted',
            default = dparser['neo4j']['encrypted'],
            choices = cparser['choices']['neo4j']['encrypted'],
            help = cparser['help']['neo4j']['encrypted']
        )

    for op_mode in ['check', 'execute']:
        sp[op_mode].add_argument(
            '-I',
            dest = 'input_directory_or_file',
            default = dparser['input']['directory_or_file'],
            help = cparser['help']['input']['directory_or_file']
        )
        sp[op_mode].add_argument(
            '-O',
            dest = 'output_directory',
            default = dparser['output']['directory'],
            help = cparser['help']['output']['directory']
        )

    for op_mode in ['check']:
        sp[op_mode].add_argument(
            '-o',
            dest = 'persistence_format',
            default = dparser['check']['persistence']['format'],
            choices = cparser['choices']['check']['persistence']['format'],
            help = cparser['help']['persistence']['format']
        )

    for op_mode in ['execute']:
        sp[op_mode].add_argument(
            '-o',
            dest = 'persistence_format',
            default = dparser['execute']['persistence']['format'],
            choices = cparser['choices']['execute']['persistence']['format'],
            help = cparser['help']['persistence']['format']
        )
        sp[op_mode].add_argument(
            '-m',
            dest = 'execute_mode',
            default = dparser['execute']['mode'],
            choices = cparser['choices']['execute']['mode'],
            help = cparser['help']['execute']['mode']
        )
        sp[op_mode].add_argument(
            '-f',
            dest = 'output_format',
            default = dparser['output']['format'],
            choices = cparser['choices']['output']['format'],
            help = cparser['help']['output']['format']
        )
        sp[op_mode].add_argument(
            '-l',
            dest = 'ad_lang',
            default = dparser['ad']['lang'],
            choices = cparser['choices']['ad']['lang'],
            help = cparser['help']['ad']['lang']
        )
        sp[op_mode].add_argument(
            '-d',
            dest = 'ad_domain',
            required = True,
            help = cparser['help']['ad']['domain']
        )

    for op_mode in ['command']:
        sp[op_mode].add_argument(
            '-c',
            dest = 'command',
            help = cparser['help']['shell']['command']
        )

    Terminal(ap.parse_args())
