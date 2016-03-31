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
import argparse
from parsers import getNetezzaParser

def mkScheme(column_names, parsers):
    return u",\n".join(u"{0} {1}".format(column_name,
                                         str(parser))
                      for column_name, parser in
                      zip(column_names, parsers))

def parseFile(fileName, outputFileName, encoding, separator):
    with io.open(fileName, encoding=encoding) as input_file:
        column_names = input_file.readline()[:-1].split(separator)
        parsers = [getNetezzaParser() for i in range(len(column_names))]
        for i, line in enumerate(input_file):
            if i % 5000 == 0:
                print "Processed {0} lines.".format(i)
            parsers = [parser(input_string)
                            for parser, input_string in
                            zip(parsers, line[:-1].split(separator))]
    with io.open(outputFileName, "w", encoding="utf8") as out_file:
        out_file.write(mkScheme(column_names, parsers))

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
    args = parser.parse_args()
    parseFile(args.csv_file, args.output_file, args.input_encoding,
              args.separator)
