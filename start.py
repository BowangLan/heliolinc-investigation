from utils import createObservationsSpacerocks, createRandomObjects, createHelioGuessGrid, extract_heliolinc_results, extract_object_truth_values, timeit
from manager import HelioManager
from config import *
import concurrent.futures

# def main():
#     start = time()
#     print("Generating objects and detection catalog...")
#     objs = createRandomObjects(size)
#     pop = destnosim.ElementPopulation(objs, t)
#     dets = createObservationsSpacerocks(pop, mjd_list)
#     dets.write(dets_file, overwrite=True)

#     objTable = extract_object_truth_values(
#         dets.to_pandas(), mjdRef=mjd_ref, mjd_list_len=len(mjd_list))
#     objTable.to_feather(object_table_file)

#     print("Running make_tracklets...")
#     run_make_tracklets(dets_file, earth_file, obs_file,
#                        colformat_file, out_pairdets=out_pairdets_file, out_pairs=out_pairs_file)

#     pairdets_count = count_lines(out_pairdets_file)
#     print(f"Pairdets count: {pairdets_count}")
#     pairs_count = count_lines(out_pairs_file)
#     print(f"Pairs count: {pairs_count}")
#     pairs_coverage = pairs_count / (size * (len(mjd_list)) / 2) * 100
#     print(f"Pairs coverage: {pairs_coverage:.2f}%")

#     createHelioGuessGrid(guess_file)

#     print("Running heliolinc...")
#     run_heliolinc(out_pairdets_file, out_pairs_file,
#                   mjd_list[2], earth_file, guess_file, out=out_hl_file, outsum=out_hlsum_file)

#     hl_count = count_lines(out_hl_file)
#     print(f"Heliolinc count: {hl_count}")
#     hlsum_count = count_lines(out_hlsum_file)
#     print(f"Heliolinc summary count: {hlsum_count}")

#     helio_res_extracted = extract_heliolinc_results(
#         out_hl_file, out_hlsum_file)
#     helio_res_extracted.to_feather(out_hl_extracted_file)

#     duration = time() - start
#     print(f"Total duration: {duration:.4f}s")


print("Library loaded")


def generate_helio_output_config_list(output_path: Path, chunck_count: int = 10):
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


@timeit
def main():
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
    chunck_size = 12
    print("Generating helio guess grid...")
    createHelioGuessGrid(sharedConfig.guess_file)
    print("Generating output config list...")
    outputConfigList = generate_helio_output_config_list(
        Path("./temp/f1"), chunck_count=chunck_size)

    # with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
    #     executor.map(chunck_task, [sharedConfig] *
    #                  chunck_size, outputConfigList, range(1, chunck_size + 1))

    chunck_task(sharedConfig, outputConfigList[0], 1)
    for i, outputConfig in enumerate(outputConfigList):
        chunck_task(sharedConfig, outputConfig, i + 1)

    print("Fnished all tasks")


if __name__ == "__main__":
    main()
