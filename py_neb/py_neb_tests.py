#Bad practice? Idk. Fixes import issues when I modify my path in other files, though
try:
    from py_neb.py_neb import *
except ModuleNotFoundError:
    from py_neb import *

import unittest


"""
Use module unittest (see https://docs.python.org/3/library/unittest.html#module-unittest)
    for unit tests. It's much simpler.
    
    
List of tests to add:
    -Test find_local_minimum, using a 3D polynomial with known minima
    -Test midpoint_grad with polynomial:
        *With a single point, to test reshaping
        *With many points, just to check for sure
    -action:
        *Function mass/potential with wrong size outputs?
    -forward_action_grad:
        *Test with different allowed options for potential and mass
    -LeastActionPath.__init__:
        *Error checking
        *Initializing with different parameter sets
    -LeastActionPath.compute_force:
        *Feed in allowed points, transposed points, and wrong-sized points
        *Use polynomial in some number of dimensions for potential, and compute
            gradient by hand
        
Tests added:
    ==========================================================================
    07/09/2021
    -GridInterpWithBoundary.__init__:
        *Test unallowed boundaryHandler
    -GridInterpWithBoundary._find_indices:
        *Test with one point, inside of the grid region
    ==========================================================================
"""

class action_(unittest.TestCase):
    def test_constant_mass_array_potential(self):
        path = np.arange(10).reshape((5,2))
        potential = np.arange(5)**2
        
        act, eneg, mass = action(path,potential)
        
        correctAction = 40
        correctMass = np.full((5,2,2),np.identity(2))
        
        self.assertEqual(act,correctAction)
        self.assertIsNone(np.testing.assert_array_equal(eneg,potential))
        self.assertIsNone(np.testing.assert_array_equal(mass,correctMass))
        
        return None
    
    def test_constant_mass_function_potential(self):
        path = np.arange(6).reshape((3,2))
        
        def pot(coordsArr):
            return np.ones(3)
        
        act, eneg, mass = action(path,pot)
        
        correctAction = 8
        correctPotential = np.ones(3)
        correctMass = np.full((3,2,2),np.identity(2))
        
        #Also checked this by hand
        self.assertEqual(act,correctAction)
        self.assertIsNone(np.testing.assert_array_equal(eneg,correctPotential))
        self.assertIsNone(np.testing.assert_array_equal(mass,correctMass))
        
        return None
    
    def test_grid_mass_array_potential(self):
        path = np.arange(10).reshape((5,2))
        potential = np.arange(5)**2
        mass = np.full((5,2,2),np.identity(2))
        
        act, eneg, mass = action(path,potential)
        
        correctAction = 40
        correctMass = np.full((5,2,2),np.identity(2))
        
        self.assertEqual(act,correctAction)
        self.assertIsNone(np.testing.assert_array_equal(eneg,potential))
        self.assertIsNone(np.testing.assert_array_equal(mass,correctMass))
        
        return None
    
    def test_grid_mass_function_potential(self):
        path = np.arange(6).reshape((3,2))
        mass = np.full((3,2,2),np.identity(2))
        
        def pot(coordsArr):
            return np.ones(3)
        
        act, eneg, mass = action(path,pot,masses=mass)
        
        correctAction = 8
        correctPotential = np.ones(3)
        correctMass = np.full((3,2,2),np.identity(2))
        
        #Also checked this by hand
        self.assertEqual(act,correctAction)
        self.assertIsNone(np.testing.assert_array_equal(eneg,correctPotential))
        self.assertIsNone(np.testing.assert_array_equal(mass,correctMass))
        
        return None
    
    def test_function_mass_array_potential(self):
        path = np.arange(10).reshape((5,2))
        potential = np.arange(5)**2
        
        def mass_func(coordsArr):
            return np.full((5,2,2),np.identity(2))
        
        act, eneg, mass = action(path,potential,masses=mass_func)
        
        correctAction = 40
        correctMass = np.full((5,2,2),np.identity(2))
        
        self.assertEqual(act,correctAction)
        self.assertIsNone(np.testing.assert_array_equal(eneg,potential))
        self.assertIsNone(np.testing.assert_array_equal(mass,correctMass))
        
        return None
    
    def test_function_mass_function_potential(self):
        path = np.arange(6).reshape((3,2))
        
        def pot(coordsArr):
            return np.ones(3)
        
        def mass_func(coordsArr):
            return np.full((3,2,2),np.identity(2))
        
        act, eneg, mass = action(path,pot,masses=mass_func)
        
        correctAction = 8
        correctPotential = np.ones(3)
        correctMass = np.full((3,2,2),np.identity(2))
        
        #Also checked this by hand
        self.assertEqual(act,correctAction)
        self.assertIsNone(np.testing.assert_array_equal(eneg,correctPotential))
        self.assertIsNone(np.testing.assert_array_equal(mass,correctMass))
        
        return None
    
    def test_wrong_potential_shape(self):
        path = np.arange(10).reshape((5,2))
        potential = np.arange(30)**2
        
        with self.assertRaises(ValueError):
            action(path,potential)
        
        return None
    
    def test_wrong_mass_shape(self):
        path = np.arange(10).reshape((5,2))
        potential = np.arange(5)**2
        massGrid = np.ones(12)
        
        with self.assertRaises(ValueError):
            action(path,potential,masses=massGrid)
        
        return None
    
