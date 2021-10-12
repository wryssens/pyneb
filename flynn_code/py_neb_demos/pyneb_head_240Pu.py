import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import time
from matplotlib.pyplot import cm

from datetime import date
import sys
import pandas as pd
### add pyneb
sys.path.insert(0, '../../py_neb/py_neb')
import solvers
import utilities
import utils
today = date.today()
### Define nucleus data path (assumes our github structure)
nucleus = "240Pu"
data_path = f"../../PES/{nucleus}.h5"
### defines PES object from utils.py
PES = utils.PES(data_path)
mass_PES = utils.PES(data_path)
uniq_coords = PES.get_unique(return_type='array')
grids,EE = PES.get_grids(return_coord_grid=True,shift_GS=False)
mass_grids = PES.get_mass_grids()
mass_keys = mass_grids.keys()
### IMPORTANT: LIST THE INDICIES OF THE MASS TENSOR TO USE.
mass_tensor_indicies = ['20','30','pair']

minima_ind = utilities.SurfaceUtils.find_all_local_minimum(EE)
gs_ind = utilities.SurfaceUtils.find_local_minimum(EE,searchPerc=[0.25,0.25,0.25],returnOnlySmallest=True)
gs_coord = np.array((grids[0][gs_ind],grids[1][gs_ind],grids[2][gs_ind])).T
E_gs_raw = EE[gs_ind]
EE = EE - E_gs_raw
#########


#Define potential function
# note this interpolator only interpolates points or arrays of points, no grids.
V_func = utilities.NDInterpWithBoundary(uniq_coords,EE,boundaryHandler='exponential',minVal=0)


# Create dictionary of functions for each comp of the tensor
mass_grids = {key: utilities.NDInterpWithBoundary(uniq_coords,mass_grids[key],boundaryHandler='exponential',minVal=0) \
              for key in mass_keys}
# function returns matrix of functions
M_func = utilities.mass_funcs_to_array_func(mass_grids,mass_tensor_indicies)
#M_func = None # for LAP 
auxFunc = None # for MEP
if M_func is not None:
    mass_title = 'True'
else:
    mass_title = 'False'
#########
E_gs = V_func(gs_coord)
V_func_shift = V_func#utilities.shift_func(V_func,shift=-1.0*E_gs)
const_names = ['pairing']
const_comps = [0]
plane_names = ['Q20','Q30','E_HFB']
re_dict= {'pairing':uniq_coords[2]}
xx_s,yy_s,zz_s = PES.get_2dsubspace(const_names,const_comps,plane_names)
zz_s = zz_s - E_gs_raw

'''
fig, ax = plt.subplots(1,1,figsize = (12, 10))
im = ax.contourf(xx_s,yy_s,zz_s,cmap='Spectral_r',extend='both',levels=MaxNLocator(nbins = 200).tick_values(0,8))
ax.contour(xx_s,yy_s,zz_s,colors=['black'],levels=[E_gs])      
plt.plot(gs_coord[0],gs_coord[1],'o',ms=12,color='black')
cbar = fig.colorbar(im)
plt.show()
'''
NImgs = 32
k = 1.0
kappa = 2.0
E_const = E_gs
nDims = len(uniq_coords)
force_R0 = False
force_RN = True
springR0 = False
springRN = True
endPointFix = (force_R0,force_RN)
springForceFix = (springR0,springRN)

### Optimization parameters 
## Velocity Verlet parameter set
dt = .2
NIterations = 300

### define initial path
R0 = gs_coord # NEB starting point
RN = (185,17,1) # NEB end point
init_path_constructor = utils.init_NEB_path(R0,RN,NImgs)
init_path = init_path_constructor.linear_path()

### Define parameter dictionaries (mostly for book keeping)
neb_params ={'k':k,'kappa':kappa,'constraintEneg':E_const}
method_dict = {'k':k,'kappa':kappa,'NImages': NImgs,'Iterations':NIterations,'dt':dt,'optimization':'Local FIRE','HarmonicForceEnds': endPointFix, \
                   'SpringForceEnds': springForceFix}

    
#### Compute LAP
# LAP function you want to minimize
target_func_LAP = utilities.TargetFunctions.action
# LAP specialized function that takes the gradient of target function
target_func_grad_LAP = solvers.forward_action_grad

LAP_params = {'potential':V_func_shift,'nPts':NImgs,'nDims':nDims,'mass':M_func,'endpointSpringForce': springForceFix ,\
                 'endpointHarmonicForce':endPointFix,'target_func':target_func_LAP,\
                 'target_func_grad':target_func_grad_LAP,'nebParams':neb_params}

### define the least action object 
### This essentially defines the forces given the target and gradient functions 
lap = solvers.LeastActionPath(**LAP_params)

### Define the optimizer object to use. Note the initial band is passed
### here and the operations defined in LeastActionPath are applied to
### the band.
minObj_LAP = solvers.VerletMinimization(lap,initialPoints=init_path)

### Begining the optimization procedure. Results are all of the velocities
### band positions, and forces for each iteration of the optimization.
t0 = time.time()
tStepArr, alphaArr, stepsSinceReset = minObj_LAP.fire(dt,NIterations,useLocal=True)
allPaths_LAP = minObj_LAP.allPts
#allPaths_LAP, allVelocities_LAP, allForces_LAP = minObj_LAP.velocity_verlet(dt,NIterations)
final_path_LAP = allPaths_LAP[-1]
t1 = time.time()
total_time_LAP = t1 - t0
print('total_time LAP: ',total_time_LAP)
action_array_LAP = np.zeros(NIterations+2)
for i,path in enumerate(allPaths_LAP):
    #path_call = utilities.InterpolatedPath(path)
    #action_array_LAP[i] = path_call.compute_along_path(utilities.TargetFunctions.action,100,tfArgs=[V_func_shift])[1][0]
    action_array_LAP[i] = utilities.TargetFunctions.action(path, V_func_shift,M_func)[0]
