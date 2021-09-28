#Appears to be common/best practice to import required packages in every file
#they are used in
import numpy as np
import sys
import matplotlib.pyplot as plt
import itertools

from scipy.interpolate import interpnd, RectBivariateSpline
import warnings

class TargetFunctions:
    #No need to do any compatibility checking with gradients here.
    @staticmethod
    def action(path,potential,masses=None):
        """
        Allowed masses:
            -Constant mass; set masses = None
            -Array of values; set masses to a numpy array of shape (nPoints, nDims, nDims)
            -A function; set masses to a function
        Allowed potential:
            -Array of values; set potential to a numpy array of shape (nPoints,)
            -A function; set masses to a function
            
        Computes action as
            $ S = \sum_{i=1}^{nPoints} \sqrt{2 E(x_i) M_{ab}(x_i) (x_i-x_{i-1})^a(x_i-x_{i-1})^b} $
        """
        nPoints, nDims = path.shape
        
        if masses is None:
            massArr = np.full((nPoints,nDims,nDims),np.identity(nDims))
        elif not isinstance(masses,np.ndarray):
            massArr = masses(path)
        else:
            massArr = masses
            
        massDim = (nPoints, nDims, nDims)
        if massArr.shape != massDim:
            raise ValueError("Dimension of massArr is "+str(massArr.shape)+\
                             "; required shape is "+str(massDim)+". See action function.")
        
        if not isinstance(potential,np.ndarray):
            potArr = potential(path)
        else:
            potArr = potential
        
        potShape = (nPoints,)
        if potArr.shape != potShape:
            raise ValueError("Dimension of potArr is "+str(potArr.shape)+\
                             "; required shape is "+str(potShape)+". See action function.")
        
        for ptIter in range(nPoints):
            if potArr[ptIter] < 0:
                potArr[ptIter] = 0.01
            
        #Actual calculation
        actOut = 0
        for ptIter in range(1,nPoints):
            coordDiff = path[ptIter] - path[ptIter - 1]
            dist = np.dot(coordDiff,np.dot(massArr[ptIter],coordDiff)) #The M_{ab} dx^a dx^b bit
            actOut += np.sqrt(2*potArr[ptIter]*dist)
        
        return actOut, potArr, massArr
    
    @staticmethod
    def action_squared(path,potential,masses=None):
        '''
        Parameters
        ----------
        path : ndarray
            np.ndarray of shape (Nimgs,nDim) containing postions of all images.
        potential : object or ndarray
            Allowed potential:
            -Array of values; set potential to a numpy array of shape (nPoints,)
            -A function; set masses to a function
        masses : object or ndarray, Optional
            Allowed masses:
            -Constant mass; set masses = None
            -Array of values; set masses to a numpy array of shape (nPoints, nDims, nDims)
            -A function; set masses to a function

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        actOut : float
            
        potArr : ndarray
            ndarray of shape (Nimgs,1) containing the PES values for each image in path
        massArr : ndarray
            ndarray of shape (Nimgs,nDim,nDim) containing the mass tensors for each image in path.

        '''
        """    
        Computes action as
            $ S = \sum_{i=1}^{nPoints} \ E(x_i) M_{ab}(x_i) (x_i-x_{i-1})^a(x_i-x_{i-1})^b $
        """
        nPoints, nDims = path.shape
        
        if masses is None:
            massArr = np.full((nPoints,nDims,nDims),np.identity(nDims))
        elif not isinstance(masses,np.ndarray):
            massArr = masses(path)
        else:
            massArr = masses
            
        massDim = (nPoints, nDims, nDims)
        if massArr.shape != massDim:
            raise ValueError("Dimension of massArr is "+str(massArr.shape)+\
                             "; required shape is "+str(massDim)+". See action function.")
        
        if not isinstance(potential,np.ndarray):
            potArr = potential(path)
        else:
            potArr = potential
        
        potShape = (nPoints,)
        if potArr.shape != potShape:
            raise ValueError("Dimension of potArr is "+str(potArr.shape)+\
                             "; required shape is "+str(potShape)+". See action function.")
        
        for ptIter in range(nPoints):
            if potArr[ptIter] < 0:
                potArr[ptIter] = 0.01
            
        #Actual calculation
        actOut = 0
        for ptIter in range(1,nPoints):
            coordDiff = path[ptIter] - path[ptIter - 1]
            dist = np.dot(coordDiff,np.dot(massArr[ptIter],coordDiff)) #The M_{ab} dx^a dx^b bit
            actOut += potArr[ptIter]*dist
        return actOut, potArr, massArr
    
    @staticmethod
    def something_for_mep():
        return None