class forward_action_grad_(unittest.TestCase):
    def test_correct_inputs(self):
        path = np.array([[0,0],[1,1],[2,2]],dtype=float)
        
        def potential(path):
            return path[:,0]**2 + path[:,1]**2
        
        def mass(path):
            return np.full((3,2,2),np.identity(2),dtype=float)
        
        potentialOnPath = potential(path)
        massOnPath = mass(path)
        
        gradOfAction, gradOfPes = \
            forward_action_grad(path,potential,potentialOnPath,mass,massOnPath,\
                                action)
              
        #Computed by hand/Mathematica
        correctGradOfPes = np.array([[0,0],[2,2],[4,4]],dtype=float)
        correctGradOfAction = np.stack(2*(np.array([-np.sqrt(2),-1.77636*10**(-7),\
                                                    3*np.sqrt(2)]),)).T
        
        #Heuristic absolute tolerance of 10**(-8) makes it pass the test. Makes
        #sense that gradient isn't more precise, as finite-difference step is
        #eps = 10**(-8)
        self.assertIsNone(np.testing.assert_allclose(gradOfPes,correctGradOfPes,\
                                                     atol=10**(-8)))
        self.assertIsNone(np.testing.assert_allclose(gradOfAction,correctGradOfAction,\
                                                     atol=10**(-8)))
        
        return None

class GridInterpWithBoundary_init_(unittest.TestCase):
    def test_unallowed_boundary_handler(self):
        dummyHandler = "linear"
        with self.assertRaises(ValueError):
            g = GridInterpWithBoundary(None,None,boundaryHandler=dummyHandler)
            
            
        return None
    
class GridInterpWithBoundary_find_indices_(unittest.TestCase):
    def test_in_bounds(self):
        x = np.arange(-5,5.5,0.5)
        y = x.copy()
        
        xx, yy = np.meshgrid(x,y)
        zz = xx**2 + yy**2
        
        #GridInterpWithBoundary is weird. In the current implementation, *calling*
        #g(xi) transposes the points beforce calling g._find_indices. There, it
        #is expected that xi has shape (ndims,-), while calling g(xi) expects
        #xi to have shape (-,ndims)
        point = np.array([0.2,0.4]).reshape((2,1))
        
        g = GridInterpWithBoundary((x,y),zz,minVal=None)
        
        indices, normDistances = g._find_indices(point)
        
        correctIndices = 2*(np.array([10],dtype=int),)
        correctDistances = [np.array([0.4]),np.array([0.8])]
        
        self.assertEqual(indices,correctIndices)
        self.assertEqual(normDistances,correctDistances)
        
        return None

class GridInterpWithBoundaries_evaluate_linear_(unittest.TestCase):
    def test_in_bounds(self):
        x = np.arange(-5,5.5,0.5)
        y = x.copy()
        
        xx, yy = np.meshgrid(x,y)
        zz = xx**2 + yy**2
        
        point = np.array([0.2,0.4]).reshape((2,1))
        
        g = GridInterpWithBoundary((x,y),zz,minVal=None)
        indices, normDist = g._find_indices(point)
        
        values = g._evaluate_linear(indices, normDist)
        
        #Verified via Mathematica
        correctVal = np.array([0.3])
        
        #correctVal is off from expected value by ~floating point precision
        self.assertIsNone(np.testing.assert_allclose(values,correctVal))
        return None
    
