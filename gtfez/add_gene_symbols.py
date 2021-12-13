import argparse
import sys
from typing import Dict, Iterator, TextIO, Union

from . import ParsingError, Record, parse


def table_to_dict(filename: str):
    """Parse a two-column tsv to a dictionary.

    Parse a two-column table in tsv format to a dictionary mapping the
    first column to the second column.

    Args:
        filename: path to tsv file

    Returns:
        dictionary mapping column 1 keys to column 2 values

    Raises:
        ParsingError: if a line does not have at least two columns
    """
    output_dict = {}
    with open(filename) as file:
        for i, line in enumerate(file):
            fields = line.strip().split("\t")
            try:
                output_dict[fields[0]] = fields[1]
            except IndexError:
                raise ParsingError(f"Cannot parse line {i} of table.")
    return output_dict


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "gtf_in", type=lambda x: parse(open(x)), help="input gtf to add gene symbols to"
    )
    parser.add_argument(
        "id_to_symbol_table",
        type=table_to_dict,
        help="tab-separated table mapping IDs to symbols",
    )
    parser.add_argument(
        "-g",
        "--gene-id-key GENE_ID_KEY",
        default="gene_id",
        help="key of a GTF attribute that exists in the input file that you want to "
        "use to look up gene symbols, i.e., corresponding to first column of "
        "id_to_symbol_table",
    )
    parser.add_argument(
        "-s",
        "--gene-symbol-key GENE_SYMBOL_KEY",
        default="gene_name",
        help="GTF attribute key that you want to add to the output file, i.e., "
        "corresponding to the second column of id_to_symbol_table",
    )
    parser.add_argument(
        "-o",
        "--outfile OUTFILE",
        default=sys.stdout,
        type=argparse.FileType("w"),
        help="path to file where output gtf should be written",
    )
    return parser.parse_args()


def add_gene_symbols(
    gtf_in: Iterator[Union[str, Record]],
    outfile: TextIO,
    id_to_symbol_table: Dict[str, str],
    gene_id_key: str = "gene_id",
    gene_symbol_key: str = "gene_name",
):
    for record in gtf_in:
        if isinstance(record, Record):
            if gene_id_key in record.attributes:
                gene_id = record.attributes[gene_id_key]
                if gene_id in id_to_symbol_table:
                    gene_symbol = id_to_symbol_table[gene_id]
                    record.attributes[gene_symbol_key] = gene_symbol

        print(record, file=outfile)


def main():
    """Main method of script"""
    args = parse_args()
    add_gene_symbols(
        args.gtf_in,
        args.outfile,
        args.id_to_symbol_table,
        args.gene_id_key,
        args.gene_symbol_key,
    )


if __name__ == "__main__":
    main()
