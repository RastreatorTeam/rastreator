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

    for op_mode in ['audit', 'check', 'execute', 'path', 'shell']:
        sp[op_mode] = subparsers.add_parser(
            op_mode,
            help = f'{op_mode.capitalize()} mode'
        )
        sp[op_mode].add_argument(
            '-v',
            choices = cparser['choices']['verbose']['mode'],
            dest = 'verbose_mode',
            default = dparser['verbose']['mode'],
            help = cparser['help']['verbose']['mode']
        )

    for op_mode in ['audit', 'execute', 'path', 'shell']:
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
            choices = cparser['choices']['neo4j']['encrypted'],
            dest = 'neo4j_encrypted',
            default = dparser['neo4j']['encrypted'],
            help = cparser['help']['neo4j']['encrypted']
        )

    for op_mode in ['audit', 'check', 'path']:
        sp[op_mode].add_argument(
            '-I',
            dest = 'input_directory_or_file',
            required = True,
            help = cparser['help']['input']['directory_or_file']
        )
        sp[op_mode].add_argument(
            '-O',
            dest = 'output_directory',
            default = dparser['output']['directory'],
            help = cparser['help']['output']['directory']
        )
        sp[op_mode].add_argument(
            '-o',
            choices = cparser['choices'][op_mode]['persistence']['format'],
            dest = 'persistence_format',
            default = dparser[op_mode]['persistence']['format'],
            help = cparser['help']['persistence']['format']
        )

    for op_mode in ['audit', 'path']:
        sp[op_mode].add_argument(
            '-f',
            choices = cparser['choices']['output']['format'],
            dest = 'output_format',
            default = dparser['output']['format'],
            help = cparser['help']['output']['format']
        )
        sp[op_mode].add_argument(
            '-l',
            choices = cparser['choices']['ad']['lang'],
            dest = 'ad_lang',
            default = dparser['ad']['lang'],
            help = cparser['help']['ad']['lang']
        )
        sp[op_mode].add_argument(
            '-d',
            dest = 'ad_domain',
            required = True,
            help = cparser['help']['ad']['domain']
        )
        sp[op_mode].add_argument(
            '-m',
            choices = cparser['choices']['query']['mode'],
            dest = 'query_mode',
            default = dparser['query']['mode'],
            help = cparser['help']['query']['mode']
        )

    for op_mode in ['path']:
        sp[op_mode].add_argument(
            '-S',
            dest = 'start_node',
            default = dparser[op_mode]['start_node'],
            help = cparser['help'][op_mode]['start_node']
        )
        sp[op_mode].add_argument(
            '-E',
            dest = 'end_node',
            default = dparser[op_mode]['end_node'],
            help = cparser['help'][op_mode]['end_node']
        )
        sp[op_mode].add_argument(
            '-s',
            choices = cparser['choices'][op_mode]['has_session'],
            dest = 'has_session',
            default = dparser[op_mode]['has_session'],
            help = cparser['help'][op_mode]['has_session']
        )

    for op_mode in ['execute']:
        sp[op_mode].add_argument(
            '-c',
            dest = 'command',
            help = cparser['help'][op_mode]['command']
        )

    Terminal(ap.parse_args())
