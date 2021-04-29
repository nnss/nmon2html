#!/usr/bin/env python3

import argparse as argparse
import logging
import re
import sys
from collections import OrderedDict

import jinja2 as jinja2

"""

Parser skell:

new hash:
{ AAA = {title: group(2),
         text: group(3) }
  BBBP = {title: group(2),
         text: group(3) }
  other_keys = { title: group(2),
                part: 'title',
                group(1): [ group(3).split(",") ]}
ZZZZ,(index_time)
  other_keys = { title: group(2),
                part: index_time,
                group(1): [ group(3).split(",") ]}

"""


class NMonHtmlConverter:
    def __init__(self, debug=0, file=None, logfile=None):
        if file is None:
            sys.stderr.write("The file was not specified, exiting")
            exit(127)
        self.file = file
        self.tmpl = "templates/simple.html.jinja"
        if debug >= 5:
            debug = 5
        if debug == 0:
            debug = 2
        if logfile is not None:
            logfile = sys.stderr
        self.logger = logging.getLogger(__name__)
        levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
        level = levels[min(len(levels) - 1, debug)]  # capped to number of levels
        self.logger.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler(logfile)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        self.skel = {'text': r'AAA|BBBP',
                     'procs': r'TOP',
                     'net': r'NET|NETPACKET',
                     'graph': r'CPU.*|DISK|MEM|JFS|VM|PROC',
                     }

    def proc_file(self):
        result_var = OrderedDict()
        time_key = 'title'
        with open(self.file) as lines:
            for line in lines:
                line = line.rstrip()
                self.logger.debug("LINE::" + line)
                m = re.match(r'^([^,]+)\s*,\s*([^,]+)\s*,\s*(.*)$', line)
                if m:
                    self.logger.info("group 1: '" + m.group(1) + "'")
                    #####
                    # the AAA section is just a 3 column info from the nmon
                    # and the execution
                    ##
                    if m.group(1) == "AAA":
                        if 'AAA' not in result_var:
                            result_var[m.group(1)] = OrderedDict()
                        result_var[m.group(1)][m.group(2)] = m.group(3)
                    ####
                    # the BBBP section is the system info part
                    elif m.group(1) == 'BBBP':
                        m = re.match(r'^([^,]+)\s*,\s*([^,]+)\s*,\s*([^,]+)\s*,?\s*(.*)?$', line)
                        if m.group(1) not in result_var:
                            result_var[m.group(1)] = OrderedDict()
                        text = m.group(4)[1:-1] if m.group(4) is not None else ""
                        if m.group(3) not in result_var[m.group(1)]:
                            result_var[m.group(1)][m.group(3)] = OrderedDict()
                            text = m.group(4)[1:-1] if m.group(4) is not None else ""
                            result_var[m.group(1)][m.group(3)] = text
                        elif text != "":
                            result_var[m.group(1)][m.group(3)] += text + "\n"
                    elif m.group(1) == "ZZZZ":
                        time_key = m.group(3).replace(",", " ")
                    else:
                        m = re.match(r'^([^,]+)\s*,\s*([^,]+)\s*,\s*([^,]+)\s*,\s*(.*)$', line)
                        if m.group(1) == 'ZZZZ':
                            time_key = m.group(3) + " " + m.group(4)
                        else:
                            m = re.match(r'^([^,]+)\s*,\s*([^,]+)\s*,\s*([^,]+)\s*,\s*(.*)$', line)
                            if m.group(1) not in result_var:
                                result_var[m.group(1)] = OrderedDict()
                            ####
                            # top is different, the sequence index is in the 3rd column, not
                            # in the second, and in the second hte PID is located, so I need
                            # to change that
                            # The rest is quite the same, the only change is in the data section
                            # that is from the 3r column to the last one, so instead of
                            # using just regex, I use a eager regex to catch all til the end fo the file,
                            # and split by the ","
                            if m.group(1) == "TOP":
                                result_var[m.group(1)][time_key] = {'order': m.group(3),
                                                                    'values': [m.group(2)] + m.group(4).split(",")
                                                                    }
                            else:
                                ######
                                # There are some issues as the VM header is nto defined before the first
                                # ZZZZ divisor, so I need to take care of not defined blocks even after the
                                # first ZZZZ divisor
                                ####
                                m = re.match(r'^([^,]+)\s*,\s*([^,]+)\s*,\s*(.*)$', line)
                                self.logger.debug("timekey " + str(time_key))
                                self.logger.debug("grp2 " + str(m.group(2)))
                                if time_key != "title" and 'title' not in result_var[m.group(1)]:
                                    result_var[m.group(1)]['title'] = {'order': m.group(2),
                                                                       'values': m.group(3).split(",")
                                                                       }
                                else:
                                    result_var[m.group(1)][time_key] = {'order': m.group(2),
                                                                        'values': m.group(3).split(",")
                                                                        }
        ####
        # it's nicer (IMHO) to see the sections in order
        ###
        result_var = OrderedDict(sorted(result_var.items()))
        return result_var

    ####
    # this is just a helper for the jinja template
    ##
    @staticmethod
    def m(regex, text):
        if re.match(regex, text):
            return True
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Takes mon file and prints a graphic in HTML.')
    parser.add_argument('-f', '--file', dest='file', help='the file to process (nmon file)', default=None)
    parser.add_argument('-d', '--debug', dest='debug', help='debug (more d more debug level)',
                        action="count", default=0)
    parser.add_argument('-v', '--version', dest='show_version', help='Show the version of the script',
                        action='store_true')
    parser.add_argument('-p', '--part', dest='part', help='Only this part', default=None)
    parser.add_argument('-o', '--output', dest='output', help='Specify the output file', default=None)
    parser.add_argument('-l', '--load', dest='vault', help='Set the path to load the JSs files', default=None)
    args = parser.parse_args()

    prg = NMonHtmlConverter(debug=args.debug, file=args.file)

    #
    info = prg.proc_file()
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = prg.tmpl
    template = templateEnv.get_template(TEMPLATE_FILE)
    outputText = template.render(info=info, meta=prg)  # this is where to put args to the template renderer
    if args.output is not None:
        with open(args.output, 'w+') as fd:
            fd.write(outputText)
    else:
        print(outputText)