min_action_LAP = np.around(action_array_LAP[-1],2)
title = 'Eric_'+nucleus+'_LAP_'+'Mass_'+mass_title

### write run meta data to txt file.
metadata = {'title':title,'Created_by': 'Eric','Created_on':today.strftime("%b-%d-%Y"),'method':'NEB-LAP-Numerical','method_description':method_dict, \
                'masses':None,'E_gs': str(E_gs),'action':action_array_LAP[-1],'run_time':total_time_LAP ,\
                    'initial_start_point': R0,'initial_end_point': RN}
utils.make_metadata(metadata)

# write final path to txt.
np.savetxt(title+'_path.txt',final_path_LAP,comments='',delimiter=',',header="Q20,Q30")



'''
#### Compute MEP
# MEP function you want to minimize
target_func_MEP = utilities.TargetFunctions.mep_default
# MEP specialized function that takes the gradient of target function
target_func_grad_MEP = solvers.potential_central_grad 
MEP_params = {'potential':V_func_shift,'nPts':NImgs,'nDims':nDims,'auxFunc':auxFunc,'endpointSpringForce': springForceFix ,\
                 'endpointHarmonicForce':endPointFix,'target_func':target_func_MEP,\
                 'target_func_grad':target_func_grad_MEP,'nebParams':neb_params}
t0 = time.time()
mep = solvers.MinimumEnergyPath(**MEP_params)
minObj_MEP = solvers.VerletMinimization(mep,initialPoints=init_path)
tStepArr, alphaArr, stepsSinceReset = minObj_MEP.fire(dt,NIterations,useLocal=False)
allPaths_MEP = minObj_MEP.allPts
#allPaths_MEP, allVelocities_MEP, allForces_MEP = minObj_MEP.velocity_verlet(dt,NIterations)
t1 = time.time()
total_time_MEP = t1 - t0
final_path_MEP = allPaths_MEP[-1]
title = 'Eric_'+nucleus+'_MEP_'+'Mass_'+mass_title
print('total_time MEP: ',total_time_MEP)

### Compute the action of each path in allPts_MEP
action_array_MEP = np.zeros(NIterations+2)
action_array_MEP_old = np.zeros(NIterations+2)
for i,path in enumerate(allPaths_MEP):
    action_array_MEP[i] = utilities.TargetFunctions.action(path, V_func_shift,None)[0]   # endPointFix = (force_R0,force_RN) springForceFix
    #path_call = utilities.InterpolatedPath(path)
    #action_array_MEP[i] = path_call.compute_along_path(utilities.TargetFunctions.action,100,tfArgs=[V_func_shift])[1][0]
min_action_MEP =  np.around(action_array_MEP[-1],2)
min_action_MEP_old =  np.around(action_array_MEP_old[-1],2)



metadata = {'title':title,'Created_by': 'Eric','Created_on':today.strftime("%b-%d-%Y"),'method':'NEB-MEP','method_description':method_dict, \
                'masses':mass_title,'E_gs': str(E_gs),'action':action_array_MEP[-1],'run_time':total_time_MEP ,\
                    'initial_start_point': R0,'initial_end_point': RN}
utils.make_metadata(metadata)
## should include plot title, method, date created, creator, action value, wall time
    ## model description {k: 10, kappa: 20, nPts: 22, nIterations: 750, optimization: velocity_verlet, endpointForce: on}
np.savetxt(title+'_path.txt',final_path_MEP,comments='',delimiter=',',header="Q20,Q30")
'''
print('LAP Final OTP: ',final_path_LAP)
#print('MEP Final OTP: ', final_path_MEP)
#print('LAP path energy: ',V_func_shift(final_path_LAP))
#print('MEP path energy: ',V_func_shift(final_path_MEP))



### Plot the results.
fig, ax = plt.subplots(1,1,figsize = (12, 10))

im = ax.contourf(xx_s,yy_s,zz_s,cmap='Spectral_r',extend='both',levels=MaxNLocator(nbins = 200).tick_values(0,15))
ax.contour(xx_s,yy_s,zz_s,colors=['black'],levels=[E_gs])              
ax.plot(init_path[:, 0], init_path[:, 1], '.-', color = 'orange',ms=10,label='Initial Path')
ax.plot(final_path_LAP[:, 0], final_path_LAP[:, 1], '.-',ms=10,label='LAP',color='purple')
#ax.plot(final_path_MEP[:, 0], final_path_MEP[:, 1], '.-',ms=10,label='MEP',color='red')    
ax.set_ylabel('$Q_{30}$',size=20)
ax.set_xlabel('$Q_{20}$',size=20)
ax.set_title('M = '+str(NIterations)+' N = '+str(NImgs)+' k='+str(k)+' kappa='+str(kappa)+'_Mass_'+str(mass_title))
ax.legend()
fig.suptitle(f'Projection on to lambda_2 = {const_comps[0]}',fontsize=24)
cbar = fig.colorbar(im)
plt.savefig('Eric_'+nucleus+'Mass_'+mass_title+'.pdf')
plt.show()  
plt.clf()

plt.plot(range(NIterations+2),action_array_LAP,label='LAP '+str(min_action_LAP))
#plt.plot(range(NIterations+2),action_array_MEP,label='MEP '+str(min_action_MEP))
#plt.plot(range(NIterations+2),action_array_MEP_old,label='MEP Discrete '+str(min_action_MEP_old))
plt.xlabel('Iterations')
plt.ylabel('Action')
plt.legend()
plt.savefig('Eric_'+nucleus+'Mass_'+mass_title+'_action.pdf')
plt.show()