class GradientApproximations:
    #Should check compatibility here (at least have a list of compatible actions
    #to check in *other* methods)
    #Fill out as appropriate
    @staticmethod
    def method_1():
        
        return None

def find_local_minimum(arr):
    """
    Returns the indices corresponding to the local minimum values. Taken 
    directly from https://stackoverflow.com/a/3986876
    
    Parameters
    ----------
    arr : Numpy array
        A D-dimensional array.

    Returns
    -------
    minIndsOut : Tuple of numpy arrays
        D arrays of length k, for k minima found

    """
    neighborhood = morphology.generate_binary_structure(len(arr.shape),1)
    local_min = (filters.minimum_filter(arr, footprint=neighborhood,\
                                        mode="nearest")==arr)
    
    background = (arr==0)
    eroded_background = morphology.binary_erosion(background,\
                                                  structure=neighborhood,\
                                                  border_value=1)
        
    detected_minima = local_min ^ eroded_background
    allMinInds = np.vstack(local_min.nonzero())
    minIndsOut = tuple([allMinInds[coordIter,:] for \
                        coordIter in range(allMinInds.shape[0])])
    return minIndsOut

def find_approximate_contours(coordMeshTuple,zz,eneg=0,show=False):
    nDims = len(coordMeshTuple)
    
    fig, ax = plt.subplots()
    
    if nDims == 1:
        sys.exit("Err: weird edge case I haven't handled. Why are you looking at D=1?")
    elif nDims == 2:
        allContours = np.zeros(1,dtype=object)
        if show:
            cf = ax.contourf(*coordMeshTuple,zz,cmap="Spectral_r")
            plt.colorbar(cf,ax=ax)
        #Select allsegs[0] b/c I'm only finding one level; ccp.allsegs is a
            #list of lists, whose first index is over the levels requested
        allContours[0] = ax.contour(*coordMeshTuple,zz,levels=[eneg]).allsegs[0]
    else:
        allContours = np.zeros(zz.shape[2:],dtype=object)
        possibleInds = np.indices(zz.shape[2:]).reshape((nDims-2,-1)).T
        for ind in possibleInds:
            meshInds = 2*(slice(None),) + tuple(ind)
            localMesh = (coordMeshTuple[0][meshInds],coordMeshTuple[1][meshInds])
            # print(localMesh)
            allContours[tuple(ind)] = \
                ax.contour(*localMesh,zz[meshInds],levels=[eneg]).allsegs[0]
        if show:
            plt.show(fig)
            
    if not show:
        plt.close(fig)
    
    return allContours

