import io
import re

class IntParser(object):
    def __init__(self, precision_bits, name, priority=2):
        self.lower_bound = -1 * 2**(precision_bits - 1)
        self.upper_bound = 2**(precision_bits - 1) - 1
        self.valid = True
        self.priority = priority
        self.name = name
    def __call__(self, input_string):
        if not self.valid:
            return False
        if not re.match('-?\d*$', input_string):
            self.valid = False
            return False
        if '' == input_string:
            return False
        input_int = int(input_string)
        if not self.lower_bound <= input_int <= self.upper_bound:
            self.valid = False
        return self.valid
    def __str__(self):
        return self.name

class FloatParser(object):
    def __init__(self, priority=1):
        self.valid = True
        self.digits = 0
        self.priority=priority
    def __call__(self, input_string):
        if not self.valid:
            return False
        try:
            input_float = float(input_string)
            digits = len(input_string) - 1
            if digits > self.digits:
                self.digits = digits
        except ValueError:
            self.vaild = False
        return self.valid
    def __str__(self):
        if self.digits <= 6:
            return "REAL"
        return "DOUBLE PRECISION"

class StringParser(object):
    valid = True
    def __init__(self, priority=0):
        self.lengths_seen = set()
        self.is_ascii = True
        self.priority = priority
    def __call__(self, input_string):
        self.lengths_seen.add(len(input_string))
        if self.is_ascii:
            if not all(ord(c) < 128 for c in input_string):
                self.is_ascii = False
        return True
    def __str__(self):
        if len(self.lengths_seen) == 1:
            fmt_string = "CHAR({0})"
        else:
            fmt_string = "VARCHAR({0})"
        if not self.is_ascii:
            fmt_string = "N" + fmt_string
        return fmt_string.format(max(self.lengths_seen))

def getNetezzaParsers():
    return [IntParser(8, 'BYTEINT', 5),
            IntParser(16, 'SMALLINT', 4),
            IntParser(32, 'INTEGER', 3),
            IntParser(64, 'BIGINT', 2),
            FloatParser(),
            StringParser()]

def refreshParsers(parsers, input_string):
    def generateNewParsers():
        for parser in parsers:
            if parser(input_string):
                yield parser
    return list(generateNewParsers())

def getFormatString(parsers):
    def sortFunction(parser):
        if parser.valid:
            return parser.priority
        else:
            return -1
    return str(max(parsers, key=sortFunction))

def mkScheme(column_names, parser_lists):
    return u",\n".join(u"{0} {1}".format(column_name,
                                       getFormatString(parsers))
                      for column_name, parsers in
                      zip(column_names, parser_lists))

def parseFile(fileName, encoding, separator):
    with io.open(fileName, encoding=encoding) as input_file:
        column_names = input_file.readline()[:-1].split(separator)
        parser_lists = [getNetezzaParsers() for i in range(len(column_names))]
        for i, line in enumerate(input_file):
            if i % 10 == 0:
                print i
            parser_lists = [refreshParsers(parsers, input_string)
                            for parsers, input_string in
                            zip(parser_lists, line[:-1].split(separator))]
    with io.open("scheme.txt", "w", encoding="utf8") as out_file:
        out_file.write(mkScheme(column_names, parser_lists))

if __name__ == "__main__":
    parseFile("Data_Nye_SpillereUTF8.csv", "utf8", ",")
