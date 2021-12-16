from os.path import dirname, join

import gtfez
import pytest
from gtfez.add_gene_names import add_gene_names, table_to_dict


@pytest.fixture
def sample_gtf_infile():
    return open(join(dirname(__file__), "data", "test_in.gtf"))


@pytest.fixture
def sample_gtf_outfile():
    return open(join(dirname(__file__), "data", "test_add_gene_names_out.gtf"))


@pytest.fixture
def sample_gene_table():
    return join(dirname(__file__), "data", "ensID_to_symbol.tsv")


def test_table_to_dict(sample_gene_table):
    table = table_to_dict(sample_gene_table)
    assert table["ENSCAFG00000010239"] == "ABC1"
    assert table["ENSCAFG00000056546"] == "NOP6"
    assert "ENSCAFG00000013472" not in table


def test_add_gene_names(
    sample_gtf_infile, sample_gtf_outfile, sample_gene_table, tmp_path
):
    with open(tmp_path / "out.gtf", "w") as out_gtf:
        id_to_symbol_table = table_to_dict(sample_gene_table)
        add_gene_names(
            gtfez.parse(sample_gtf_infile),
            id_to_symbol_table,
            outfile=out_gtf,
        )

    with open(tmp_path / "out.gtf", "r") as out_gtf:
        for line1, line2 in zip(sample_gtf_outfile, out_gtf):
            assert line1 == line2
