#!/usr/bin/python3

 #
 # This file is part of the PySourceCloze distribution
 # (https://github.com/gurivier/pysourcecloze).
 # Copyright (c) 2022 Guillaume RIVIERE.
 #
 # This program is free software: you can redistribute it and/or modify
 # it under the terms of the GNU General Public License as published by
 # the Free Software Foundation, version 3.
 #
 # This program is distributed in the hope that it will be useful, but
 # WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 # General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License
 # along with this program. If not, see <http://www.gnu.org/licenses/>.
 #

import json
import re
import os
import operator
from functools import reduce

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def fopen(filename, mode):
    try:
        f = open(filename, mode)
        return f
    except Exception as e:
        eprint(f'Error: {e}')
        sys.exit(1)

class SourceCloze(object):

    def __init__(self, delimiter='§'):
        self.delimiter = delimiter
        self.lexicon = []
        self.all_patterns = []

    def load_lexicon_from_file(self, lexicon_filename):
        with fopen(lexicon_filename, 'r') as f:
            lexicon = json.load(f)
            for entry in lexicon:
                points = entry['points']
                patterns = '|'.join(entry['patterns'])
                self.lexicon.append((points, patterns))
                self.all_patterns.extend(entry['patterns'])
            self.all_patterns.sort(key=len, reverse=True)

    def load_lines_from_file(self, source_filename):
        with fopen(source_filename, 'r') as f:
            lines = [line.rstrip() for line in f]
        return lines

    def enclose_lines_with_delimiter(self, lines):
        d = self.delimiter
        enclosed_lines = []
        patterns = '|'.join(self.all_patterns)
        pattern1_re = f'({patterns})'
        replace1_s = f'{d}\\1{d}'
        for line in lines:
            line = re.sub(pattern1_re, replace1_s, line)
            for points, patterns in self.lexicon:
                pattern2_re = f'{d}({patterns}){d}'
                replace2_s = f'{d}{points}{d}\\1{d}'
                line = re.sub(pattern2_re, replace2_s, line)
            enclosed_lines.append(line)
        return enclosed_lines

    def insert_lines_points(self, lines, outer_points=10):
        d = self.delimiter
        points_lines = []
        for line in lines:
            for points, patterns in self.lexicon:
                pattern_re = f'{d}{d}({patterns}){d}'
                replace_s = f'{d}{points}{d}\\1{d}'
                line = re.sub(pattern_re, replace_s, line)
            pattern_re = f'{d}{d}([^{d}]*){d}'
            replace_s = f'{d}{outer_points}{d}\\1{d}'
            line = re.sub(pattern_re, replace_s, line)
            points_lines.append(line)
        return points_lines

    def clean_lines_to_raw(self, lines):
        d = self.delimiter
        raw_lines = [re.sub(f'{d}[^{d}]*{d}([^{d}]*){d}', r'\1', line) for line in lines]
        return f'{os.linesep}'.join(raw_lines)

    def count_points_per_pattern(self, lines):
        d = self.delimiter
        count = dict()
        for line in lines:
            matches = re.findall(f'{d}([^{d}]*){d}([^{d}]*){d}', line)
            for points, pattern in matches:
                if pattern not in count:
                    count.update({pattern: int(points)})
                else:
                    count[pattern] += int(points)
        return count

    def show_points_per_pattern(self, count):
        total_points = sum(count.values())
        patterns_count = sorted(list(count.items()), key=operator.itemgetter(1), reverse=True)
        print('   Points    Percent    Pattern')
        for pattern, points in patterns_count:
            percent = points * 100 / total_points
            print(f'     {points:4d}       {percent:3.0f}%    {pattern}')
        s_pt = 's' if total_points != 1 else ''
        s_pa = 's' if len(patterns_count) != 1 else ''
        print(f'  {total_points:7d} pt{s_pt}           {len(patterns_count)} pattern{s_pa}')

    def convert_lines_to_cloze(self, lines):
        d = self.delimiter
        pattern_re = f'{d}([^{d}]*){d}([^{d}]*){d}'
        replace_s = f'{{\\1:SAC:=\\2}}'
        cloze_lines = [re.sub(pattern_re, replace_s, line) for line in lines]
        matches = [match for line in lines for match in re.findall(f'{d}[^{d}]*{d}([^{d}]*){d}', line)]
        sizes = [len(match) for match in matches]
        return cloze_lines, sizes

    def replace_chevrons_to_html(self, lines):
        replacers = ('<', '&lt;'), ('>', '&gt;')
        return [reduce(lambda a, kv: a.replace(*kv), replacers, line) for line in lines]

    def dress_lines_with_html_ol(self, lines, cloze_id, sizes):
        html_lines = [f'<ol id="{cloze_id}" class="cloze">']
        html_lines.extend([f'<li>{line}</li>' for line in lines])
        html_lines.append('</ol>')
        html_lines = self.add_script_lines(html_lines, cloze_id, sizes)
        return html_lines

    def dress_lines_with_html_pre(self, lines, cloze_id, sizes):
        html_lines = [f'<pre id="{cloze_id}" class="cloze">']
        html_lines.extend(lines)
        html_lines.append('</pre>')
        html_lines = self.add_script_lines(html_lines, cloze_id, sizes)
        return html_lines

    def add_script_lines(self, html_lines, cloze_id, sizes):
        html_lines.append(f'<script>SourceCloze(\'{cloze_id}\', {sizes})</script>')
        return html_lines

    @classmethod
    def give_xml_question(cls, type, data_dirpath, html, sourcename, penalty='0.3333333'):
        with fopen(os.path.join(data_dirpath, 'template', 'question.xml.tpl'), 'r') as f:
            xml = f.read().format(type=type, sourcename=sourcename, html=html, penalty=penalty)
        return xml

