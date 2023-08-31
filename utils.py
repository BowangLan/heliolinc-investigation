import numpy as np
import pandas as pd
import subprocess
import matplotlib.pyplot as plt

import astropy.table as tb
from astropy.time import Time
from astropy import units as u
from astropy import constants as c

from spacerocks.units import Units
from spacerocks.simulation import Simulation
from spacerocks.model import PerturberModel, builtin_models
from spacerocks.cbindings import correct_for_ltt_destnosim
from spacerocks.observer import Observer
from spacerocks.constants import epsilon


def createRandomObjects(size: int):
    # a, e, i, lan, aop, M
    # a : 1.1 -  50
    # e : 0.0 - 0.99
    # i : 0 - 180
    # lan : 0 - 360
    # aop : 0 - 360
    # M : 0 - 360
    """
    - Semi-major axis: provide as 'a' (au)
    - Eccentricity: provide as 'e'
    - Perihelion: provide as 'q' (au)
    - Inclination: provide as 'i' (degrees)
    - Argument of perihelion: provide as 'omega' or 'aop' (degrees)
    - Longitude of ascending node: provide as 'Omega' or 'lan' (degrees)
    - Longitude of perihelion: provide as 'varpi' or 'lop' (degrees)
    - Time of perihelion passage: provide as 'top' or 'T_p' (years)
    - Mean anomaly: provide as 'man' or 'M' (degrees)
    """

    table = tb.Table(
        data=[
            np.random.uniform(1.1, 50, size=size),
            np.random.uniform(0, 0.99, size=size),
            np.random.uniform(0, 180, size=size),
            np.random.uniform(0, 360, size=size),
            np.random.uniform(0, 360, size=size),
            np.random.uniform(0, 360, size=size)
        ],
        names=['a', 'e', 'i', 'Omega', 'omega', 'M']
    )
    return table


def createObservationsSpacerocks(population, mjd, progress=False):
    '''
    Calls the Spacerocks backend to generate observations for the input population


    Arguments:
    - population: Population object for the input orbits
    '''
    # first set up times and do spacerock stuff

    # self.createEarthSpaceRock()
    times = Time(mjd, format='mjd', scale='utc')
    rocks = population.generateSpaceRocks()

    units = Units()
    units.timescale = 'utc'
    units.timeformat = 'jd'
    units.mass = u.M_sun

    spiceids, kernel, masses = builtin_models['ORBITSPP']
    model = PerturberModel(spiceids=spiceids, masses=masses)

    sim = Simulation(model=model, epoch=times.jd[0], units=units)
    sim.add_spacerocks(rocks)
    sim.integrator = 'leapfrog'

    ras = np.array([])
    decs = np.array([])
    orbitid = np.array([])
    mjds = np.array([])
    oidlist = np.arange(len(population))
    xList = np.array([])
    yList = np.array([])
    zList = np.array([])
    dList = np.array([])

    if progress == True:
        from rich.progress import track
        epochs = track(range(len(times.jd)))
    else:
        epochs = range(len(times.jd))

    for i in epochs:
        sim.integrate(times.jd[i], exact_finish_time=1)
        a = np.zeros((sim.N, 3), dtype=np.double)
        b = np.zeros((sim.N, 3), dtype=np.double)
        sim.serialize_particle_data(xyz=a, vxvyvz=b)
        x, y, z = a.T
        vx, vy, vz = b.T

        x = np.ascontiguousarray(x)[sim.N_active:]
        y = np.ascontiguousarray(y)[sim.N_active:]
        z = np.ascontiguousarray(z)[sim.N_active:]
        vx = np.ascontiguousarray(vx)[sim.N_active:]
        vy = np.ascontiguousarray(vy)[sim.N_active:]
        vz = np.ascontiguousarray(vz)[sim.N_active:]

        xList = np.append(xList, x)
        yList = np.append(yList, y)
        zList = np.append(zList, z)
        dList = np.append(dList, np.sqrt(x**2 + y**2 + z**2))

        # observer = Observer(epoch=times.jd[i], obscode='W84', units=units)
        observer = Observer.from_obscode('W84').at(times.jd[i])
        ox = observer.x.au.astype(np.double)
        oy = observer.y.au.astype(np.double)
        oz = observer.z.au.astype(np.double)
        ovx = observer.vx.value.astype(np.double)
        ovy = observer.vy.value.astype(np.double)
        ovz = observer.vz.value.astype(np.double)

        # Compute ltt-corrected topocentroc Ecliptic coordinates
        xt, yt, zt = correct_for_ltt_destnosim(
            x, y, z, vx, vy, vz, ox, oy, oz, ovx, ovy, ovz)
        lon = np.arctan2(yt, xt)
        lat = np.arcsin(zt / np.sqrt(xt**2 + yt**2 + zt**2))
        dec = np.degrees(np.arcsin(np.sin(lat) * np.cos(epsilon) +
                         np.cos(lat) * np.sin(lon) * np.sin(epsilon)))
        ra = np.degrees(np.arctan2((np.cos(lat) * np.cos(epsilon) * np.sin(lon) -
                        np.sin(lat) * np.sin(epsilon)), np.cos(lon) * np.cos(lat)))

        ra[ra > 180] -= 360

        orbitid = np.append(orbitid, oidlist)
        mjds = np.append(mjds, len(oidlist) * [mjd[i]])

        ras = np.append(ras, ra)
        decs = np.append(decs, dec)

    del x, y, z, vx, vy, vz, a, b, sim, xt, yt, zt, ox, oy, oz, observer
    # gather data into something useable
    t = tb.Table()
    t['AstRA(deg)'] = ras
    del ras
    # t['RA'][t['RA'] > 180] -= 360
    t['AstDec(deg)'] = decs
    del decs
    t['ObjID'] = orbitid.astype('int64')
    del orbitid

    t['FieldMJD'] = mjds
    t['Mag'] = 20
    t['Band'] = 'r'
    t['ObsCode'] = 'W84'

    t['d'] = dList
    t['x'] = xList
    t['y'] = yList
    t['z'] = zList

    # ObjID,FieldID,FieldMJD,AstRange(km),AstRangeRate(km/s),AstRA(deg),AstRARate(deg/day),AstDec(deg),AstDecRate(deg/day),Ast-Sun(J2000x)(km),Ast-Sun(J2000y)(km),Ast-Sun(J2000z)(km),Ast-Sun(J2000vx)(km/s),Ast-Sun(J2000vy)(km/s),Ast-Sun(J2000vz)(km/s),Obs-Sun(J2000x)(km),Obs-Sun(J2000y)(km),Obs-Sun(J2000z)(km),Obs-Sun(J2000vx)(km/s),Obs-Sun(J2000vy)(km/s),Obs-Sun(J2000vz)(km/s),Sun-Ast-Obs(deg),V,V(H=0),fiveSigmaDepth,filter,MaginFilterTrue,AstrometricSigma(mas),PhotometricSigma(mag),SNR,AstrometricSigma(deg),MaginFilter,dmagDetect,dmagVignet,AstRATrue(deg),AstDecTrue(deg),detector,OBSCODE,NA

    return t


