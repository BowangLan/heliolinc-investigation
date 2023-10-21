from utils import create_observations_spacerocks, create_random_objects, create_helio_guess_grid, extract_heliolinc_results, extract_object_truth_values, timeit
from destnosim import ElementPopulation
from helio import run_make_tracklets, run_heliolinc
from config import *
import pandas as pd


class HelioManager():

    sharedConfig: HelioSharedConfig
    outputConfig: HelioOutputConfig

    def __init__(self, sharedConfig: HelioSharedConfig, outputConfig: HelioOutputConfig) -> None:
        self.sharedConfig = sharedConfig
        self.outputConfig = outputConfig

    @timeit
    def generate_guess_grid(self) -> None:
        create_helio_guess_grid(self.sharedConfig.guess_file)

    @timeit
    def generate_dets(self) -> None:
        objs = create_random_objects(self.sharedConfig.size)
        pop = ElementPopulation(objs, self.sharedConfig.t)
        dets = create_observations_spacerocks(
            pop, self.sharedConfig.mjd_list, startOidIndex=self.outputConfig.startOidIndex)
        dets.write(self.outputConfig.dets_file, overwrite=True)

        # create object table
        obj_table = extract_object_truth_values(
            dets.to_pandas(), self.sharedConfig.mjd_ref, len(self.sharedConfig.mjd_list))
        obj_table.to_feather(self.outputConfig.object_table_file)

    @timeit
    def run_helio(self) -> None:
        """Runs make_tracklets and heliolinc using the provided config from the class instance.
        """
        run_make_tracklets(self.outputConfig.dets_file, self.sharedConfig.earth_file, self.sharedConfig.obs_file,
                           self.sharedConfig.colformat_file, out_pairdets=self.outputConfig.out_pairdets_file, out_pairs=self.outputConfig.out_pairs_file)

        run_heliolinc(self.outputConfig.out_pairdets_file, self.outputConfig.out_pairs_file,
                      self.sharedConfig.mjd_ref, self.sharedConfig.earth_file, self.sharedConfig.guess_file,
                      out=self.outputConfig.out_hl_file, outsum=self.outputConfig.out_hlsum_file,
                      stdout_file=self.outputConfig.output_dir / "heliolinc_stdout.txt")

    @timeit
    def extract_helio_results(self) -> None:
        helio_res_extracted = extract_heliolinc_results(
            self.outputConfig.out_hl_file, self.outputConfig.out_hlsum_file)
        helio_res_extracted.to_feather(self.outputConfig.out_hl_extracted_file)
        print(
            f"[Task {self.outputConfig.startOidIndex}] Extracted helio results saved to {self.outputConfig.out_hl_extracted_file}")

    def run(self) -> None:

        # create helio guess grid
        print("Generating helio guess grid...")
        self.generate_guess_grid()

        # generate detections
        print("Generating objects and detection catalog...")
        self.generate_dets()

        # run make_tracklets and heliolinc
        print(
            f"Running make_tracklets and heliolinc on {self.sharedConfig.size} objects...")
        self.run_helio()

        # extract heliolinc results
        print("Extracting heliolinc results...")
        self.extract_helio_results()

    def get_extracted_output(self) -> pd.DataFrame:
        df = pd.read_feather(self.outputConfig.out_hl_extracted_file)
        return df

    def get_object_table(self) -> pd.DataFrame:
        df = pd.read_feather(self.outputConfig.object_table_file)
        return df

    def get_guess_table(self) -> pd.DataFrame:
        df = pd.read_csv(self.sharedConfig.guess_file, delimiter=' ')
        return df
