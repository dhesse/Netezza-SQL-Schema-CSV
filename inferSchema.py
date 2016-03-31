import io
import sys
import re

class StringParser(object):
    valid = True
    def __init__(self):
        self.lengths_seen = set()
        self.is_ascii = True
    def __call__(self, input_string):
        self.lengths_seen.add(len(input_string))
        if self.is_ascii:
            if not all(ord(c) < 128 for c in input_string):
                self.is_ascii = False
        return self
    def __str__(self):
        if len(self.lengths_seen) == 1:
            fmt_string = "CHAR({0})"
        else:
            fmt_string = "VARCHAR({0})"
        if not self.is_ascii:
            fmt_string = "N" + fmt_string
        return fmt_string.format(max(self.lengths_seen))

class FloatParser(object):
    def __init__(self):
        self.valid = True
        self.digits = 0
    def __call__(self, input_string):
        if not re.match('-?\d+\.\d+$', input_string):
            return StringParser()
        digits = len(input_string) - 1
        if digits > self.digits:
            self.digits = digits
        return self
    def __str__(self):
        if self.digits <= 6:
            return "REAL"
        return "DOUBLE PRECISION"

class IntParser(object):
    def __init__(self, precision_levels):
        self.precision_levels = precision_levels
        self.max_seen = - float('inf')
        self.min_seen = float('inf')
    def __call__(self, input_string):
        if input_string == '':
            return self
        if not re.match('-?\d+$', input_string):
            return FloatParser()
        input_int = int(input_string)
        if self.max_seen < input_int:
            self.max_seen = input_int
        if self.min_seen > input_int:
            self.min_seen = input_int
        return self
    def __str__(self):
        for bits in sorted(self.precision_levels.keys()):
            if -2**(bits-1) <= self.min_seen and \
               self.max_seen <= 2**(bits-1) - 1:
                break
        else:
            print "Error, big integer!"
            sys.exit(1)
        return self.precision_levels[bits]

def getNetezzaPrecisionLevels():
    return {8: 'BYTEINT',
            16: 'SMALLINT',
            32: 'INTEGER',
            64: 'BIGINT'}

def mkScheme(column_names, parsers):
    return u",\n".join(u"{0} {1}".format(column_name,
                                         str(parser))
                      for column_name, parser in
                      zip(column_names, parsers))

def parseFile(fileName, encoding, separator):
    with io.open(fileName, encoding=encoding) as input_file:
        column_names = input_file.readline()[:-1].split(separator)
        parsers = [IntParser(getNetezzaPrecisionLevels())
                   for i in range(len(column_names))]
        for i, line in enumerate(input_file):
            if i % 10 == 0:
                print i
            parsers = [parser(input_string)
                            for parser, input_string in
                            zip(parsers, line[:-1].split(separator))]
    with io.open("scheme.txt", "w", encoding="utf8") as out_file:
        out_file.write(mkScheme(column_names, parsers))

if __name__ == "__main__":
    parseFile("Data_Nye_SpillereUTF8.csv", "utf8", ",")