def get_program_parameters(version):
    import argparse, textwrap
    parser = argparse.ArgumentParser(description='PySourceCloze generates Moodle clozes from source codes using decorated source files')
    parser.add_argument('-v', '--version', action='version', version=version, help='show program version and exit')
    subparsers = parser.add_subparsers(title='required arguments', required=True, dest='command', metavar='command',
                                       help='command name (or alias)')
    parsers = {
        'e': subparsers.add_parser('enclose', aliases=['e'],
                                   help='enclose lexemes (i.e., lexeme => §pts§lexeme§)',
                                   description='enclose in source file the lexemes from lexicon (i.e., lexeme => §pts§lexeme§)'),
        'f': subparsers.add_parser('fill', aliases=['f'],
                                   help='fill points of empty patterns (i.e., §§pattern§ => §pts§pattern§)',
                                   description='fill empty points in source file (i.e., §§pattern§ => §pts§pattern§);\npoints are set from then lexicon or set to OUTERS_POINTS for patterns out of the lexicon'),
        'c': subparsers.add_parser('clean', aliases=['c'],
                                   help='clean to show back raw code (i.e., §*§pattern§ => pattern)',
                                   description='clean to show back raw code from source file (i.e., §*§pattern§ => pattern)'),
        's': subparsers.add_parser('sum', aliases=['s'],
                                   help='show summed points per pattern and distribution among total points',
                                   description='show summed points per pattern in source file and distribution among total points'),
        'g': subparsers.add_parser('generate', aliases=['g'],
                                   help='generate the HTML or XML cloze question for Moodle',
                                   description='generate the HTML or XML cloze question for Moodle'),
        'i': subparsers.add_parser('init', aliases=['i'],
                                   help='get the HTML or XML description embedding instructions and init script for Moodle',
                                   description='get the HTML or XML description that will embed instructions and init script for Moodle (to insert as first question on each page)'),
        'u': subparsers.add_parser('updates', aliases=['u'],
                                   help='check if a new release is available and exit',
                                   add_help=False),
    }
    for p in ('e', 'f', 'c', 's', 'g'):
        parsers[p].add_argument('-d', '--delimiter', nargs=1, type=str, default='§', help='the source file delimiter (default: §, alternative: £)')
        if p not in ('c', 's', 'g'):
            parsers[p].add_argument('lexicon_file', nargs=1, type=str, help='the lexicon JSON file')
        parsers[p].add_argument('source_file', nargs=1, type=str, help='the source file to read')
    for p in ('g', 'i'):
        parsers[p].add_argument('-qt', '--question-text', dest='question_file', nargs=1, type=str, help='question\'s text file in raw HTML code')
    parsers['f'].add_argument('outers_points', nargs=1, type=str, help='points given for patterns out of lexicon')
    parsers['g'].add_argument('output_mode', nargs=1, type=str, help=textwrap.dedent('''\
    output mode
      XML                cloze question in Moodle XML file structure
      XML-NUMS           numbered cloze question in Moodle XML file structure
      HTML               cloze in raw HTML code
      HTML-NUMS          numbered cloze in raw HTML code
    '''))
    parsers['i'].add_argument('lang', nargs=1, type=str, help=textwrap.dedent('''\
    instructions\' version
      EN                 English version
      FR                 French version
    '''))
    parsers['i'].add_argument('output_mode', nargs=1, type=str, help=textwrap.dedent('''\
    output mode
      XML                question in Moodle XML file structure
      HTML               raw HTML code
    '''))
    for p in ('e', 'f', 'g', 'i'):
        parsers[p].add_argument('-p', '--print', action='store_true', help='print result on standard output (not in file)')
    information = textwrap.dedent(f'''\
    further information:
      project directory    https://github.com/gurivier/pysourcecloze
      documentation        https://github.com/gurivier/pysourcecloze/wiki
    ''')
    usages = ''.join(['  '+p.format_usage().strip('usage: ') for p in parsers.values()])
    parser.formatter_class = argparse.RawTextHelpFormatter
    parser.epilog = textwrap.dedent(f'commands usage:\n{usages}\n{information}')
    for subparser in parsers.values():
        subparser.formatter_class = argparse.RawTextHelpFormatter
        subparser.epilog = information
    args = parser.parse_args()
    return args

