"""
Clean up an NCBI-style gtf file so that it can be parsed by CellRanger
"""
import argparse
import sys
from copy import deepcopy
from typing import IO, Iterator, Union

from . import Record, parse


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "gtf_in", type=lambda x: parse(open(x)), help="input NCBI-style gtf to clean up"
    )
    return parser.parse_args()


def fix_mito_record(record: Record) -> Record:
    pass


def fix_record(
    record: Record,
    allowed_attributes: list[str] = [
        "gene_id",
        "transcript_id",
        "transcript_biotype",
        "gene",
        "gene_name",
        "exon_number",
    ],
) -> Record:
    """Change a nuclear record to be parseable by CellRanger

    Change a record to be parseable by CellRanger by making the
    following changes:
    * Remove attributes whose keys are not in the list of allowed keys
    * Add a "gene_name" attribute that mirrors the "gene" attribute, as
      "gene_name" is where CellRanger looks for the gene symbol

    Arguments:
        record: a Feature object to transform
        allowed_attributes: a list of attribute to allow in the output

    Returns:
        an edited version of the input record
    """
    keys_to_delete = set(record.attributes.keys()) - set(allowed_attributes)
    for key in keys_to_delete:
        del record.attributes[key]
    if "gene" in record.attributes:
        record.attributes["gene_name"] = record.attributes["gene"]

    return record


def deal_with_mito_record(record: Record, outfile: IO = sys.stdout):
    """Create good mitochondrial records

    Mitochondrial annotations in NCBI GTF files are their own special
    brand of messed up, so we throw away everything except "gene" records
    and then recreate transcript and exon records out of the gene record,
    which is OK because of course MT genes are not spliced.
    """
    if record.feature == "gene":
        gene_record = deepcopy(record)
        # add "MT-" to the beginning of mitochondrial gene names
        gene_record.attributes["gene_name"] = "MT-{}".format(
            gene_record.attributes["gene"]
        )

        # make a new transcript record with a transcript ID that is the
        # same as the gene name, because mito genes only have one transcript
        transcript_record = deepcopy(gene_record)
        transcript_record.feature = "transcript"
        transcript_record.attributes["transcript_id"] = transcript_record.attributes[
            "gene_name"
        ]
        transcript_record.attributes[
            "transcript_biotype"
        ] = transcript_record.attributes["gene_biotype"]
        del transcript_record.attributes["gene_biotype"]
        del gene_record.attributes["transcript_id"]

        # make a new exon record that is identical to the transcript record
        # except for being labeled as an exon
        exon_record = deepcopy(transcript_record)
        exon_record.feature = "exon"

        # print it all out
        print(gene_record, file=outfile)
        print(transcript_record, file=outfile)
        print(exon_record, file=outfile)


def cleanup_ncbi_gtf(gtf_in: Iterator[Union[str, Record]], outfile: IO = sys.stdout):
    for record in gtf_in:
        if isinstance(record, str):
            print(record, file=outfile)

        elif record.source == "Gnomon":
            print(fix_record(record), file=outfile)

        elif record.source == "RefSeq":
            deal_with_mito_record(record, outfile=outfile)


def main():
    """Main method of program"""
    args = parse_args()
    cleanup_ncbi_gtf(args.gtf_in)


if __name__ == "__main__":
    main()
