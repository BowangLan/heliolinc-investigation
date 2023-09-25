from utils import createObservationsSpacerocks, createRandomObjects, count_lines, createHelioGuessGrid, extract_heliolinc_results, extract_object_truth_values
from config import *
import destnosim
from helio import run_make_tracklets, run_heliolinc
from time import time



class HelioManager():

    def __init__(self, size: int, t: int, mjd_list: list, mjd_ref: float, dets_file: str, object_table_file: str, guess_file: str, earth_file: str, obs_file: str, colformat_file: str, out_pairdets_file: str, out_pairs_file: str, out_hl_file: str, out_hlsum_file: str, out_hl_extracted_file: str):
        self.size = size
        self.t = t
        self.mjd_list = mjd_list
        self.mjd_ref = mjd_ref
        self.dets_file = dets_file
        self.object_table_file = object_table_file
        self.guess_file = guess_file
        self.earth_file = earth_file
        self.obs_file = obs_file
        self.colformat_file = colformat_file
        self.out_pairdets_file = out_pairdets_file
        self.out_pairs_file = out_pairs_file
        self.out_hl_file = out_hl_file
        self.out_hlsum_file = out_hlsum_file
        self.out_hl_extracted_file = out_hl_extracted_file

    def run(self):
        # create detections
        print("Generating objects and detection catalog...")
        objs = createRandomObjects(size)
        pop = destnosim.ElementPopulation(objs, t)
        dets = createObservationsSpacerocks(pop, mjd_list)
        dets.write(dets_file, overwrite=True)

        # create object table
        objTable = extract_object_truth_values(
            dets.to_pandas(), mjdRef=mjd_ref, mjd_list_len=len(mjd_list))
        objTable.to_feather(object_table_file)

        # run make_tracklets
        print("Running make_tracklets...")
        run_make_tracklets(dets_file, earth_file, obs_file,
                        colformat_file, out_pairdets=out_pairdets_file, out_pairs=out_pairs_file)

        # pairdets_count = count_lines(out_pairdets_file)
        # print(f"Pairdets count: {pairdets_count}")
        # pairs_count = count_lines(out_pairs_file)
        # print(f"Pairs count: {pairs_count}")
        # pairs_coverage = pairs_count / (size * (len(mjd_list)) / 2) * 100
        # print(f"Pairs coverage: {pairs_coverage:.2f}%")

        # create helio guess grid
        createHelioGuessGrid(guess_file)

        print("Running heliolinc...")
        run_heliolinc(out_pairdets_file, out_pairs_file,
                    mjd_list[2], earth_file, guess_file, out=out_hl_file, outsum=out_hlsum_file)

        # hl_count = count_lines(out_hl_file)
        # print(f"Heliolinc count: {hl_count}")
        # hlsum_count = count_lines(out_hlsum_file)
        # print(f"Heliolinc summary count: {hlsum_count}")

        # extract heliolinc results
        helio_res_extracted = extract_heliolinc_results(
            out_hl_file, out_hlsum_file)
        helio_res_extracted.to_feather(out_hl_extracted_file)





def main():
    start = time()
    print("Generating objects and detection catalog...")
    objs = createRandomObjects(size)
    pop = destnosim.ElementPopulation(objs, t)
    dets = createObservationsSpacerocks(pop, mjd_list)
    dets.write(dets_file, overwrite=True)

    objTable = extract_object_truth_values(
        dets.to_pandas(), mjdRef=mjd_ref, mjd_list_len=len(mjd_list))
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
