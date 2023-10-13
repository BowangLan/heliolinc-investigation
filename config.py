from pydantic import BaseModel
from pathlib import Path
import time

HELIO_PATH = Path("./heliolinc2")


dets_file = "./temp/dets.csv"
object_table_file = "./temp/objTable.feather"
guess_file = "./temp/hypo.csv"
earth_file = HELIO_PATH / "tests/Earth1day2020s_02a.txt"
obs_file = HELIO_PATH / "tests/ObsCodes.txt"
colformat_file = "colformat.txt"
out_pairdets_file = "./temp/pairdets.csv"
out_pairs_file = "./temp/pairs.csv"
out_hl_file = "./temp/hl_out.csv"
out_hlsum_file = "./temp/hl_outsum.csv"
out_hl_extracted_file = "./temp/hl_extracted.feather"

dets_file = "./temp/dets.csv"
object_table_file = "./temp/objTable.feather"
guess_file = "./temp/hypo.csv"
earth_file = HELIO_PATH / "tests/Earth1day2020s_02a.txt"
obs_file = HELIO_PATH / "tests/ObsCodes.txt"
colformat_file = "colformat.txt"
out_pairdets_file = "./temp/pairdets.csv"
out_pairs_file = "./temp/pairs.csv"
out_hl_file = "./temp/hl_out.csv"
out_hlsum_file = "./temp/hl_outsum.csv"
out_hl_extracted_file = "./temp/hl_extracted.feather"


def insert_postfix_to_filepath(filepath: str, p: str):
    *a, b = filepath.split('.')
    return '.'.join(a) + f"-{p}." + b


class HelioSharedConfig(BaseModel):
    size: int
    t: int
    mjd_list: list[float]
    guess_file: Path
    earth_file: Path
    obs_file: Path
    colformat_file: Path

    @property
    def mjd_ref(self):
        if len(self.mjd_list) % 2 == 1:
            mid_index = len(self.mjd_list) // 2 - 1
        else:
            mid_index = len(self.mjd_list) // 2
        return self.mjd_list[mid_index]


class HelioOutputConfig(BaseModel):

    output_dir: Path

    def create_output_dir(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created output dir: {self.output_dir}")

    @property
    def dets_file(self):
        return self.output_dir / "dets.csv"

    @property
    def object_table_file(self):
        return self.output_dir / "objTable.feather"

    @property
    def out_pairdets_file(self):
        return self.output_dir / "pairdets.csv"

    @property
    def out_pairs_file(self):
        return self.output_dir / "pairs.csv"

    @property
    def out_hl_file(self):
        return self.output_dir / "hl_out.csv"

    @property
    def out_hlsum_file(self):
        return self.output_dir / "hl_outsum.csv"

    @property
    def out_hl_extracted_file(self):
        return self.output_dir / "hl_extracted.feather"
