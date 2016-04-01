#!/usr/bin/env python
"""Infer the SQL schema for the IBM PureData Analytics Platform (a.k.a. Netezza)
from a .csv file.

This script will try to interpret the columns in a .csv file and match
them to Netezza's built-in types:

CHAR(N)
VARCHAR(N)
NCHAR(N)
NVARCHAR(N)

BYTEINT   8-bit signed integer
SMALLINT 16 bit signed integer
INTEGER  32 bit signed integer
BIGINT   64 bit signed integer

REAL
DOUBLE PRECISION

DATE
TIME
DATETYPE

NOTE: Some of the officially supported types are not used here!
"""

import io
import re
import argparse
import parsers

def mkScheme(column_names, parsers):
    return u",\n".join(u"{0} {1}".format(column_name,
                                         str(parser))
                      for column_name, parser in
                      zip(column_names, parsers))

def quoteColumnNames(column_names):
    """Add quotes around non-standard column names that Netezza allows."""
    for name in column_names:
        if re.search('[^A-Z_]', name):
            yield u'"{0}"'.format(name)
        else:
            yield name

def parseFile(fileName, outputFileName, encoding, separator):
    with io.open(fileName, encoding=encoding) as input_file:
        column_names = list(quoteColumnNames(
            input_file.readline()[:-1].split(separator)))
        column_parsers = [parsers.getNetezzaParser() for i in column_names]
        for i, line in enumerate(input_file):
            if i % 5000 == 0:
                print "Processed {0} lines.".format(i)
            column_parsers = [parser(input_string)
                            for parser, input_string in
                            zip(column_parsers, line[:-1].split(separator))]
    with io.open(outputFileName, "w", encoding="utf8") as out_file:
        out_file.write(mkScheme(column_names, column_parsers))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_file',
                        help="input .csv file")
    parser.add_argument('output_file',
                        help="output file name, will be overwritten")
    parser.add_argument('--input_encoding', '-e', default='utf8',
                        help="input file encoding (default: utf8)")
    parser.add_argument('--separator', '-s', default=',',
                        help=("separator that is used in the .csv file"
                              " (default: ',')"))
    parser.add_argument('--dateformat', '-d',
                        help=("date parsing format, as python regular"
                              " expression (default: '\d{4}\-\d{2}\-\d{2}')"))
    parser.add_argument('--timeformat', '-t',
                        help=("date parsing format, as python regular"
                              " expression (default: '\d{2}:\d{2}:d{2}')"))
    parser.add_argument('--datetimeformat', '-dt',
                        help=("date parsing format, as python regular"
                              " expression (default: "
                              "'\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:d{2}')"))
    args = parser.parse_args()
    parsers.DateParser.format_string = \
        args.dateformat or parsers.DateParser.format_string
    parsers.TimeParser.format_string = \
        args.timeformat or parsers.TimeParser.format_string
    parsers.DateTimeParser.format_string = \
        args.dateformat or parsers.DateTimeParser.format_string
    parseFile(args.csv_file, args.output_file, args.input_encoding,
              args.separator)
