"""This file contains the parsers, together with a hierarchy in which
to use them. We e.g. start with an IntParser, should that fail, we try
a FloatParser, and so on. The StringParser will always work.

Note that there is quite a bit of business logic inside the parses,
which is a bit ugly."""
import sys
import re

class StringParser(object):
    """Parse a string, check for length and asci-ness."""
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

class TimeParser(object):
    """Parse a time object."""
    format_string = '\d{2}:\d{2}:d{2}'
    def __call__(self, input_string):
        if not re.search(TimeParser.format_string, input_string):
            return getNextParser(self)
        return self
    def __str__(self):
        return 'TIME'

class DateParser(object):
    """Parse a date object."""
    format_string = '\d{4}\-\d{2}\-\d{2}'
    def __call__(self, input_string):
        if not re.search(DateParser.format_string, input_string):
            return getNextParser(self)
        return self
    def __str__(self):
        return 'DATE'

class DateTimeParser(object):
    """Parse a date-and-time object."""
    format_string = '\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:d{2}'
    def __call__(self, input_string):
        if not re.search(DateTimeParser.format_string, input_string):
            return getNextParser(self)
        return self
    def __str__(self):
        return 'TIMESTAMP'

class FloatParser(object):
    """Parse a float. Keep track of precision."""
    def __init__(self):
        self.valid = True
        self.digits = 0
    def __call__(self, input_string):
        if not input_string:
            return self
        if not re.match('-?\d+\.\d+$', input_string):
            return getNextParser(self)
        digits = len(input_string) - 1
        if digits > self.digits:
            self.digits = digits
        return self
    def __str__(self):
        if self.digits <= 6:
            return "REAL"
        return "DOUBLE PRECISION"

class IntParser(object):
    """Parse an int, keep track of size. On call of __str__ decide
    what precision we will ultimately need. For this, the parser needs
    to be aware of Netezza's precision levels."""
    def __init__(self, precision_levels):
        self.precision_levels = precision_levels
        self.max_seen = - float('inf')
        self.min_seen = float('inf')
    def __call__(self, input_string):
        if input_string == '':
            return self
        try:
            input_int = int(input_string)
            if self.max_seen < input_int:
                self.max_seen = input_int
            if self.min_seen > input_int:
                self.min_seen = input_int
        except ValueError:
            return getNextParser(self)
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

def getNextParser(this):
    """This defines the parser hierarchy."""
    return {IntParser: FloatParser,
            FloatParser: DateTimeParser,
            DateTimeParser: DateParser,
            DateParser: TimeParser,
            TimeParser: StringParser}[type(this)]()

def getNetezzaPrecisionLevels():
    """Netezza int precision levels are kept here."""
    return {8: 'BYTEINT',
            16: 'SMALLINT',
            32: 'INTEGER',
            64: 'BIGINT'}

def getNetezzaParser():
    """Starting point to retrieve the parser highest up in the
    hierarchy."""
    return IntParser(getNetezzaPrecisionLevels())