# Creates a helio guess grid and writes it to out_filename

def createHelioGuessGrid(out_filename, r_range=(1.1, 50), r_dot_range=(-1, 1), r_dot_dot_range=(0, 0), geometric_r=False, ns=(50, 5, 1), n_round=3):
    r = np.linspace(r_range[0], r_range[1], ns[0])
    if geometric_r:
        r = np.logspace(r_range[0], r_range[1], ns[0])
    r_dot = np.linspace(r_dot_range[0], r_dot_range[1], ns[1])
    r_dot_dot = np.linspace(r_dot_dot_range[0], r_dot_dot_range[1], ns[2])
    grid = np.array([[[(r_, r_dot_, r_dot_dot_) for r_dot_dot_ in r_dot_dot]
                    for r_dot_ in r_dot] for r_ in r]).reshape(-1, 3)
    tab = tb.Table()
    tab["#r(AU)"] = grid.T[0].round(n_round)
    GM = c.GM_sun.to(u.au ** 3 / (u.d**2)).value
    v_esc = np.sqrt(2 * GM / (tab["#r(AU)"]))
    tab["rdot(AU/day)"] = (grid.T[1] * v_esc).round(n_round)
    tab["norm"] = 1
    tab["mean_accel"] = grid.T[2].round(n_round)
    tab.write(out_filename, delimiter=' ', overwrite=True)


def extract_heliolinc_results(hl_out_file, hl_outsum_file):
    out = pd.read_csv(hl_out_file)
    outs = pd.read_csv(hl_outsum_file)
    cn_list = outs['#clusternum']
    os_ids = out['idstring']
    os_cn = out['clusternum']
    cn_to_idstring = {}
    for i in range(len(os_ids)):
        cn = os_cn[i]
        cn_to_idstring[cn] = os_ids[i]
    idstring_list = [cn_to_idstring[cn] for cn in cn_list]
    return pd.DataFrame({'idstring': idstring_list, 'clusternum': cn_list,
                    'heliodist': outs['heliodist'], 'heliovel': outs['heliovel'], 'helioacc': outs['helioacc']})


def extract_object_truth_values(dets, mjdRef: float = 60683.5, mjd_list_len: int = 6):
    dets1 = dets[['ObjID', 'd', 'FieldMJD']]
    dets1.sort_values('ObjID', inplace=True)
    dList = dets1['d'].values
    mjdList = (dets1['FieldMJD'] - mjdRef).values
    objCount = int(len(dList) / mjd_list_len)
    helioTruth = []
    for oid in range(objCount):
        x = mjdList[oid * mjd_list_len: (oid + 1) * mjd_list_len] # day
        y = dList[oid * mjd_list_len: (oid + 1) * mjd_list_len] # AU
        fit = np.polyfit(x, y, 2)
        helioTruth.append(fit)

    helioTruth = np.array(helioTruth)
    ha, hv, hd = helioTruth.T
    return pd.DataFrame({'ObjID': np.arange(objCount), 'helioDist': hd, 'helioVel': hv, 'helioAcc': ha})


def count_lines(filename: str):
    t = subprocess.run(["wc", "-l", filename], capture_output=True)
    return int(t.stdout.decode().strip().split(" ")[0])



def plot_hypo_diff_grid(helio_extracted, obj_table, ax=None):
    linked_id_list = set(helio_extracted['idstring'].unique())
    linked_obj_list = obj_table[obj_table['ObjID'].isin(linked_id_list)]
    not_linked_obj_list = obj_table[~obj_table['ObjID'].isin(linked_id_list)]
    if ax:
        ax.scatter(linked_obj_list['helioDist'], linked_obj_list['helioVel'], s=1, c='green')
        ax.scatter(not_linked_obj_list['helioDist'], not_linked_obj_list['helioVel'], s=1, c='red')
    else:
        plt.scatter(linked_obj_list['helioDist'], linked_obj_list['helioVel'], s=1, c='green')
        plt.scatter(not_linked_obj_list['helioDist'], not_linked_obj_list['helioVel'], s=1, c='red')