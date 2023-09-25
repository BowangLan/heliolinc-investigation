from pathlib import Path

HELIO_PATH = Path("./heliolinc2")

size = 10000
t = 25
mjd_list = [t + 60676 for t in [0.5, 0.6, 7.5, 7.6, 13.5, 13.6]]
mjd_ref = mjd_list[2]

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
