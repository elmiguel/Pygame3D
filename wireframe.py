import numpy as np

class Wireframe:
    """ An array of vectors in R3 and list of edges connecting them. """
    
    def __init__(self):
        self.nodes = np.zeros((0,4))
        self.edges = []
        self.faces = []

    def addNodes(self, node_array):
        """ Append 1s to a list of 3-tuples and add to self.nodes """
        ones_added = np.hstack((node_array, np.ones((len(node_array),1))))
        self.nodes = np.vstack((self.nodes, ones_added))
    
    def addEdges(self, edge_list):
        # Is it better to use a for loop or generate a long list then add it?
        # Should raise exception if edge value > len(self.nodes)
        self.edges += [edge for edge in edge_list if edge not in self.edges]

    def addFaces(self, face_list):
        for node_list in face_list:
            num_nodes = len(node_list)
            if all((node < len(self.nodes) for node in node_list)):
                #self.faces.append([self.nodes[node] for node in node_list])
                self.faces.append(node_list)
                self.addEdges([(node_list[n-1], node_list[n]) for n in range(num_nodes)])
    
    def output(self):
        if len(self.nodes) > 1:
            self.outputNodes()
        if self.edges:
            self.outputEdges()
        if self.faces:
            self.outputFaces()  
    
    def outputNodes(self):
        print "\n --- Nodes --- "
        for i, (x, y, z, _) in enumerate(self.nodes):
            print "   %d: (%d, %d, %d)" % (i, x, y, z)

    def outputEdges(self):
        print "\n --- Edges --- "
        for i, (node1, node2) in enumerate(self.edges):
            print "   %d: %d -> %d" % (i, node1, node2)
            
    def outputFaces(self):
        print "\n --- Faces --- "
        for i, nodes in enumerate(self.faces):
            print "   %d: (%s)" % (i, ", ".join(['%d' % n for n in nodes]))
    
    def transform(self, transformation_matrix):
        """ Apply a transformation defined by a transformation matrix """
        self.nodes = np.dot(self.nodes, transformation_matrix)
    
    def translate(self, dx=0, dy=0, dz=0):
        """ Translate by vector [dx, dy, dz] """
        self.nodes = np.dot(self.nodes, np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[dx,dy,dz,1]]))
    
    def scale(self, s, cx=0, cy=0, cz=0):
        """ Scale equally along all axes centred on the point (cx,cy,cz). """
        self.nodes = np.dot(self.nodes, np.array([[s, 0, 0, 0],
                                                  [0, s, 0, 0],
                                                  [0, 0, s, 0],
                                                  [cx*(1-s), cy*(1-s), cz*(1-s), 1]]))
    
    def rotateX(self, y, z, radians):
        """ Rotate wireframe about the x-axis by 'radians' radians """
        
        c = np.cos(radians)
        s = np.sin(radians)
        self.nodes = np.dot(self.nodes, np.array([[1, 0, 0, 0],
                                                  [0, c,-s, 0],
                                                  [0, s, c, 0],
                                                  [0, -y*c-z*s+y, y*s-z*c+z, 1]]))
        
    def rotateY(self, x, z, radians):
        """ Rotate wireframe about the y-axis by 'radians' radians """
        
        c = np.cos(radians)
        s = np.sin(radians)
        self.nodes = np.dot(self.nodes, np.array([[ c, 0, s, 0],
                                                  [ 0, 1, 0, 0],
                                                  [-s, 0, c, 0],
                                                  [ z*s-x*c+x, 0, -z*c-x*s+z, 1]]))
        
    def rotateZ(self, x, y, radians):
        """ Rotate wireframe about the z-axis by 'radians' radians """
        
        c = np.cos(radians)
        s = np.sin(radians)
        self.nodes = np.dot(self.nodes, np.array([[c,-s, 0, 0],
                                                  [s, c, 0, 0],
                                                  [0, 0, 1, 0],
                                                  [-x*c-y*s+x, x*s-c*y+y, 0, 1]]))
    
    def findCentre(self):
        """ Find the spatial centre by finding the range of the x, y and z coordinates. """

        min_values = self.nodes[:,:-1].min(axis=0)
        max_values = self.nodes[:,:-1].max(axis=0)
        return 0.5*(min_values + max_values)
    
    def update(self):
        """ Override this function to control wireframe behaviour """
        pass

