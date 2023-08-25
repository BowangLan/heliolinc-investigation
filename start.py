from utils import createObservationsSpacerocks, createRandomObjects, count_lines, createHelioGuessGrid, extract_heliolinc_results, extract_object_truth_values
from config import HELIO_PATH
import destnosim
from helio import run_make_tracklets, run_heliolinc
from time import time


size = 800
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


def main():
    start = time()
    print("Generating objects and detection catalog...")
    objs = createRandomObjects(size)
    pop = destnosim.ElementPopulation(objs, t)
    dets = createObservationsSpacerocks(pop, mjd_list)
    dets.write(dets_file, overwrite=True)

    objTable = extract_object_truth_values(dets.to_pandas(), mjdRef=mjd_ref, mjd_list_len=len(mjd_list))
    objTable.to_feather(object_table_file)

    print("Running make_tracklets...")
    run_make_tracklets(dets_file, earth_file, obs_file,
                       colformat_file, out_pairdets=out_pairdets_file, out_pairs=out_pairs_file)

    pairdets_count = count_lines(out_pairdets_file)
    print(f"Pairdets count: {pairdets_count}")
    pairs_count = count_lines(out_pairs_file)
    print(f"Pairs count: {pairs_count}")
    pairs_coverage = pairs_count / (size * (len(mjd_list)) / 2) * 100
    print(f"Pairs coverage: {pairs_coverage:.2f}%")

    createHelioGuessGrid(guess_file)

    print("Running heliolinc...")
    run_heliolinc(out_pairdets_file, out_pairs_file,
                  mjd_list[2], earth_file, guess_file, out=out_hl_file, outsum=out_hlsum_file)

    hl_count = count_lines(out_hl_file)
    print(f"Heliolinc count: {hl_count}")
    hlsum_count = count_lines(out_hlsum_file)
    print(f"Heliolinc summary count: {hlsum_count}")

    helio_res_extracted = extract_heliolinc_results(
        out_hl_file, out_hlsum_file)
    helio_res_extracted.to_feather(out_hl_extracted_file)

    duration = time() - start
    print(f"Total duration: {duration:.4f}s")


if __name__ == "__main__":
    main()
