import re
from collections import OrderedDict
from collections.abc import MutableMapping
from typing import Iterator, TextIO, Union


class ParsingError(Exception):
    """An error encountered while parsing a gtf record"""

    pass


class Record:
    """A single line of a gtf file."""

    seqname: str
    """see gtf specification"""
    source: str
    """see gtf specification"""
    feature: str
    """see gtf specification"""
    start: int
    """see gtf specification"""
    end: int
    """see gtf specification"""
    score: str
    """see gtf specification"""
    strand: str
    """see gtf specification. Stored a either '+' or '-'."""
    frame: str
    """see gtf specification"""
    attributes: "AttributesDict"
    """a dictionary of the record's attributes field"""

    def __init__(self, line: str):
        """Create a Record from a single line of a GTF"""
        fields = line.strip().split("\t")
        try:
            self.seqname = fields[0]
            self.source = fields[1]
            self.feature = fields[2]
            self.start = int(fields[3])
            self.end = int(fields[4])
            self.score = fields[5]
            self.strand = fields[6]
            self.frame = fields[7]
            self.attributes = AttributesDict(fields[8])
        except (ValueError, IndexError):
            raise ParsingError(f"Cannot parse line: '{line.strip()}'")

    def __str__(self) -> str:
        """Convert the Record back into a line of GTF"""
        return "\t".join(
            map(
                str,
                [
                    self.seqname,
                    self.source,
                    self.feature,
                    self.start,
                    self.end,
                    self.score,
                    self.strand,
                    self.frame,
                    self.attributes,
                ],
            )
        )


class AttributesDict(MutableMapping):
    """An ordered dictionary of GTF attributes

    The ninth column of a GTF file is a list of key-value pairs that the
    specification calls attributes. This class is, more or less, a wrapper
    around collections.OrderedDict with the added ability to parse the
    weirdly formatted attributes column and then print itself back out in
    the correct (still weird) format.

    >>> import gtfez
    >>> attr_dict = gtfez.AttributesDict('key1 "val1"; key2 "val2"; key3 "val3"')
    >>> attr_dict["key1"]
    'val1'
    >>> attr_dict["key2"] = "blah"
    >>> print(attr_dict)
    key1 "val1"; key2 "blah"; key3 "val3";
    """

    _field_seperator_re = re.compile(""";(?=(?:[^'"]|'[^']*'|"[^"]*")*$)""")
    _attribute_re = re.compile(r'^(\w+) "(.*)"$')

    def __init__(self, attributes_field: str):
        """Make an AttributesDict from the attributes field of a gtf record

        Args:
            attributes_field: a string containing the attributes column of
                a single line of a gtf file
        """
        self._attributes = OrderedDict()
        for attribute in self._field_seperator_re.split(attributes_field.rstrip(";")):
            match = self._attribute_re.match(attribute.lstrip(" "))
            if match:
                self._attributes[match.group(1)] = match.group(2)
            else:
                raise ParsingError(f"Cannot parse key/val pair: '{attribute}'")

    def __setitem__(self, key, value):
        self._attributes[key] = value

    def __getitem__(self, key):
        return self._attributes[key]

    def __delitem__(self, key):
        del self._attributes[key]

    def __iter__(self):
        return iter(self._attributes)

    def __len__(self) -> int:
        return len(self._attributes)

    def __str__(self) -> str:
        return " ".join([f'{k} "{v}";' for k, v in self._attributes.items()])

    def move_to_beginning(self, key):
        self._attributes.move_to_end(key, last=False)


def parse(file: TextIO) -> Iterator[Union[str, Record]]:
    """Parse a GTF file

    Given an input stream of a GTF file, parse each line of the file,
    yielding a string if the line is a comment or a Record if the line is a
    regular GTF record.

    Args:
        file: the input GTF

    Yields:
        If the line starts with '#', a string containing the entire line,
        including the '#'. If the line is a GTF record, a Record object.

    Raises:
        ParsingError: if one of the lines of the file is misformatted
    """
    for i, line in enumerate(file):
        if line.startswith("#"):
            yield line.strip()
        else:
            try:
                yield Record(line)
            except ParsingError as e:
                raise ParsingError(f"Line {i+1}: {e}")