class WireframeGroup:
    """ A dictionary of wireframes and methods to manipulate them all together """
    
    def __init__(self):
        self.wireframes = {}
    
    def addWireframe(self, name, wireframe):
        self.wireframes[name] = wireframe
    
    def output(self):
        for name, wireframe in self.wireframes.items():
            print name
            wireframe.output()    
    
    def outputNodes(self):
        for name, wireframe in self.wireframes.items():
            print name
            wireframe.outputNodes()
    
    def outputEdges(self):
        for name, wireframe in self.wireframes.items():
            print name
            wireframe.outputEdges()
    
    def translate(self, dx=0, dy=0, dz=0):
        """ Translate by vector [dx, dy, dz] """
        
        for wireframe in self.wireframes.values():
            wireframe.translate(dx, dy, dz)

    def scale(self, scale, (x, y, z)):
        """ Scale wireframes in all directions from a given point, (x,y,z). """
        
        for wireframe in self.wireframes.values():
            wireframe.scale(scale, x, y, z)
    
    def rotateX(self, radians, centre = None):
        """ Rotate wireframes by 'radians' radians
            about a vector parallel to x-axis and passing through the centre of the wireframes """
        
        if not centre:
            (cx, cy, cz) = self.findCentre()
        else:
            (cy, cz) = centre
        
        for wireframe in self.wireframes.values():
            wireframe.rotateX(cy, cz, radians)
        
    def rotateY(self, radians, centre = None):
        """ Rotate wireframes by 'radians' radians
            about a vector parallel to y-axis and passing through the centre of the wireframes """
        
        if not centre:
            (cx, cy, cz) = self.findCentre()
        else:
            (cx, cz) = centre
        
        for wireframe in self.wireframes.values():
            wireframe.rotateY(cx, cz, radians)
        
    def rotateZ(self, radians, centre = None):
        """ Rotate wireframes by 'radians' radians
            about a vector parallel to y-axis and passing through the centre of the wireframes """
        
        if not centre:
            (cx, cy, cz) = self.findCentre()
        else:
            (cx, cy) = centre
        
        for wireframe in self.wireframes.values():
            wireframe.rotateZ(cx, cy, radians)
    
    def findCentre(self):
        """ Find the central point of all the wireframes. """
        
        # There may be a more efficient way to find the minimums for a group of wireframes
        min_values = np.array([wireframe.nodes[:,:-1].min(axis=0) for wireframe in self.wireframes.values()]).min(axis=0)
        max_values = np.array([wireframe.nodes[:,:-1].max(axis=0) for wireframe in self.wireframes.values()]).max(axis=0)
        return 0.5*(min_values + max_values)
    
    def update(self):
        for wireframe in self.wireframes.values():
            wireframe.update()
    
def getCuboid((x,y,z), (w,h,d)):
    """ Return a wireframe cuboid starting at (x,y,z)
        with width, w, height, h, and depth, d. """

    cuboid = Wireframe()
    cuboid.addNodes(np.array([[nx,ny,nz] for nx in (x,x+w) for ny in (y,y+h) for nz in (z,z+d)]))
    cuboid.addFaces([(0,1,3,2), (4,5,7,6)])
    cuboid.addFaces([(0,1,5,4), (2,3,7,6)])
    cuboid.addFaces([(0,2,6,4), (1,3,7,5)])
    
    return cuboid

def getSpheroid((x,y,z), (rx, ry, rz), resolution=10):
    """ Returns a wireframe spheroid centred on (x,y,z)
        with a radius of (rx,ry,rz) in the respective axes. """
    
    spheroid   = Wireframe()
    latitudes  = [n*np.pi/resolution for n in range(1,resolution)]
    longitudes = [n*2*np.pi/resolution for n in range(resolution)]

    # Add nodes except for poles
    spheroid.addNodes([(x + rx*np.sin(n)*np.sin(m), y - ry*np.cos(m), z - rz*np.cos(n)*np.sin(m)) for m in latitudes for n in longitudes])

    # Add square faces to whole spheroid but poles
    num_nodes = resolution*(resolution-1)
    spheroid.addFaces([(m+n, m+(n+1)%resolution, (m+resolution)%resolution**2+(n+1)%resolution, (m+resolution)%num_nodes+n) for n in range(resolution) for m in range(0,num_nodes-resolution,resolution)])

    # Add poles and triangular faces around poles
    spheroid.addNodes([(x, y+ry, z),(x, y-ry, z)])
    spheroid.addFaces([(num_nodes+1, (n+1)%resolution, n) for n in range(resolution)])
    start_node = num_nodes-resolution
    spheroid.addFaces([(num_nodes, start_node+n, start_node+(n+1)%resolution) for n in range(resolution)])

    return spheroid

def getHorizontalGrid((x,y,z), (dx,dz), (nx,nz)):
    """ Returns a nx by nz wireframe grid that starts at (x,y,z) with width dx.nx and depth dz.nz. """
    
    grid = Wireframe()
    grid.addNodes(np.array([[x+n1*dx, y, z+n2*dz] for n1 in range(nx+1) for n2 in range(nz+1)]))
    grid.addEdges([(n1*(nz+1)+n2,n1*(nz+1)+n2+1) for n1 in range(nx+1) for n2 in range(nz)])
    grid.addEdges([(n1*(nz+1)+n2,(n1+1)*(nz+1)+n2) for n1 in range(nx) for n2 in range(nz+1)])
    
    return grid