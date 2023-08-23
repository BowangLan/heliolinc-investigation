import os
import subprocess
from config import HELIO_PATH


def run_make_tracklets(
    dets: str, earth: str,
    obscode: str,
    colformat: str,
    maxvel: float = 2,
    maxtime: float = 5,
    out_pairdets: str = "pairdetfile.csv",
    out_pairs: str = "outpairfile",
    stdout_file: str = "./temp/make_tracklets_output.txt",
):
    """
    Runs the make_tracklets executable with the given parameters.
    You can configure the path to the make_tracklets executable in config.py.

    Parameters:
    - dets (str): The name of the input detection catalog file in CSV format.
    - earth (str): The name of the input file that contains the Earth's position and velocity as a function of time.
    - obscode (str): The name of the input file that contains the observatory codes and their geocentric positions.
    - colformat (str): The name of the input file that specifies the column format of the detection catalog file.
    - maxvel (float): Maximum angular velocity for valid pairs or tracklets
    - maxtime (float): Maximum time between detections in a pair
    - out_pairdets (str): The name of the output paired detection file in CSV format.
    - out_pairs (str): The name of the output pair file that records the pairs and longer tracklets.
    """
    # Construct the command string with the given parameters
    cmd = f"{HELIO_PATH / 'src/make_tracklets'} -dets {dets} -pairdets {out_pairdets} -pairs {out_pairs} \
        -earth {earth} -obscode {obscode} -colformat {colformat} -maxvel {maxvel} -maxtime {maxtime}"

    # Execute the command using os.system
    with open(stdout_file, 'w') as f:
        subprocess.run(cmd, shell=True, stdout=f, stderr=f)


def run_heliolinc(
        dets: str,
        pairs: str,
        mjd: int,
        obspos: str,
        heliodist: str,
        out: str = "./temp/hl_output.csv",
        outsum: str = "./temp/hl_outsum.csv",
        stdout_file: str = "./temp/heliolinc_output.txt",
):
    """
    Runs the heliolinc executable with the given parameters.

    Parameters:
    - dets (str): The name of the input detection catalog file in CSV format.
    - pairs (str): The name of the input pair file that records the pairs and longer tracklets.
    - mjd (int): The MJD of the observations.
    - obspos (str): The name of the input file that contains the observatory codes and their geocentric positions.
    - heliodist (str): The name of the input file that contains the heliocentric distance of the Earth as a function of time.
    - out (str): The name of the output file that contains the heliocentric orbital elements of the objects.
    - outsum (str): The name of the output file that contains the summary of the heliocentric orbital elements of the objects.
    - stdout_file (str): The name of the file to write the stdout and stderr to.
    """
    cmd = f"{HELIO_PATH / 'src/heliolinc'} -dets {dets} -pairs {pairs} -mjd {mjd} \
            -obspos {obspos} -heliodist {heliodist} -out {out} -outsum {outsum}"

    with open(stdout_file, 'w') as f:
        subprocess.run(cmd, shell=True, stdout=f, stderr=f)
