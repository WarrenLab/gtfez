"""Add gene names/symbols to a gtf file.

Often, gtf files come with generic IDs in the "gene_id" field (e.g.,
"ENSCAFG00000052763"), and missing or incomplete human-readable gene names
or symbols included. This script takes as input a gtf file and a tsv table
mapping gene IDs to gene names, and outputs a gtf file with the gene names
added to the attributes dictionaries of the gtf records.
"""
import argparse
import sys
from typing import Dict, Iterator, TextIO, Union

from . import Record, parse


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
            if len(fields) == 2 and fields[1] != "":
                output_dict[fields[0]] = fields[1]
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
        help="tab-separated table mapping gene IDs to names/symbols",
    )
    parser.add_argument(
        "-i",
        "--gene-id-key",
        default="gene_id",
        help="key of a GTF attribute that exists in the input file that you want to "
        "use to look up gene symbols, i.e., corresponding to first column of "
        "id_to_symbol_table",
    )
    parser.add_argument(
        "-n",
        "--gene-name-key",
        default="gene_name",
        help="GTF attribute key that you want to add to the output file, i.e., "
        "corresponding to the second column of id_to_symbol_table",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        default=sys.stdout,
        type=argparse.FileType("w"),
        help="path to file where output gtf should be written",
    )
    return parser.parse_args()


def add_gene_names(
    gtf_in: Iterator[Union[str, Record]],
    id_to_symbol_table: Dict[str, str],
    outfile: TextIO = sys.stdout,
    gene_id_key: str = "gene_id",
    gene_name_key: str = "gene_name",
):
    for record in gtf_in:
        if isinstance(record, Record):
            if gene_id_key in record.attributes:
                gene_id = record.attributes[gene_id_key]
                if gene_id in id_to_symbol_table:
                    gene_symbol = id_to_symbol_table[gene_id]
                    record.attributes[gene_name_key] = gene_symbol

        print(record, file=outfile)


def main():
    """Main method of script"""
    args = parse_args()
    add_gene_names(
        args.gtf_in,
        args.id_to_symbol_table,
        outfile=args.outfile,
        gene_id_key=args.gene_id_key,
        gene_name_key=args.gene_name_key,
    )


if __name__ == "__main__":
    main()
