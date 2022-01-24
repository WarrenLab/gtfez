from os.path import dirname, join

import gtfez
import pytest


@pytest.fixture
def sample_gtf_infile():
    return open(join(dirname(__file__), "data", "test_ncbi.gtf"))


@pytest.fixture
def sample_gtf_outfile():
    return open(join(dirname(__file__), "data", "test_ncbi_out.gtf"))


def test_write_full_file(sample_gtf_infile, sample_gtf_outfile, tmp_path):
    with open(tmp_path / "out.gtf", "w") as out_gtf:
        gtfez.cleanup_ncbi.cleanup_ncbi_gtf(
            gtfez.parse(sample_gtf_infile), outfile=out_gtf
        )

    with open(tmp_path / "out.gtf", "r") as out_gtf:
        for line1, line2 in zip(sample_gtf_outfile, out_gtf):
            assert line1 == line2
