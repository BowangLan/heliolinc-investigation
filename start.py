from utils import createObservationsSpacerocks, createRandomObjects, create_helio_guess_grid, extract_heliolinc_results, extract_object_truth_values, timeit
from manager import HelioManager
from config import *
import concurrent.futures
import pandas as pd


print("Library loaded")


def generate_helio_output_config_list(output_path: Path, chunck_count: int):
    return [
        HelioOutputConfig(
            output_dir=output_path / f"{i}"
        ) for i in range(1, chunck_count + 1)
    ]


def chunck_task(shared_config: HelioSharedConfig, output_config: HelioOutputConfig, i: int):
    output_config.create_output_dir()
    print(f"Starting chunck task {i}...")
    # with open(output_config.output_dir / "log.txt", "w") as f:
    #     with contextlib.redirect_stdout(f):
    m = HelioManager(shared_config, output_config)
    # time.sleep(7)
    print(f"[Task {i}] Generating detections...")
    m.generate_dets()
    print(f"[Task {i}] Running make_tracklets and helio...")
    m.run_helio()
    print(f"[Task {i}] Extracting helio results...")
    m.extract_helio_results()
    print(f"Finished chunck task {i}")


def combine_output(sharedConfig: HelioSharedConfig, output_config_list: list[HelioOutputConfig], output_dir: Path):
    """Combine the object table and extracted output table from different chuncks into a single object table and extracted output.
    """
    manager = HelioManager(sharedConfig, output_config_list[0])
    obj_table = manager.get_object_table()
    extracted_output = manager.get_extracted_output()
    for con in output_config_list[1:]:
        manager = HelioManager(sharedConfig, con)
        obj_table = pd.concat([obj_table, manager.get_object_table()])
        extracted_output = pd.concat(
            [extracted_output, manager.get_extracted_output()])
    obj_table.reset_index(inplace=True)
    obj_table.to_feather(output_dir / "obj_table.feather")
    print("Combined object table saved to obj_table.feather")
    extracted_output.reset_index(inplace=True)
    extracted_output.to_feather(output_dir / "extracted_output.feather")
    print("Combined extracted output saved to extracted_output.feather")


@timeit
def main():
    chunck_size = 8
    output_dir = Path("./temp/f1")
    t = 25
    mjd_list = [t + 60676 for t in [0.5, 0.6, 7.5, 7.6, 13.5, 13.6]]
    sharedConfig = HelioSharedConfig(
        size=1000,
        t=t,
        mjd_list=mjd_list,
        guess_file=Path("./temp/hypo.csv"),
        earth_file=HELIO_PATH / "tests/Earth1day2020s_02a.txt",
        obs_file=HELIO_PATH / "tests/ObsCodes.txt",
        colformat_file=Path("./colformat.txt")
    )

    print("Generating output config list...")
    outputConfigList = generate_helio_output_config_list(
        output_dir, chunck_size)

    print("Generating helio guess grid...")
    create_helio_guess_grid(sharedConfig.guess_file)

    # running with parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
        executor.map(chunck_task, [sharedConfig] *
                     chunck_size, outputConfigList, range(1, chunck_size + 1))

    # running in series
    # chunck_task(sharedConfig, outputConfigList[0], 1)
    # for i, outputConfig in enumerate(outputConfigList):
    #     chunck_task(sharedConfig, outputConfig, i + 1)

    print("Combining output...")
    combine_output(sharedConfig, outputConfigList, output_dir)

    print("Fnished all tasks")


if __name__ == "__main__":
    main()