def get_program_paths():
    script_path = os.path.dirname(os.path.realpath(__file__))
    installation_path = os.getenv('PYSOCLZ_INSTALL_DIR', script_path)
    data_dirpath = os.path.join(installation_path, 'data')
    if not os.path.isdir(data_dirpath):
        eprint('Error: cannot access \'data\' dir.')
        eprint('If you moved or linked \'pysoclz.py\', set the environment variable PYSOCLZ_INSTALL_DIR to the installation directory.')
        sys.exit(1)
    return installation_path, data_dirpath

def get_version(installation_path):
    import importlib
    return importlib.import_module('_version', installation_path).__version__

def check_for_new_version(cur_version, installation_path):
    import requests
    try:
        resp = requests.get('https://api.github.com/repos/gurivier/pysourcecloze/releases/latest')
        if resp:
            new_version = resp.json()['name'].split(' ')[1]
            if new_version > cur_version:
                print(f'Update available: PySourceCloze release {new_version} is available.\n')
                print(f'  Upgrade from installation dir:')
                print(f'    cd {installation_path}')
                print(f'    git clone https://github.com/gurivier/pysourcecloze.git\n')
                sys.exit(1)
            else:
                print(f'PySourceCloze {cur_version} is already the lastest release.')
        else:
            from http.client import responses
            eprint(f'Error: could not check for updates: Error {resp.status_code} {responses[resp.status_code]}.')
    except HTTPError as e:
        eprint(f'Error: could not check for updates: {e}')
    except requests.exceptions.ConnectionError as e:
        eprint('Error: could not check for updates: network connection error.')
    except requests.exceptions.ConnectionError as e:
        eprint('Error: could not check for updates: connection has timeout.')
    except requests.exceptions.RequestException as e:
        eprint(f'Error: could not check for updates: {e}')

def check_input_filename(args):
    bad_extension = False
    if args.command in ('g', 'generate', 's', 'sum', 'c', 'clean'):
        source_filename = args.source_file[0]
        if source_filename[-4:] != '.clo':
            eprint(f'Error: a \'.clo\' file type is required for source_file.')
            bad_extension = True
    if args.command in ('e', 'enclose', 'f', 'fill'):
        lexicon_filename = args.lexicon_file[0]
        if lexicon_filename[-5:] != '.json':
            eprint(f'Error: a \'.json\' file type is required for lexicon_file.')
            bad_extension = True        
    if bad_extension:
        sys.exit(1)
        
def get_ouput_file(args):
    import ntpath
    output_filename = None
    output_file = None
    if hasattr(args, 'print') and not args.print:
        if args.command in ('i', 'init'):
            has_question_file = hasattr(args, 'question_file') and args.question_file is not None
            i_lang = args.lang[0].lower()
            i_mode = args.output_mode[0].lower()
            path = os.path.dirname(args.question_file[0]) if has_question_file else '.'
            name = ntpath.basename(args.question_file[0]).split('.')[0] if has_question_file else 'sourcecloze'
            output_filename = os.path.join(path, f'{name}-instructions-{i_lang}.ini.{i_mode}.new')
        elif args.command in ('g', 'generate'):
            source_filename = args.source_file[0].removesuffix('.clo')
            mode = args.output_mode[0].split('-')[0].lower()
            output_filename = f'{source_filename}.clz.{mode}.new'
        elif args.command in ('f', 'fill', 'e', 'enclose'):
            source_filename = args.source_file[0].removesuffix('.clo')
            output_filename = f'{source_filename}.clo.new'
    if output_filename is not None:
        print(f'Output filename: \'{output_filename.removesuffix(".new")}\'')
        output_file = fopen(output_filename, 'w')
    return output_file, output_filename

def get_question_file(args):
    has_question_file = hasattr(args, 'question_file') and args.question_file is not None
    question_lines = []
    if has_question_file:
        question_filename = args.question_file[0]
        question_lines = [line.rstrip() for line in fopen(question_filename, 'r')]
    return has_question_file, question_lines

def rename_new_file(output_filename_new, bak=True):
    import shutil
    output_filename = output_filename_new.removesuffix('.new')
    if bak and os.path.isfile(output_filename):
        shutil.move(output_filename, f'{output_filename}.bak')
    shutil.move(output_filename_new, output_filename)

def delete_openned_file(filename, desc):
    if desc is not None:
        desc.close()
    os.remove(filename)