def round_points_to_grid(coordMeshTuple,ptsArr):
    """
    

    Parameters
    ----------
    coordMeshTuple : TYPE
        DESCRIPTION.
    ptsArr : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    nDims = len(coordMeshTuple)
    if nDims < 2: #TODO: probably useless, but could be nice for completion
        raise TypeError("Expected nDims >= 2; recieved "+str(nDims))
        
    uniqueCoords = [np.unique(c) for c in coordMeshTuple]
    
    if ptsArr.shape == (nDims,):
        ptsArr = ptsArr.reshape((1,nDims))
    
    if ptsArr.shape[1] != nDims:
        raise ValueError("ptsArr.shape = "+str(ptsArr.shape)+\
                         "; second dimension should be nDims, "+str(nDims))
        
    nPts = ptsArr.shape[0]
    
    indsOut = np.zeros((nPts,nDims),dtype=int)
    
    #In case some points are on the grid, which np.searchsorted doesn't seem to
    #handle the way I'd like
    for dimIter in range(nDims):
        for (ptIter, pt) in enumerate(ptsArr[:,dimIter]):
            #Nonsense with floating-point precision makes me use
            #np.isclose rather than a == b
            tentativeInd = np.argwhere(np.isclose(uniqueCoords[dimIter],pt))
            if tentativeInd.shape == (0,1): #Nothing found on grid
                indsOut[ptIter,dimIter] = \
                    np.searchsorted(uniqueCoords[dimIter],pt) - 1
            else: #Is on grid
                indsOut[ptIter,dimIter] = tentativeInd
    
    #I subtract 1 in some cases
    indsOut[indsOut<0] = 0
    
    gridValsOut = np.zeros((nPts,nDims))
    for ptIter in range(nPts):
        inds = indsOut[ptIter]
        # Some indexing is done to deal with the default shape of np.meshgrid.
        # For D dimensions, the output is of shape (N2,N1,N3,...,ND), while the
        # way indices are generated expects a shape of (N1,...,ND). So, I swap
        # the first two indices by hand. See https://numpy.org/doc/stable/reference/generated/numpy.meshgrid.html
        inds[[0,1]] = inds[[1,0]]
        inds = tuple(inds)
        gridValsOut[ptIter] = np.array([c[inds] for c in coordMeshTuple])
        
    #Expect columns of returned indices to be in order (N1,N2,N3,...,ND)
    indsOut[:,[0,1]] = indsOut[:,[1,0]]
    
    return indsOut, gridValsOut

def find_endpoints_on_grid(coordMeshTuple,potArr,returnAllPoints=False,eneg=0):
    """
    

    Parameters
    ----------
    returnAllPoints : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    allowedEndpoints : TYPE
        DESCRIPTION.

    """
    if returnAllPoints:
        warnings.warn("find_endpoints_on_grid is finding all "\
                      +"contours; this may include starting point")
    
    nDims = len(coordMeshTuple)
    uniqueCoords = [np.unique(c) for c in coordMeshTuple]
    
    allContours = find_approximate_contours(coordMeshTuple,potArr,eneg=eneg)
    
    allowedEndpoints = np.zeros((0,nDims))
    allowedIndices = np.zeros((0,nDims),dtype=int)
    
    for contOnLevel in allContours:
        gridContOnLevel = []
        gridIndsOnLevel = []
        for cont in contOnLevel:
            locGridInds, locGridVals = \
                round_points_to_grid(coordMeshTuple,cont)
            
            gridIndsOnLevel.append(locGridInds)
            gridContOnLevel.append(locGridVals)
        
        if returnAllPoints:
            for (cIter,c) in enumerate(gridContOnLevel):
                allowedEndpoints = np.concatenate((allowedEndpoints,c),axis=0)
                allowedIndices = np.concatenate((allowedIndices,gridIndsOnLevel[cIter]),axis=0)
        else:
            lenOfContours = np.array([c.shape[0] for c in gridContOnLevel])
            outerIndex = np.argmax(lenOfContours)
            allowedEndpoints = \
                np.concatenate((allowedEndpoints,gridContOnLevel[outerIndex]),axis=0)
            allowedIndices = \
                np.concatenate((allowedIndices,gridIndsOnLevel[outerIndex]),axis=0)
        
    allowedEndpoints = np.unique(allowedEndpoints,axis=0)
    allowedIndices = np.unique(allowedIndices,axis=0)
    
    return allowedEndpoints, allowedIndices

def midpoint_grad(func,points,eps=10**(-8)):
    """
    TODO: allow for arbitrary shaped outputs, for use with inertia tensor
    TODO: maybe only have one gradient approx ever
    
    Midpoint finite difference. Probably best if not used with actual DFT calculations,
        vs a forwards/reverse finite difference
    Assumes func only depends on a single point (vs the action, which depends on
         all of the points)
    """
    if len(points.shape) == 1:
        points = points.reshape((1,-1))
    nPoints, nDims = points.shape
    
    gradOut = np.zeros((nPoints,nDims))
    for dimIter in range(nDims):
        step = np.zeros(nDims)
        step[dimIter] = 1
        
        forwardStep = points + eps/2*step
        backwardStep = points - eps/2*step
        
        forwardEval = func(forwardStep)
        backwardEval = func(backwardStep)
        
        gradOut[:,dimIter] = (forwardEval-backwardEval)/eps
    
    return gradOut

def auxiliary_potential(func_in,shift=10**(-4)):
    warnings.warn("auxiliary_potential is deprecated, use shift_func",DeprecationWarning)
    def func_out(coords):
        return func_in(coords) + shift
    return func_out

def shift_func(func_in,shift=10**(-4)):
    """
    Shifts function by shift

    Parameters
    ----------
    func_in : function
    shift : float
        The amount to shift by. The default is 10**(-4).

    Returns
    -------
    func_out : function
        The shifted function

    """
    def func_out(coords):
        return func_in(coords) + shift
    return func_out

def action(path,potential,masses=None):
    """
    Allowed masses:
        -Constant mass; set masses = None
        -Array of values; set masses to a numpy array of shape (nPoints, nDims, nDims)
        -A function; set masses to a function
    Allowed potential:
        -Array of values; set potential to a numpy array of shape (nPoints,)
        -A function; set masses to a function
        
    Computes action as
        $ S = \sum_{i=1}^{nPoints} \sqrt{2 E(x_i) M_{ab}(x_i) (x_i-x_{i-1})^a(x_i-x_{i-1})^b} $
    """
    warnings.warn("action is deprecated, use TargetFunctions.action",DeprecationWarning)
    
    nPoints, nDims = path.shape
    
    if masses is None:
        massArr = np.full((nPoints,nDims,nDims),np.identity(nDims))
    elif not isinstance(masses,np.ndarray):
        massArr = masses(path)
    else:
        massArr = masses
        
    massDim = (nPoints, nDims, nDims)
    if massArr.shape != massDim:
        raise ValueError("Dimension of massArr is "+str(massArr.shape)+\
                         "; required shape is "+str(massDim)+". See action function.")
    
    if not isinstance(potential,np.ndarray):
        potArr = potential(path)
    else:
        potArr = potential
    
    potShape = (nPoints,)
    if potArr.shape != potShape:
        raise ValueError("Dimension of potArr is "+str(potArr.shape)+\
                         "; required shape is "+str(potShape)+". See action function.")
    
    for ptIter in range(nPoints):
        if potArr[ptIter] < 0:
            potArr[ptIter] = 0.01
    
    # if np.any(potArr[1:-2]<0):
    #     print("Path: ")
    #     print(path)
    #     print("Potential: ")
    #     print(potArr)
    #     raise ValueError("Encountered energy E < 0; stopping.")
        
    #Actual calculation
    actOut = 0
    for ptIter in range(1,nPoints):
        coordDiff = path[ptIter] - path[ptIter - 1]
        dist = np.dot(coordDiff,np.dot(massArr[ptIter],coordDiff)) #The M_{ab} dx^a dx^b bit
        actOut += np.sqrt(2*potArr[ptIter]*dist)
    
    return actOut, potArr, massArr
def action_sqr(path,potential,masses=None):
    '''
    Parameters
    ----------
    path : ndarray
        np.ndarray of shape (Nimgs,nDim) containing postions of all images.
    potential : object or ndarray
        Allowed potential:
        -Array of values; set potential to a numpy array of shape (nPoints,)
        -A function; set masses to a function
    masses : object or ndarray, Optional
        Allowed masses:
        -Constant mass; set masses = None
        -Array of values; set masses to a numpy array of shape (nPoints, nDims, nDims)
        -A function; set masses to a function

    Raises
    ------
    ValueError
        DESCRIPTION.

    Returns
    -------
    actOut : float
        
    potArr : ndarray
        ndarray of shape (Nimgs,1) containing the PES values for each image in path
    massArr : ndarray
        ndarray of shape (Nimgs,nDim,nDim) containing the mass tensors for each image in path.

    '''
    """    
    Computes action as
        $ S = \sum_{i=1}^{nPoints} \ E(x_i) M_{ab}(x_i) (x_i-x_{i-1})^a(x_i-x_{i-1})^b $
    """
    warnings.warn("action_sqr is deprecated, use TargetFunctions.action_squared",DeprecationWarning)
    
    nPoints, nDims = path.shape
    
    if masses is None:
        massArr = np.full((nPoints,nDims,nDims),np.identity(nDims))
    elif not isinstance(masses,np.ndarray):
        massArr = masses(path)
    else:
        massArr = masses
        
    massDim = (nPoints, nDims, nDims)
    if massArr.shape != massDim:
        raise ValueError("Dimension of massArr is "+str(massArr.shape)+\
                         "; required shape is "+str(massDim)+". See action function.")
    
    if not isinstance(potential,np.ndarray):
        potArr = potential(path)
    else:
        potArr = potential
    
    potShape = (nPoints,)
    if potArr.shape != potShape:
        raise ValueError("Dimension of potArr is "+str(potArr.shape)+\
                         "; required shape is "+str(potShape)+". See action function.")
    
    for ptIter in range(nPoints):
        if potArr[ptIter] < 0:
            potArr[ptIter] = 0.01
    
    # if np.any(potArr[1:-2]<0):
    #     print("Path: ")
    #     print(path)
    #     print("Potential: ")
    #     print(potArr)
    #     raise ValueError("Encountered energy E < 0; stopping.")
        
    #Actual calculation
    actOut = 0
    for ptIter in range(1,nPoints):
        coordDiff = path[ptIter] - path[ptIter - 1]
        dist = np.dot(coordDiff,np.dot(massArr[ptIter],coordDiff)) #The M_{ab} dx^a dx^b bit
        actOut += potArr[ptIter]*dist
    return actOut, potArr, massArr

class RectBivariateSplineWrapper(RectBivariateSpline):
    def __init__(self,*args,**kwargs):
        super(RectBivariateSplineWrapper,self).__init__(*args,**kwargs)
        self.function = self.func_wrapper()
        
    def func_wrapper(self):
        def func_out(coords):
            if coords.shape == (2,):
                coords = coords.reshape((1,2))
                
            res = self.__call__(coords[:,0],coords[:,1],grid=False)
            return res
        return func_out
    
class NDInterpWithBoundary:
    """
    Based on scipy.interpolate.RegularGridInterpolator
    """
    def __init__(self, points, values, boundaryHandler="exponential",minVal=0):
        if len(points) < 3:
            warnings.warn("Using ND linear interpolator with "+str(len(points))\
                          +" dimensions. Consider using spline interpolator instead.")
        
        if boundaryHandler not in ["exponential"]:
            raise ValueError("boundaryHandler '%s' is not defined" % boundaryHandler)
        
        if not hasattr(values, 'ndim'):
            #In case "values" is not an array
            values = np.asarray(values)
            
        if len(points) > values.ndim:
            raise ValueError("There are %d point arrays, but values has %d "
                             "dimensions" % (len(points), values.ndim))
            
        if hasattr(values, 'dtype') and hasattr(values, 'astype'):
            if not np.issubdtype(values.dtype, np.inexact):
                values = values.astype(float)
                
        for i, p in enumerate(points):
            if not np.all(np.diff(p) > 0.):
                raise ValueError("The points in dimension %d must be strictly "
                                 "ascending" % i)
            if not np.asarray(p).ndim == 1:
                raise ValueError("The points in dimension %d must be "
                                 "1-dimensional" % i)
            if not values.shape[i] == len(p):
                raise ValueError("There are %d points and %d values in "
                                 "dimension %d" % (len(p), values.shape[i], i))
        
        self.grid = tuple([np.asarray(p) for p in points])
        self.values = values
        self.boundaryHandler = boundaryHandler
        self.minVal = minVal #To be used later, perhaps

    def __call__(self, xi):
        """
        Interpolation at coordinates
        Parameters
        ----------
        xi : ndarray of shape (..., ndim)
            The coordinates to sample the gridded data at
        """
        ndim = len(self.grid)
        
        #Don't really understand what this does
        xi = interpnd._ndim_coords_from_arrays(xi, ndim=ndim)
        if xi.shape[-1] != len(self.grid):
            raise ValueError("The requested sample points xi have dimension "
                              "%d, but this RegularGridInterpolator has "
                              "dimension %d" % (xi.shape[1], ndim))
        
        #Checking if each point is acceptable, and interpolating individual points.
        #Might as well just make the user deal with reshaping, unless I find I need
        #to do so repeatedly
        nPoints = int(xi.size/len(self.grid))
        result = np.zeros(nPoints)
        
        for (ptIter, point) in enumerate(xi):
            isInBounds = np.zeros((2,ndim),dtype=bool)
            isInBounds[0] = (np.array([g[0] for g in self.grid]) <= point)
            isInBounds[1] = (point <= np.array([g[-1] for g in self.grid]))
            
            if np.count_nonzero(~isInBounds) == 0:
                indices, normDistances = self._find_indices(np.expand_dims(point,1))
                result[ptIter] = self._evaluate_linear(indices, normDistances)
            else:
                if self.boundaryHandler == "exponential":
                    result[ptIter] = self._exp_boundary_handler(point,isInBounds)
                
        return result
    
    def _find_indices(self, xi):
        """
        Finds indices of nearest gridpoint (utilizing the regularity of the grid).
        Also computes how far in each coordinate dimension every point is from
        the previous gridpoint (not the nearest), normalized such that the next 
        gridpoint (in a particular dimension) is distance 1 from the nearest gridpoint.
        The distance is normed to make the interpolation simpler.
        
        As an example, returned indices of [[2,3],[1,7],[3,2]] indicates that the
        first point has nearest grid index (2,1,3), and the second has nearest
        grid index (3,7,2).
        
        Note that, if the nearest edge is the outermost edge in a given coordinate,
        the inner edge is return instead. For this reason, this is a custom method
        here, despite similar logic being used elsewhere.

        Parameters
        ----------
        xi : Numpy array
            Array of coordinate(s) to evaluate at. Of dimension (ndims,_)

        Returns
        -------
        indices : Tuple of numpy arrays
            The indices of the nearest gridpoint for all points of xi. Can
            be used as indices of a numpy array
        normDistances : List of numpy arrays
            The distance along each dimension to the nearest gridpoint

        """
        
        indices = []
        # compute distance to lower edge in unity units
        normDistances = []
        # iterate through dimensions
        for x, grid in zip(xi, self.grid):
            #This is why the grid must be sorted - this search is now quick. All
            #this does is find the index in which to place x such that the list
            #self.grid[coordIter] remains sorted.
            i = np.searchsorted(grid, x) - 1
            
            #If x would be the new first element, index it as zero
            i[i < 0] = 0
            #If x would be the last element, make it not so. However, the way
            #the interpolation scheme is set up, we need the nearest gridpoint
            #that is not the outermost gridpoint. See below with grid[i+1]
            i[i > grid.size - 2] = grid.size - 2
            
            indices.append(i)
            normDistances.append((x - grid[i]) / (grid[i + 1] - grid[i]))
            
        return tuple(indices), normDistances

    def _evaluate_linear(self, indices, normDistances):
        """
        A complicated way of implementing repeated linear interpolation. See
        e.g. https://en.wikipedia.org/wiki/Bilinear_interpolation#Weighted_mean
        for the 2D case. Note that the weights simplify because of the normed
        distance that's returned from self._find_indices

        Parameters
        ----------
        indices : TYPE
            DESCRIPTION.
        normDistances : TYPE
            DESCRIPTION.

        Returns
        -------
        values : TYPE
            DESCRIPTION.

        """
        #TODO: remove extra dimension handling
        # slice for broadcasting over trailing dimensions in self.values.
        vslice = (slice(None),) + (None,)*(self.values.ndim - len(indices))
        
        # find relevant values
        # each i and i+1 represents a edge
        edges = itertools.product(*[[i, i + 1] for i in indices])
        values = 0.
        for edge_indices in edges:
            weight = 1.
            for ei, i, yi in zip(edge_indices, indices, normDistances):
                weight *= np.where(ei == i, 1 - yi, yi)
            values += np.asarray(self.values[edge_indices]) * weight[vslice]
        return values
    
    def _exp_boundary_handler(self,point,isInBounds):
        nearestAllowed = np.zeros(point.shape)
        
        for dimIter in range(point.size):
            if np.all(isInBounds[:,dimIter]):
                nearestAllowed[dimIter] = point[dimIter]
            else:
                #To convert from tuple -> numpy array -> int
                failedInd = np.nonzero(isInBounds[:,dimIter]==False)[0].item()
                if failedInd == 1:
                    failedInd = -1
                nearestAllowed[dimIter] = self.grid[dimIter][failedInd]
        
        #Evaluating the nearest allowed point on the boundary of the allowed region
        indices, normDist = self._find_indices(np.expand_dims(nearestAllowed,1))
        valAtNearest = self._evaluate_linear(indices,normDist)
        
        dist = np.linalg.norm(nearestAllowed-point)
        
        #Yes, I mean to take an additional square root here
        result = valAtNearest*np.exp(np.sqrt(dist))
        return result