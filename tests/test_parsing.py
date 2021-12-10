import pytest

import gtfez


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