def put(output_file, text):
    if output_file is not None:
        output_file.write(f'{text}{os.linesep}')
    else:
        print(text)

def main():
    import ntpath
    installation_path, data_dirpath = get_program_paths()
    cur_version = get_version(installation_path)
    args = get_program_parameters(cur_version)
    if args.command in ('u', 'updates'):
        check_for_new_version(cur_version, installation_path)
        sys.exit(1)
    check_input_filename(args)
    output_file, output_filename = get_ouput_file(args)
    has_question_file, question_lines = get_question_file(args)
    if args.command in ('i', 'init'):
        i_lang = args.lang[0].lower()
        i_mode = args.output_mode[0].upper()
        instructions_filename = f'{data_dirpath}/instructions/instructions_{i_lang}.inc.html'
        if not os.path.isfile(instructions_filename):
            eprint('Error: lang file not found \'{instructions_filename}\'')
            delete_openned_file(output_filename, output_file)
            sys.exit(1)
        else:
            instructions_lines = [line.rstrip() for line in fopen(instructions_filename, 'r')]
            script_filename = f'{data_dirpath}/init/script.js'
            script_lines = ['<script>'] + [line.rstrip() for line in fopen(script_filename, 'r')] + ['</script>']
            chooser_filename = f'{data_dirpath}/instructions/color_chooser.inc.html'
            chooser_lines = [line.rstrip() for line in fopen(chooser_filename, 'r')]
            html_lines = instructions_lines + script_lines + chooser_lines + question_lines
            if i_mode == 'XML':
                question_name = ntpath.basename(args.question_file[0]).split('.')[0] if has_question_file else 'sourcecloze'
                question_id = f'{question_name}-instructions-{i_lang}-init'
                html = ''.join(html_lines)
                xml = SourceCloze.give_xml_question('description', data_dirpath, html, question_id, 0)
                put(output_file, xml)
            elif i_mode == 'HTML':
                html = f'{os.linesep}'.join(html_lines)
                put(output_file, html)
            else:
                eprint(f'Error: unknown output mode \'{i_mode}\'')
                delete_openned_file(output_filename, output_file)
                sys.exit(1)
    else:
        sc = SourceCloze(args.delimiter)
        source_filename = args.source_file[0]
        lines = sc.load_lines_from_file(source_filename)
        if args.command in ('c', 'clean'):
            raw = sc.clean_lines_to_raw(lines)
            put(output_file, raw)
        elif args.command in ('s', 'sum'):
            count = sc.count_points_per_pattern(lines)
            sc.show_points_per_pattern(count)
        elif args.command in ('g', 'generate'):
            mode = args.output_mode[0].upper()
            sourcename = ntpath.basename(source_filename).removesuffix('.clo')
            cloze_id = sourcename.replace('.', '_')
            clozes, sizes = sc.convert_lines_to_cloze(lines)
            lines = sc.replace_chevrons_to_html(clozes)
            if mode == 'XML':
                html_lines = sc.dress_lines_with_html_pre(lines, cloze_id, sizes)
                html = f'{os.linesep}'.join(question_lines + html_lines)
                xml = sc.give_xml_question('cloze', data_dirpath, html, sourcename)
                put(output_file, xml)
            elif mode == 'XML-NUMS':
                html_lines = sc.dress_lines_with_html_ol(lines, cloze_id, sizes)
                html = ''.join(question_lines + html_lines)
                xml = sc.give_xml_question('cloze', data_dirpath, html, sourcename)
                put(output_file, xml)
            elif mode == 'HTML':
                html_lines = sc.dress_lines_with_html_pre(lines, cloze_id, sizes)
                html = f'{os.linesep}'.join(question_lines + html_lines)
                put(output_file, html)
            elif mode == 'HTML-NUMS':
                html_lines = sc.dress_lines_with_html_ol(lines, cloze_id, sizes)
                html = f'{os.linesep}'.join(question_lines + html_lines)
                put(output_file, html)
            else:
                eprint(f'Error: unknown output mode \'{mode}\'')
                delete_openned_file(output_filename, output_file)
                sys.exit(1)
        else:
            lexicon_filename = args.lexicon_file[0]
            sc.load_lexicon_from_file(lexicon_filename)
            if args.command in ('f', 'fill'):
                outers_points = args.outers_points[0]
                lines = sc.insert_lines_points(lines, outers_points)
                put(output_file, f'{os.linesep}'.join(lines))
            elif args.command in ('e', 'enclose'):
                lines = sc.enclose_lines_with_delimiter(lines)
                put(output_file, f'{os.linesep}'.join(lines))
    if output_file is not None:
        output_file.close()
        rename_new_file(output_filename)

if __name__ == '__main__':
    import sys
    exit_code = main()
    sys.exit(exit_code)
