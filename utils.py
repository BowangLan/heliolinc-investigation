import numpy as np

import astropy.table as tb 
from astropy.time import Time  
from astropy import units as u

from spacerocks.units import Units
from spacerocks.simulation import Simulation
from spacerocks.model import PerturberModel, builtin_models
from spacerocks.cbindings import correct_for_ltt_destnosim
from spacerocks.observer import Observer
from spacerocks.constants import epsilon

def createObservationsSpacerocks(population, mjd, progress=True):
	'''
	Calls the Spacerocks backend to generate observations for the input population


	Arguments:
	- population: Population object for the input orbits
	'''
	## first set up times and do spacerock stuff

	#self.createEarthSpaceRock()
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

		observer = Observer(epoch=times.jd[i], obscode='W84', units=units)
		ox = observer.x.au.astype(np.double)
		oy = observer.y.au.astype(np.double)
		oz = observer.z.au.astype(np.double)
		ovx = observer.vx.value.astype(np.double)
		ovy = observer.vy.value.astype(np.double)
		ovz = observer.vz.value.astype(np.double)
		
		# Compute ltt-corrected topocentroc Ecliptic coordinates
		xt, yt, zt = correct_for_ltt_destnosim(x, y, z, vx, vy, vz, ox, oy, oz, ovx, ovy, ovz)
		lon = np.arctan2(yt, xt)
		lat = np.arcsin(zt / np.sqrt(xt**2 + yt**2 + zt**2))
		dec = np.degrees(np.arcsin(np.sin(lat) * np.cos(epsilon) + np.cos(lat) * np.sin(lon) * np.sin(epsilon)))
		ra = np.degrees(np.arctan2((np.cos(lat) * np.cos(epsilon) * np.sin(lon) - np.sin(lat) * np.sin(epsilon)), np.cos(lon) * np.cos(lat)))

		ra[ra>180] -= 360

		orbitid = np.append(orbitid, oidlist)
		mjds = np.append(mjds, len(oidlist) * [i])

		ras = np.append(ras, ra)
		decs = np.append(decs, dec)



	del x, y, z, vx, vy, vz, a, b, sim, xt, yt, zt, ox, oy, oz, observer
	## gather data into something useable
	t = tb.Table()
	t['RA'] = ras
	del ras
	#t['RA'][t['RA'] > 180] -= 360
	t['DEC'] = decs
	del decs
	t['ORBITID'] = orbitid
	t['ORBITID'] = t['ORBITID'].astype('int64')
	del orbitid

	t['MJD'] = mjds

	return t