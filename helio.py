import os
from config import HELIO_PATH


def run_make_tracklets(dets: str, earth: str, obscode: str, colformat: str, out_pairdets: str = "pairdetfile.csv", out_pairs: str = "outpairfile"):
    """
    Runs the make_tracklets executable with the given parameters.
    You can configure the path to the make_tracklets executable in config.py.

    Parameters:
    - dets (str): The name of the input detection catalog file in CSV format.
    - pairdets (str): The name of the output paired detection file in CSV format.
    - pairs (str): The name of the output pair file that records the pairs and longer tracklets.
    - earth (str): The name of the input file that contains the Earth's position and velocity as a function of time.
    - obscode (str): The name of the input file that contains the observatory codes and their geocentric positions.
    - colformat (str): The name of the input file that specifies the column format of the detection catalog file.
    """
    # Construct the command string with the given parameters
    cmd = f"{HELIO_PATH / 'src/make_tracklets'} -dets {dets} -pairdets {out_pairdets} -pairs {out_pairs} \
        -earth {earth} -obscode {obscode} -colformat {colformat}"

    # Execute the command using os.system
    os.system(cmd)


def run_heliolinc():
    pass
