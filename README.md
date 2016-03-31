# Netezza-SQL-Schema-CSV

Infer the SQL schema for the IBM PureData Analytics Platform (a.k.a. Netezza)
from a .csv file.

This script will try to interpret the columns in a .csv file and match
them to Netezza's built-in types:

## Supported Types

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

## Usage

    inferSchema.py [-h] [--input_encoding INPUT_ENCODING]
                   [--separator SEPARATOR]
                    csv_file output_file

    positional arguments:
      csv_file              input .csv file
      output_file           output file name, will be overwritten
    
    optional arguments:
      -h, --help            show this help message and exit
      --input_encoding INPUT_ENCODING, -e INPUT_ENCODING
                            input file encoding (default: utf8)
      --separator SEPARATOR, -s SEPARATOR
                            separator that is used in the .csv file (default: ',')