class GridInterpWithBoundaries_call_(unittest.TestCase):
    def test_in_bounds(self):
        x = np.arange(-5,5.5,0.5)
        y = x.copy()
        
        xx, yy = np.meshgrid(x,y)
        zz = xx**2 + yy**2
        
        #Reminder that when calling GridInterpWithBoundary, the points should
        #have their *first* dimension equal to the number of coordinates
        point = np.array([0.2,0.4])
        
        g = GridInterpWithBoundary((x,y),zz,minVal=None)
        values = g(point)
        
        #Since we're in the interpolation region, should be the same output
        #as evaluating g._evaluate_linear()
        correctValues = np.array([0.3])
        
        self.assertIsNone(np.testing.assert_allclose(values,correctValues))
        return None
    
    def test_out_of_bounds(self):
        x = np.arange(-5,5.5,0.5)
        y = x.copy()
        
        xx, yy = np.meshgrid(x,y)
        zz = xx**2 + yy**2
        
        #Reminder that when calling GridInterpWithBoundary, the points should
        #have their *first* dimension equal to the number of coordinates
        point = np.array([5.2,0.4])
        
        g = GridInterpWithBoundary((x,y),zz,minVal=None)
        values = g(point)
        
        #Computed in Mathematica
        correctVal = np.array([39.41149756])
        
        self.assertIsNone(np.testing.assert_allclose(values,correctVal))
        return None
    
    def test_in_and_out_of_bounds(self):
        x = np.arange(-5,5.5,0.5)
        y = x.copy()
        
        xx, yy = np.meshgrid(x,y)
        zz = xx**2 + yy**2
        
        #Reminder that when calling GridInterpWithBoundary, the points should
        #have their *first* dimension equal to the number of coordinates
        points = np.array([[5.2,0.4],[0.,0.1],[-1,3]])
        
        g = GridInterpWithBoundary((x,y),zz,minVal=None)
        values = g(points)
        
        correctVals = np.array([39.41149756,0.05,10])
        self.assertIsNone(np.testing.assert_allclose(values,correctVals))
        return None

class LeastActionPath_compute_tangents_(unittest.TestCase):
    def test_first_branch(self):
        def pot(coordsArr):
            return np.ones(3)
        
        nPts = 4
        nDims = 2
        
        lap = LeastActionPath(pot,nPts,nDims)
        
        points = np.stack(2*(np.arange(4),)).T
        enegs = np.arange(4)
        
        tangents = lap._compute_tangents(points,enegs)
        
        correctTangents = np.zeros((nPts,nDims))
        correctTangents[1:3] = np.sqrt(2)/2
        
        #Use assert_allclose rather than assert_array_equal because of some quirk
        #in the calculation, which gives a difference of almost machine precision
        #(~10^(-16)) from the analytic correct answer, \sqrt{2}/2
        self.assertIsNone(np.testing.assert_allclose(tangents,correctTangents))
        
        return None
    
    def test_second_branch(self):
        def pot(coordsArr):
            return np.ones(3)
        
        nPts = 4
        nDims = 2
        
        lap = LeastActionPath(pot,nPts,nDims)
        
        points = np.stack(2*(np.arange(4),)).T
        enegs = np.arange(3,-1,-1)
        
        tangents = lap._compute_tangents(points,enegs)
        
        correctTangents = np.zeros((nPts,nDims))
        correctTangents[1:3] = np.sqrt(2)/2
        
        #Use assert_allclose rather than assert_array_equal because of some quirk
        #in the calculation, which gives a difference of almost machine precision
        #(~10^(-16)) from the analytic correct answer, \sqrt{2}/2
        self.assertIsNone(np.testing.assert_allclose(tangents,correctTangents))
        
        return None
    
    def test_third_branch(self):
        def pot(coordsArr):
            return np.ones(3)
        
        nPts = 3
        nDims = 2
        
        lap = LeastActionPath(pot,nPts,nDims)
        
        points = np.stack(2*(np.arange(3),)).T
        enegs = np.array([-1,-5,1])
        
        tangents = lap._compute_tangents(points,enegs)
        
        correctTangents = np.zeros((nPts,nDims))
        correctTangents[1] = np.sqrt(2)/2
        
        #Use assert_allclose rather than assert_array_equal because of some quirk
        #in the calculation, which gives a difference of almost machine precision
        #(~10^(-16)) from the analytic correct answer, \sqrt{2}/2
        self.assertIsNone(np.testing.assert_allclose(tangents,correctTangents))
        
        return None
    
    def test_last_branch(self):
        def pot(coordsArr):
            return np.ones(3)
        
        nPts = 3
        nDims = 2
        
        lap = LeastActionPath(pot,nPts,nDims)
        
        points = np.stack(2*(np.arange(3),)).T
        #Maybe not obvious that this takes the last branch. Checked it by
        #putting a print statement under the last branch.
        enegs = np.array([-1,-5,-1])
        
        tangents = lap._compute_tangents(points,enegs)
        
        correctTangents = np.zeros((nPts,nDims))
        correctTangents[1] = np.sqrt(2)/2
        
        #Use assert_allclose rather than assert_array_equal because of some quirk
        #in the calculation, which gives a difference of almost machine precision
        #(~10^(-16)) from the analytic correct answer, \sqrt{2}/2
        self.assertIsNone(np.testing.assert_allclose(tangents,correctTangents))
        
        return None

