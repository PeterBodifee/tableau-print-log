#!/usr/bin/env python

VERSION='0.1'

# standard library imports
import sys
import argparse
import fileinput
import signal
import textwrap
import json 

# signal handler
def signal_handler(signal, frame):
    exit(0)

# command line parser
def get_cli_parser():

    # possible values for the severity filter
    sev_filter_list=['info','warn','error']
    
    # list of message types on which can be filtered.
    type_filter_list=['msg',
                      'dll-version-info',
                      'open-log',
                      'startup-info',
                      'memory-usage',
                      'environment',
                      'display-device',
                      'command-pre',
                      'command-post',
                      'set-collation',
                      'end-ds-connect',
                      'ds-parser-connect',
                      'end-ds-parser-connect',
                      'ds-connect-data-connection',
                      'end-ds-connect-data-connection',
                      'construct-protocol',
                      'construct-protocol-group',
                      'protocol-added-to-group',
                      'begin-query',
                      'query-category',
                      'query-plan',
                      'end-query',
                      'get-cached-query',
                      'optimal-mode-factors',
                      'cache-freshness',
                      'mem-mc-load',
                      'ec-load',
                      'eqc-load',
                      'eqc-store',
                      'ds-load-metadata',
                      'read-metadata'
                     ]
    
    # set up the argument parser
    parser = argparse.ArgumentParser(
        description='Print human readable Tableau log files')
    
    # version option
    parser.add_argument('--version', 
                        action='version', 
                        version=VERSION
                        )
    # debug option
    parser.add_argument("--debug",
                        action="store_true",
                        dest="Debug",
                        default=False,
                        help=argparse.SUPPRESS
                       )

    # severity parameter (optional)
    parser.add_argument("--severity",
                        metavar="SEVERITY",
                        nargs='+',
                        dest="severity_filter",
                        choices=sev_filter_list,
                        default="",
                        help='specifiy the severity for filtering, '
                             +'values can be: '
                             +', '.join(sev_filter_list)
                       )
    
    # message type paramater (optional)
    parser.add_argument("--type",
                        metavar="MESSAGE_TYPE",
                        nargs='+',
                        dest="message_type",
                        choices=type_filter_list,
                        default="",
                        help='specifiy the message type severity for \
                              filtering, values can be: '
                             +', '.join(type_filter_list)
                       )
    
    # input file parameter (optional, otherwise std input)
    parser.add_argument("--file",
                        nargs='+',
                        dest="log_file",
                        help='specify the log file(s) to be printed. \
                              Otherwise standard input will be taken'
                       )
    
    return parser


def print_line(line_in_logfile, sev_filter=None, type_filter=None):
    # set up text wrapper for long string messages
    wp = textwrap.TextWrapper(width=80,
                              initial_indent=' '*4, 
                              subsequent_indent=' '*4)

    # decode the JSON formatted log entry into a Dict
    line=json.loads(line_in_logfile) 

    # the actual log message is in "v" and its type is keyed with "k"
    msg_timestamp=line["ts"]
    msg_severity=line["sev"]
    msg_type=line["k"]
    log_msg=line["v"]

    # don't print when severity is not in a filter when set
    if sev_filter:
        if not msg_severity in sev_filter:
            return
 
    # don't print when type is not in filter when set
    if type_filter:
        if not msg_type in type_filter:
            return
 

    # print format of the log msg depends on type
    # it maybe another JSON formatted message (python dict)
    if isinstance(log_msg, dict):
        # read all items in dictionary and put each key,val on one line
        msg='\n'.join("    {:16s}: {}".
                      format(k,v) for k,v in log_msg.items()) 
    elif isinstance(log_msg, str):
        # wrap message with wrapper so it wrap before 80th column
        msg=wp.fill(log_msg)
    else:
        # type we are not expecting to see.
        msg='>   message has type '+type(log_msg)

    # output log entry
    print("-"*80)
    print("{t} | {s:6} | {k} :\n{m}".
          format(t=msg_timestamp,
                 s=msg_severity,
                 k=msg_type,
                 m=msg
                )
         )
    return

def main():

    # catch OS interrupt signal for a normal termination
    signal.signal(signal.SIGINT, signal_handler)
    # catch OS broken pipe for a normal termination
    signal.signal(signal.SIGPIPE, signal_handler)
    
    # process command line arguments.
    args = get_cli_parser().parse_args()

    if args.Debug:
        print ("="*80)
        print ("DEBUG severity_filter:", args.severity_filter)
        print ("DEBUG message_type   :", args.message_type)
        print ("DEBUG log_file       :", args.log_file)
        print ("="*80)

    # if no filenames on cli, create empty list for fileinput
    if args.log_file is None:
        args.log_file = []

    # loop over all lines in all files (or stdin when empty)
    try:
        for line in fileinput.input(args.log_file):
            print_line(line,
                   sev_filter=args.severity_filter,
                   type_filter=args.message_type)
    except Exception as e:
        print(str(e), file=stderr)
    return

if __name__ == "__main__":
    main()


