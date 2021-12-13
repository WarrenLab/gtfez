import filecmp
from os.path import dirname, join
import pytest

import gtfez


@pytest.fixture
def sample_gtf_infile():
    return open(join(dirname(__file__), "data", "test_in.gtf"))


@pytest.fixture
def sample_gtf_outfile():
    return open(join(dirname(__file__), "data", "test_out.gtf"))


@pytest.fixture
def feature_types():
    return [
        "gene",
        "exon",
        "CDS",
        "start_codon",
        "stop_codon",
        "five_prime_utr",
        "three_prime_utr",
        "transcript",
    ]


@pytest.fixture
def correct_protein_coding_gene_ids():
    return set(
        [
            "ENSCAFG00000010239",
            "ENSCAFG00000056546",
            "ENSCAFG00000013472",
            "ENSCAFG00000051139",
            "ENSCAFG00000013422",
            "ENSCAFG00000029799",
            "ENSCAFG00000013353",
            "ENSCAFG00000013346",
            "ENSCAFG00000013336",
            "ENSCAFG00000010261",
        ]
    )


@pytest.fixture
def sample_record():
    return gtfez.Record(
        "38\tensembl\tgene\t17521011\t17523601\t.\t+\t.\t"
        'gene_id "ENSCAFG00000052763"; '
        'gene_version "1"; '
        'gene_source "ensembl"; '
        'gene_biotype "lncRNA";'
    )


def test_parse_attributes():
    attribute_string = (
        'gene_id "ENSCAFG00000055060"; '
        'gene_biotype "miRNA"; '
        'transcript_biotype "miRNA"; '
        'exon_id "ENSCAFE00000485336"; '
        'exon_version "1"; '
        'comment "this is a comment";'
    )
    attributes = gtfez.AttributesDict(attribute_string)
    assert attributes["gene_id"] == "ENSCAFG00000055060"
    assert attributes["gene_biotype"] == "miRNA"
    assert attributes["exon_version"] == "1"
    assert attributes["comment"] == "this is a comment"


def test_parse_bad_attributes():
    attribute_string = (
        'gene_id "ENSCAFG00000055060"; '
        'gene_biotype "miRNA"; '
        'transcript_biotype "miRNA" wlekrj; '
        'exon_id "ENSCAFE00000485336"; '
        'exon_version "1"; '
        'comment "this is a comment";'
    )
    with pytest.raises(gtfez.ParsingError):
        gtfez.AttributesDict(attribute_string)


def test_attributes_to_string():
    attribute_string = (
        'gene_id "ENSCAFG00000055060"; '
        'gene_biotype "miRNA"; '
        'transcript_biotype "miRNA"; '
        'exon_id "ENSCAFE00000485336"; '
        'exon_version "1"; '
        'comment "this is a comment";'
    )
    assert str(gtfez.AttributesDict(attribute_string)) == attribute_string


def test_parse_line(sample_record):
    assert sample_record.seqname == "38"
    assert sample_record.source == "ensembl"
    assert sample_record.start == 17521011
    assert sample_record.end == 17523601
    assert sample_record.score == "."
    assert sample_record.strand == "+"
    assert sample_record.frame == "."
    assert sample_record.attributes["gene_biotype"] == "lncRNA"


def test_print_line(sample_record):
    sample_record.source = "my_butt"
    sample_record.start += 1
    sample_record.end -= 1
    sample_record.attributes["gene_version"] = "no"

    assert str(sample_record) == (
        "38\tmy_butt\tgene\t17521012\t17523600\t.\t+\t.\t"
        'gene_id "ENSCAFG00000052763"; '
        'gene_version "no"; '
        'gene_source "ensembl"; '
        'gene_biotype "lncRNA";'
    )