class LeastActionPath_spring_force_(unittest.TestCase):
    def test_no_endpoint_force(self):
        def pot(coordsArr):
            return np.ones(3)
        
        endpointSpringForce = False
        nPts = 3
        nDims = 2
        
        points = np.stack(2*(np.array([0,1,3]),)).T
        
        lap = LeastActionPath(pot,nPts,nDims,nebParams={"k":1},endpointSpringForce=endpointSpringForce)
        tangents = np.zeros((nPts,nDims))
        tangents[1] = np.sqrt(2)/2
        
        springForce = lap._spring_force(points,tangents)
        
        correctSpringForce = np.zeros((nPts,nDims))
        correctSpringForce[1] = 1
        
        self.assertIsNone(np.testing.assert_allclose(springForce,correctSpringForce))
        
        return None
    
    def test_all_endpoint_force(self):
        def pot(coordsArr):
            return np.ones(3)
        
        endpointSpringForce = True
        nPts = 3
        nDims = 2
        
        points = np.stack(2*(np.array([0,1,3]),)).T
        
        lap = LeastActionPath(pot,nPts,nDims,nebParams={"k":1},endpointSpringForce=endpointSpringForce)
        tangents = np.zeros((nPts,nDims))
        tangents[1] = np.sqrt(2)/2
        
        springForce = lap._spring_force(points,tangents)
        
        correctSpringForce = np.array([[1,1],[1,1],[-2,-2]])
        
        self.assertIsNone(np.testing.assert_allclose(springForce,correctSpringForce))
        
        return None
    
    def test_left_endpoint_force(self):
        def pot(coordsArr):
            return np.ones(3)
        
        endpointSpringForce = (True,False)
        nPts = 3
        nDims = 2
        
        points = np.stack(2*(np.array([0,1,3]),)).T
        
        lap = LeastActionPath(pot,nPts,nDims,nebParams={"k":1},endpointSpringForce=endpointSpringForce)
        tangents = np.zeros((nPts,nDims))
        tangents[1] = np.sqrt(2)/2
        
        springForce = lap._spring_force(points,tangents)
        
        correctSpringForce = np.array([[1,1],[1,1],[0,0]])
        
        self.assertIsNone(np.testing.assert_allclose(springForce,correctSpringForce))
        
        return None
    
    def test_right_endpoint_force(self):
        def pot(coordsArr):
            return np.ones(3)
        
        endpointSpringForce = (False,True)
        nPts = 3
        nDims = 2
        
        points = np.stack(2*(np.array([0,1,3]),)).T
        
        lap = LeastActionPath(pot,nPts,nDims,nebParams={"k":1},endpointSpringForce=endpointSpringForce)
        tangents = np.zeros((nPts,nDims))
        tangents[1] = np.sqrt(2)/2
        
        springForce = lap._spring_force(points,tangents)
        
        correctSpringForce = np.array([[0,0],[1,1],[-2,-2]])
        
        self.assertIsNone(np.testing.assert_allclose(springForce,correctSpringForce))
        
        return None
    
class LeastActionPath_compute_force(unittest.TestCase):
    def test_correct_points(self):
        def pot(coordsArr):
            return coordsArr[:,0]**2 + coordsArr[:,1]**2
        
        nPts = 3
        nDims = 2
        
        points = np.stack(2*(np.array([0,1,3],dtype=float),)).T
        
        lap = LeastActionPath(pot,nPts,nDims,nebParams={"k":1,"kappa":2})
        
        netForce = lap.compute_force(points)
        
        #Computed with Mathematica
        correctNetForce = np.array([[1,1],[1,1],[-25.455844,-25.455844]])
        
        self.assertIsNone(np.testing.assert_allclose(netForce,correctNetForce))
        
        
        return None

if __name__ == "__main__":
    unittest.main()
