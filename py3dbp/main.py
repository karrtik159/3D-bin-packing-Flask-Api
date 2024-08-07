import numpy as np
from .constants import RotationType, Axis
from .auxiliary_methods import intersect, set2Decimal,generate_vertices
import numpy as np

# required to plot a representation of Bin and contained items 
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from typing import Type
import copy

DEFAULT_NUMBER_OF_DECIMALS = 0
START_POSITION = [0, 0, 0]



class Item:

    def __init__(self, partno,name,typeof, WHD, weight, level, loadbear=9999, updown=1, color=1):
        ''' '''
        self.partno = partno
        self.name = name
        self.typeof = typeof
        self.width = WHD[0]
        self.height = WHD[1]
        self.depth = WHD[2]
        self.weight = weight
        # Packing Priority level ,choose 1-3
        self.level = level
        # loadbear
        self.loadbear = loadbear
        # Upside down? True or False
        self.updown = updown if typeof == 'cube' else False
        # Draw item color
        self.color = color
        self.rotation_type = 0
        self.position = START_POSITION
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS


    def formatNumbers(self, number_of_decimals):
        ''' '''
        self.width = set2Decimal(self.width, number_of_decimals)
        self.height = set2Decimal(self.height, number_of_decimals)
        self.depth = set2Decimal(self.depth, number_of_decimals)
        self.weight = set2Decimal(self.weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals


    def string(self):
        ''' '''
        return "%s(%sx%sx%s, weight: %s) pos(%s) rt(%s) vol(%s)" % (
            self.partno, self.width, self.height, self.depth, self.weight,
            self.position, self.rotation_type, self.getVolume()
        )


    def getVolume(self):
        ''' '''
        return set2Decimal(self.width * self.height * self.depth, self.number_of_decimals)


    def getMaxArea(self):
        ''' '''
        a = sorted([self.width,self.height,self.depth],reverse=True) if self.updown == True else [self.width,self.height,self.depth]
    
        return set2Decimal(a[0] * a[1] , self.number_of_decimals)


    def getDimension(self):
        ''' rotation type '''
        if self.rotation_type == RotationType.RT_WHD:
            dimension = [self.width, self.height, self.depth]
        elif self.rotation_type == RotationType.RT_HWD:
            dimension = [self.height, self.width, self.depth]
        elif self.rotation_type == RotationType.RT_HDW:
            dimension = [self.height, self.depth, self.width]
        elif self.rotation_type == RotationType.RT_DHW:
            dimension = [self.depth, self.height, self.width]
        elif self.rotation_type == RotationType.RT_DWH:
            dimension = [self.depth, self.width, self.height]
        elif self.rotation_type == RotationType.RT_WDH:
            dimension = [self.width, self.depth, self.height]
        else:
            dimension = []

        return dimension
    
    def _plot(self,color,figure: Type[go.Figure] = None) -> Type[go.Figure]:
        """Adds the plot of a box to a given figure

         Parameters
         ----------
        figure: go.Figure
             A plotly figure where the box should be plotted

         Returns
         -------
         go.Figure
        """
        # Generate the coordinates of the vertices
        vertices = generate_vertices(self.getDimension(), self.position).T
        x, y, z = vertices[0, :], vertices[1, :], vertices[2, :]
        # The arrays i, j, k contain the indices of the triangles to be plotted (two per each face of the box)
        # The triangles have vertices (x[i[index]], y[j[index]], z[k[index]]), index = 0,1,..7.
        i = [1, 2, 5, 6, 1, 4, 3, 6, 1, 7, 0, 6]
        j = [0, 3, 4, 7, 0, 5, 2, 7, 3, 5, 2, 4]
        k = [2, 1, 6, 5, 4, 1, 6, 3, 7, 1, 6, 0]
        edge_pairs = [
            (0, 1),
            (0, 2),
            (0, 4),
            (1, 3),
            (1, 5),
            (2, 3),
            (2, 6),
            (3, 7),
            (4, 5),
            (4, 6),
            (5, 7),
            (6, 7),
        ]
        for (m, n) in edge_pairs:
            vert_x = np.array([x[m], x[n]])
            vert_y = np.array([y[m], y[n]])
            vert_z = np.array([z[m], z[n]])
        if figure is None:
            # Plot the box faces
            figure = go.Figure(
                data=[
                    go.Mesh3d(
                        x=x,
                        y=y,
                        z=z,
                        i=i,
                        j=j,
                        k=k,
                        opacity=1,
                        color=color,
                        flatshading=True,
                    )
                ]
            )
            # Plot the box edges
            figure.add_trace(
                go.Scatter3d(
                    x=vert_x,
                    y=vert_y,
                    z=vert_z,
                    mode="lines",
                    line=dict(color="black", width=0),
                )
            )

        else:
            # Plot the box faces
            figure.add_trace(
                go.Mesh3d(
                    x=x,
                    y=y,
                    z=z,
                    i=i,
                    j=j,
                    k=k,
                    opacity=1,
                    color=color,
                    flatshading=True,
                )
            )
            # Plot the box edges
            figure.add_trace(
                go.Scatter3d(
                    x=vert_x,
                    y=vert_y,
                    z=vert_z,
                    mode="lines",
                    line=dict(color="black", width=0),
                )
            )

        return figure


class Bin:

    def __init__(self, partno, WHD, max_weight,corner=0,put_type=1):
        ''' '''
        self.partno = partno
        self.position = START_POSITION
        self.width = WHD[0]
        self.height = WHD[1]
        self.depth = WHD[2]
        self.max_weight = max_weight
        self.corner = corner
        self.items = []
        self.fit_items = np.array([[0,WHD[0],0,WHD[1],0,0]])
        self.unfitted_items = []
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS
        self.fix_point = False
        self.check_stable = False
        self.support_surface_ratio = 0
        self.put_type = put_type
        # used to put gravity distribution
        self.gravity = []


    def formatNumbers(self, number_of_decimals):
        ''' '''
        self.width = set2Decimal(self.width, number_of_decimals)
        self.height = set2Decimal(self.height, number_of_decimals)
        self.depth = set2Decimal(self.depth, number_of_decimals)
        self.max_weight = set2Decimal(self.max_weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals


    def string(self):
        ''' '''
        return "%s(%sx%sx%s, max_weight:%s) vol(%s)" % (
            self.partno, self.width, self.height, self.depth, self.max_weight,
            self.getVolume()
        )


    def getVolume(self):
        ''' '''
        return set2Decimal(
            self.width * self.height * self.depth, self.number_of_decimals
        )


    def getTotalWeight(self):
        ''' '''
        total_weight = 0

        for item in self.items:
            total_weight += item.weight

        return set2Decimal(total_weight, self.number_of_decimals)


    def putItem(self, item, pivot,axis=None):
        ''' put item in bin '''
        fit = False
        valid_item_position = item.position
        item.position = pivot
        rotate = RotationType.ALL if item.updown == True else RotationType.Notupdown
        for i in range(0, len(rotate)):
            item.rotation_type = i
            dimension = item.getDimension()
            # rotatate
            if (
                self.width < pivot[0] + dimension[0] or
                self.height < pivot[1] + dimension[1] or
                self.depth < pivot[2] + dimension[2]
            ):
                continue

            fit = True

            for current_item_in_bin in self.items:
                if intersect(current_item_in_bin, item):
                    fit = False
                    break

            if fit:
                # cal total weight
                if self.getTotalWeight() + item.weight > self.max_weight:
                    fit = False
                    return fit
                
                # fix point float prob
                if self.fix_point == True :
                        
                    [w,h,d] = dimension
                    [x,y,z] = [float(pivot[0]),float(pivot[1]),float(pivot[2])]

                    for i in range(3):
                        # fix height
                        y = self.checkHeight([x,x+float(w),y,y+float(h),z,z+float(d)])
                        # fix width
                        x = self.checkWidth([x,x+float(w),y,y+float(h),z,z+float(d)])
                        # fix depth
                        z = self.checkDepth([x,x+float(w),y,y+float(h),z,z+float(d)])

                    # check stability on item 
                    # rule : 
                    # 1. Define a support ratio, if the ratio below the support surface does not exceed this ratio, compare the second rule.
                    # 2. If there is no support under any vertices of the bottom of the item, then fit = False.
                    if self.check_stable == True :
                        # Cal the surface area of ​​item.
                        item_area_lower = int(dimension[0] * dimension[1])
                        # Cal the surface area of ​​the underlying support.
                        support_area_upper = 0
                        for i in self.fit_items:
                            # Verify that the lower support surface area is greater than the upper support surface area * support_surface_ratio.
                            if z == i[5]  :
                                area = len(set([ j for j in range(int(x),int(x+int(w)))]) & set([ j for j in range(int(i[0]),int(i[1]))])) * \
                                len(set([ j for j in range(int(y),int(y+int(h)))]) & set([ j for j in range(int(i[2]),int(i[3]))]))
                                support_area_upper += area

                        # If not , get four vertices of the bottom of the item.
                        if support_area_upper / item_area_lower < self.support_surface_ratio :
                            four_vertices = [[x,y],[x+float(w),y],[x,y+float(h)],[x+float(w),y+float(h)]]
                            #  If any vertices is not supported, fit = False.
                            c = [False,False,False,False]
                            for i in self.fit_items:
                                if z == i[5] :
                                    for jdx,j in enumerate(four_vertices) :
                                        if (i[0] <= j[0] <= i[1]) and (i[2] <= j[1] <= i[3]) :
                                            c[jdx] = True
                            if False in c :
                                item.position = valid_item_position
                                fit = False
                                return fit
                        
                    self.fit_items = np.append(self.fit_items,np.array([[x,x+float(w),y,y+float(h),z,z+float(d)]]),axis=0)
                    item.position = [set2Decimal(x),set2Decimal(y),set2Decimal(z)]

                if fit :
                    self.items.append(copy.deepcopy(item))

            else :
                item.position = valid_item_position

            return fit

        else :
            item.position = valid_item_position

        return fit


    def checkDepth(self,unfix_point):
        ''' fix item position z '''
        z_ = [[0,0],[float(self.depth),float(self.depth)]]
        for j in self.fit_items:
            # creat x set
            x_bottom = set([i for i in range(int(j[0]),int(j[1]))])
            x_top = set([i for i in range(int(unfix_point[0]),int(unfix_point[1]))])
            # creat y set
            y_bottom = set([i for i in range(int(j[2]),int(j[3]))])
            y_top = set([i for i in range(int(unfix_point[2]),int(unfix_point[3]))])
            # find intersection on x set and y set.
            if len(x_bottom & x_top) != 0 and len(y_bottom & y_top) != 0 :
                z_.append([float(j[4]),float(j[5])])
        top_depth = unfix_point[5] - unfix_point[4]
        # find diff set on z_.
        z_ = sorted(z_, key = lambda z_ : z_[1])
        for j in range(len(z_)-1):
            if z_[j+1][0] -z_[j][1] >= top_depth:
                return z_[j][1]
        return unfix_point[4]


    def checkWidth(self,unfix_point):
        ''' fix item position x ''' 
        x_ = [[0,0],[float(self.width),float(self.width)]]
        for j in self.fit_items:
            # creat z set
            z_bottom = set([i for i in range(int(j[4]),int(j[5]))])
            z_top = set([i for i in range(int(unfix_point[4]),int(unfix_point[5]))])
            # creat y set
            y_bottom = set([i for i in range(int(j[2]),int(j[3]))])
            y_top = set([i for i in range(int(unfix_point[2]),int(unfix_point[3]))])
            # find intersection on z set and y set.
            if len(z_bottom & z_top) != 0 and len(y_bottom & y_top) != 0 :
                x_.append([float(j[0]),float(j[1])])
        top_width = unfix_point[1] - unfix_point[0]
        # find diff set on x_bottom and x_top.
        x_ = sorted(x_,key = lambda x_ : x_[1])
        for j in range(len(x_)-1):
            if x_[j+1][0] -x_[j][1] >= top_width:
                return x_[j][1]
        return unfix_point[0]
    

    def checkHeight(self,unfix_point):
        '''fix item position y '''
        y_ = [[0,0],[float(self.height),float(self.height)]]
        for j in self.fit_items:
            # creat x set
            x_bottom = set([i for i in range(int(j[0]),int(j[1]))])
            x_top = set([i for i in range(int(unfix_point[0]),int(unfix_point[1]))])
            # creat z set
            z_bottom = set([i for i in range(int(j[4]),int(j[5]))])
            z_top = set([i for i in range(int(unfix_point[4]),int(unfix_point[5]))])
            # find intersection on x set and z set.
            if len(x_bottom & x_top) != 0 and len(z_bottom & z_top) != 0 :
                y_.append([float(j[2]),float(j[3])])
        top_height = unfix_point[3] - unfix_point[2]
        # find diff set on y_bottom and y_top.
        y_ = sorted(y_,key = lambda y_ : y_[1])
        for j in range(len(y_)-1):
            if y_[j+1][0] -y_[j][1] >= top_height:
                return y_[j][1]

        return unfix_point[2]


    def addCorner(self):
        '''add container coner '''
        if self.corner != 0 :
            corner = set2Decimal(self.corner)
            corner_list = []
            for i in range(8):
                a = Item(
                    partno='corner{}'.format(i),
                    name='corner', 
                    typeof='cube',
                    WHD=(corner,corner,corner), 
                    weight=0, 
                    level=0, 
                    loadbear=0, 
                    updown=True, 
                    color='#000000')

                corner_list.append(a)
            return corner_list


    def putCorner(self,info,item):
        '''put coner in bin '''
        fit = False
        x = set2Decimal(self.width - self.corner)
        y = set2Decimal(self.height - self.corner)
        z = set2Decimal(self.depth - self.corner)
        pos = [[0,0,0],[0,0,z],[0,y,z],[0,y,0],[x,y,0],[x,0,0],[x,0,z],[x,y,z]]
        item.position = pos[info]
        self.items.append(item)

        corner = [float(item.position[0]),float(item.position[0])+float(self.corner),float(item.position[1]),float(item.position[1])+float(self.corner),float(item.position[2]),float(item.position[2])+float(self.corner)]

        self.fit_items = np.append(self.fit_items,np.array([corner]),axis=0)
        return


    def clearBin(self):
        ''' clear item which in bin '''
        self.items = []
        self.fit_items = np.array([[0,self.width,0,self.height,0,0]])
        return

    def _plot(self, figure: Type[go.Figure] = None) -> Type[go.Figure]:
        """Adds the plot of a container with its boxes to a given figure

        Parameters
        ----------
        figure: go.Figure, default = None
            A plotly figure where the box should be plotted
        Returns
        -------
            go.Figure
        """
        if figure is None:
            figure = go.Figure()

        # Generate all vertices and edge pairs, the numbering is explained in the function utils.generate_vertices
        vertices = generate_vertices([self.width, self.height, self.depth], self.position).T
        x, y, z = vertices[0, :], vertices[1, :], vertices[2, :]
        edge_pairs = [
            (0, 1),
            (0, 2),
            (0, 4),
            (1, 3),
            (1, 5),
            (2, 3),
            (2, 6),
            (3, 7),
            (4, 5),
            (4, 6),
            (5, 7),
            (6, 7),
        ]

        # Add a line between each pair of edges to the figure
        for (m, n) in edge_pairs:
            vert_x = np.array([x[m], x[n]])
            vert_y = np.array([y[m], y[n]])
            vert_z = np.array([z[m], z[n]])
            figure.add_trace(
                go.Scatter3d(
                    x=vert_x,
                    y=vert_y,
                    z=vert_z,
                    mode="lines",
                    line=dict(color="yellow", width=3),
                )
            )
        color_list = px.colors.qualitative.Dark24

        for idx,item in enumerate(self.items):
            # item_color = color_list[-2]
            item_color = color_list[(int(item.getVolume())  +int(idx)) % len(color_list)]
            figure = item._plot(item_color, figure)
            
        camera = dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.25, y=1.25, z=1.25),
        )

        # Update figure properties for improved visualization
        figure.update_layout(
            showlegend=False,
            scene_camera=camera,
            width=800,
            height=800,
            template="plotly_dark",
        )
        max_x = self.position[0] + self.width
        max_y = self.position[1] + self.height
        max_z = self.position[2] + self.depth
        figure.update_layout(
            scene=dict(
                xaxis=dict(nticks=int(max_x + 2), range=[0, max_x + 5]),
                yaxis=dict(nticks=int(max_y + 2), range=[0, max_y + 5]),
                zaxis=dict(nticks=int(max_z + 2), range=[0, max_z + 5]),
                aspectmode="cube",
            ),
            width=800,
            margin=dict(r=20, l=10, b=10, t=10),
        )
        figure.update_scenes(
            xaxis_showgrid=False, yaxis_showgrid=False, zaxis_showgrid=False
        )
        figure.update_scenes(
            xaxis_showticklabels=False,
            yaxis_showticklabels=False,
            zaxis_showticklabels=False,
        )

        return figure

# class Packer:

#     def __init__(self):
#         ''' '''
#         self.bins = []
#         self.items = []
#         self.unfit_items = []
#         self.total_items = 0
#         self.binding = []
#         # self.apex = []


#     def addBin(self, bin):
#         ''' '''
#         return self.bins.append(bin)


#     def addItem(self, item):
#         ''' '''
#         self.total_items = len(self.items) + 1

#         return self.items.append(item)


#     def pack2Bin(self, bin, item,fix_point,check_stable,support_surface_ratio):
#         ''' pack item to bin '''
#         fitted = False
#         bin.fix_point = fix_point
#         bin.check_stable = check_stable
#         bin.support_surface_ratio = support_surface_ratio

#         # first put item on (0,0,0) , if corner exist ,first add corner in box. 
#         if bin.corner != 0 and not bin.items:
#             corner_lst = bin.addCorner()
#             for i in range(len(corner_lst)) :
#                 bin.putCorner(i,corner_lst[i])

#         elif not bin.items:
#             response = bin.putItem(item, item.position)

#             if not response:
#                 bin.unfitted_items.append(item)
#             return

#         for axis in range(0, 3):
#             items_in_bin = bin.items
#             for ib in items_in_bin:
#                 pivot = [0, 0, 0]
#                 w, h, d = ib.getDimension()
#                 if axis == Axis.WIDTH:
#                     pivot = [ib.position[0] + w,ib.position[1],ib.position[2]]
#                 elif axis == Axis.HEIGHT:
#                     pivot = [ib.position[0],ib.position[1] + h,ib.position[2]]
#                 elif axis == Axis.DEPTH:
#                     pivot = [ib.position[0],ib.position[1],ib.position[2] + d]
                    
#                 if bin.putItem(item, pivot, axis):
#                     fitted = True
#                     break
#             if fitted:
#                 break
#         if not fitted:
#             bin.unfitted_items.append(item)


#     def sortBinding(self,bin):
#         ''' sorted by binding '''
#         b,front,back = [],[],[]
#         for i in range(len(self.binding)):
#             b.append([]) 
#             for item in self.items:
#                 if item.name in self.binding[i]:
#                     b[i].append(item)
#                 elif item.name not in self.binding:
#                     if len(b[0]) == 0 and item not in front:
#                         front.append(item)
#                     elif item not in back and item not in front:
#                         back.append(item)

#         min_c = min([len(i) for i in b])
        
#         sort_bind =[]
#         for i in range(min_c):
#             for j in range(len(b)):
#                 sort_bind.append(b[j][i])
        
#         for i in b:
#             for j in i:
#                 if j not in sort_bind:
#                     self.unfit_items.append(j)

#         self.items = front + sort_bind + back
#         return


#     def putOrder(self):
#         '''Arrange the order of items '''
#         r = []
#         for i in self.bins:
#             # open top container
#             if i.put_type == 2:
#                 i.items.sort(key=lambda item: item.position[0], reverse=False)
#                 i.items.sort(key=lambda item: item.position[1], reverse=False)
#                 i.items.sort(key=lambda item: item.position[2], reverse=False)
#             # general container
#             elif i.put_type == 1:
#                 i.items.sort(key=lambda item: item.position[1], reverse=False)
#                 i.items.sort(key=lambda item: item.position[2], reverse=False)
#                 i.items.sort(key=lambda item: item.position[0], reverse=False)
#             else :
#                 pass
#         return


#     def gravityCenter(self,bin):
#         ''' 
#         Deviation Of Cargo gravity distribution
#         ''' 
#         w = int(bin.width)
#         h = int(bin.height)
#         d = int(bin.depth)

#         area1 = [set(range(0,w//2+1)),set(range(0,h//2+1)),0]
#         area2 = [set(range(w//2+1,w+1)),set(range(0,h//2+1)),0]
#         area3 = [set(range(0,w//2+1)),set(range(h//2+1,h+1)),0]
#         area4 = [set(range(w//2+1,w+1)),set(range(h//2+1,h+1)),0]
#         area = [area1,area2,area3,area4]

#         for i in bin.items:

#             x_st = int(i.position[0])
#             y_st = int(i.position[1])
#             if i.rotation_type == 0:
#                 x_ed = int(i.position[0] + i.width)
#                 y_ed = int(i.position[1] + i.height)
#             elif i.rotation_type == 1:
#                 x_ed = int(i.position[0] + i.height)
#                 y_ed = int(i.position[1] + i.width)
#             elif i.rotation_type == 2:
#                 x_ed = int(i.position[0] + i.height)
#                 y_ed = int(i.position[1] + i.depth)
#             elif i.rotation_type == 3:
#                 x_ed = int(i.position[0] + i.depth)
#                 y_ed = int(i.position[1] + i.height)
#             elif i.rotation_type == 4:
#                 x_ed = int(i.position[0] + i.depth)
#                 y_ed = int(i.position[1] + i.width)
#             elif i.rotation_type == 5:
#                 x_ed = int(i.position[0] + i.width)
#                 y_ed = int(i.position[1] + i.depth)

#             x_set = set(range(x_st,int(x_ed)+1))
#             y_set = set(range(y_st,y_ed+1))

#             # cal gravity distribution
#             for j in range(len(area)):
#                 if x_set.issubset(area[j][0]) and y_set.issubset(area[j][1]) : 
#                     area[j][2] += int(i.weight)
#                     break
#                 # include x and !include y
#                 elif x_set.issubset(area[j][0]) == True and y_set.issubset(area[j][1]) == False and len(y_set & area[j][1]) != 0 : 
#                     y = len(y_set & area[j][1]) / (y_ed - y_st) * int(i.weight)
#                     area[j][2] += y
#                     if j >= 2 :
#                         area[j-2][2] += (int(i.weight) - x)
#                     else :
#                         area[j+2][2] += (int(i.weight) - y)
#                     break
#                 # include y and !include x
#                 elif x_set.issubset(area[j][0]) == False and y_set.issubset(area[j][1]) == True and len(x_set & area[j][0]) != 0 : 
#                     x = len(x_set & area[j][0]) / (x_ed - x_st) * int(i.weight)
#                     area[j][2] += x
#                     if j >= 2 :
#                         area[j-2][2] += (int(i.weight) - x)
#                     else :
#                         area[j+2][2] += (int(i.weight) - x)
#                     break
#                 # !include x and !include y
#                 elif x_set.issubset(area[j][0])== False and y_set.issubset(area[j][1]) == False and len(y_set & area[j][1]) != 0  and len(x_set & area[j][0]) != 0 :
#                     all = (y_ed - y_st) * (x_ed - x_st)
#                     y = len(y_set & area[0][1])
#                     y_2 = y_ed - y_st - y
#                     x = len(x_set & area[0][0])
#                     x_2 = x_ed - x_st - x
#                     area[0][2] += x * y / all * int(i.weight)
#                     area[1][2] += x_2 * y / all * int(i.weight)
#                     area[2][2] += x * y_2 / all * int(i.weight)
#                     area[3][2] += x_2 * y_2 / all * int(i.weight)
#                     break
            
#         r = [area[0][2],area[1][2],area[2][2],area[3][2]]
#         result = []
#         for i in r :
#             result.append(round(i / sum(r) * 100,2))
#         return result


#     def pack(self, bigger_first=False,distribute_items=True,fix_point=True,check_stable=True,support_surface_ratio=0.75,binding=[],number_of_decimals=DEFAULT_NUMBER_OF_DECIMALS):
#         '''pack master func '''
#         # set decimals
#         for bin in self.bins:
#             bin.formatNumbers(number_of_decimals)

#         for item in self.items:
#             item.formatNumbers(number_of_decimals)
#         # add binding attribute
#         self.binding = binding
#         # Bin : sorted by volumn
#         self.bins.sort(key=lambda bin: bin.getVolume(), reverse=bigger_first)
#         # Item : sorted by volumn -> sorted by loadbear -> sorted by level -> binding
#         self.items.sort(key=lambda item: item.getVolume(), reverse=bigger_first)
#         # self.items.sort(key=lambda item: item.getMaxArea(), reverse=bigger_first)
#         self.items.sort(key=lambda item: item.loadbear, reverse=True)
#         self.items.sort(key=lambda item: item.level, reverse=False)
#         # sorted by binding
#         if binding != []:
#             self.sortBinding(bin)

#         for idx,bin in enumerate(self.bins):
#             # pack item to bin
#             for item in self.items:
#                 self.pack2Bin(bin, item, fix_point, check_stable, support_surface_ratio)

#             if binding != []:
#                 # resorted
#                 self.items.sort(key=lambda item: item.getVolume(), reverse=bigger_first)
#                 self.items.sort(key=lambda item: item.loadbear, reverse=True)
#                 self.items.sort(key=lambda item: item.level, reverse=False)
#                 # clear bin
#                 bin.items = []
#                 bin.unfitted_items = self.unfit_items
#                 bin.fit_items = np.array([[0,bin.width,0,bin.height,0,0]])
#                 # repacking
#                 for item in self.items:
#                     self.pack2Bin(bin, item,fix_point,check_stable,support_surface_ratio)
            
#             # Deviation Of Cargo Gravity Center 
#             self.bins[idx].gravity = self.gravityCenter(bin)

#             if distribute_items :
#                 for bitem in bin.items:
#                     no = bitem.partno
#                     for item in self.items :
#                         if item.partno == no :
#                             self.items.remove(item)
#                             break

#         # put order of items
#         self.putOrder()

#         if self.items != []:
#             self.unfit_items = copy.deepcopy(self.items)
#             self.items = []
#         # for item in self.items.copy():
#         #     if item in bin.unfitted_items:
#         #         self.items.remove(item)

class Packer:

    def __init__(self):
        self.bins = []
        self.items = []
        self.unfit_items = []
        self.total_items = 0
        self.binding = []

    def addBin(self, bin):
        self.bins.append(bin)

    def addItem(self, item):
        self.items.append(item)
        self.total_items += 1

    def _placeItemAtOrigin(self, bin, item):
        response = bin.putItem(item, item.position)
        if not response:
            bin.unfitted_items.append(item)
        return response

    def _findPivotAndTryFit(self, bin, item):
        for axis in range(3):
            for ib in bin.items:
                pivot = self._calculatePivot(ib, axis)
                if bin.putItem(item, pivot, axis):
                    return True
        return False

    def _calculatePivot(self, item, axis):
        pivot = [0, 0, 0]
        w, h, d = item.getDimension()
        if axis == Axis.WIDTH:
            pivot[0] = item.position[0] + w
        elif axis == Axis.HEIGHT:
            pivot[1] = item.position[1] + h
        elif axis == Axis.DEPTH:
            pivot[2] = item.position[2] + d
        return pivot

    def pack2Bin(self, bin, item, fix_point, check_stable, support_surface_ratio):
        bin.fix_point = fix_point
        bin.check_stable = check_stable
        bin.support_surface_ratio = support_surface_ratio

        if bin.corner and not bin.items:
            corner_lst = bin.addCorner()
            # for corner in corner_lst:
            #     bin.putCorner(corner)
            for i in range(len(corner_lst)) :
                bin.putCorner(i,corner_lst[i])
                
        elif not bin.items:
            if self._placeItemAtOrigin(bin, item):
                return

        if not self._findPivotAndTryFit(bin, item):
            bin.unfitted_items.append(item)

    def sortBinding(self):
        binding_groups = {name: [] for name in self.binding}
        unbound_items = []

        for item in self.items:
            bound = False
            for group in binding_groups:
                if item.name in group:
                    binding_groups[group].append(item)
                    bound = True
                    break
            if not bound:
                unbound_items.append(item)

        sorted_items = []
        for group in binding_groups.values():
            sorted_items.extend(group)

        self.items = unbound_items[:len(unbound_items)//2] + sorted_items + unbound_items[len(unbound_items)//2:]

    def putOrder(self):
        for bin in self.bins:
            if bin.put_type == 2:  # Open-top container
                bin.items.sort(key=lambda item: (item.position[0], item.position[1], item.position[2]))
            elif bin.put_type == 1:  # General container
                bin.items.sort(key=lambda item: (item.position[1], item.position[2], item.position[0]))

    def gravityCenter(self, bin):
        # Convert bin dimensions to integers
        w = int(bin.width)
        h = int(bin.height)
        d = int(bin.depth)

        # Define areas for gravity calculation
        areas = [
            (range(0, w // 2 + 1), range(0, h // 2 + 1)),
            (range(w // 2 + 1, w + 1), range(0, h // 2 + 1)),
            (range(0, w // 2 + 1), range(h // 2 + 1, h + 1)),
            (range(w // 2 + 1, w + 1), range(h // 2 + 1, h + 1))
        ]
        weights = [0, 0, 0, 0]

        # Calculate gravity distribution for each item
        for item in bin.items:
            # Convert item position and dimensions to integers
            x_st, y_st = int(item.position[0]), int(item.position[1])
            x_ed, y_ed = self._calculateEdges(item)

            x_set, y_set = set(range(x_st, int(x_ed) + 1)), set(range(y_st, int(y_ed) + 1))

            for idx, (x_range, y_range) in enumerate(areas):
                x_overlap = len(x_set & set(x_range))
                y_overlap = len(y_set & set(y_range))
                if x_overlap and y_overlap:
                    weights[idx] += x_overlap * y_overlap / ((int(x_ed) - x_st) * (int(y_ed) - y_st)) * int(item.weight)

        total_weight = sum(weights)
        gravity_distribution = [round(w / total_weight * 100, 2) for w in weights]
        return gravity_distribution


    def _calculateEdges(self, item):
        if item.rotation_type == 0:
            return item.position[0] + item.width, item.position[1] + item.height
        elif item.rotation_type == 1:
            return item.position[0] + item.height, item.position[1] + item.width
        elif item.rotation_type == 2:
            return item.position[0] + item.height, item.position[1] + item.depth
        elif item.rotation_type == 3:
            return item.position[0] + item.depth, item.position[1] + item.height
        elif item.rotation_type == 4:
            return item.position[0] + item.depth, item.position[1] + item.width
        elif item.rotation_type == 5:
            return int(item.position[0] + item.width), int(item.position[1] + item.depth)

    def pack(self, bigger_first=False, distribute_items=True, fix_point=True, check_stable=True, support_surface_ratio=0.75, binding=[], number_of_decimals=DEFAULT_NUMBER_OF_DECIMALS):
        for bin in self.bins:
            bin.formatNumbers(number_of_decimals)

        for item in self.items:
            item.formatNumbers(number_of_decimals)

        self.binding = binding
        self.bins.sort(key=lambda bin: bin.getVolume(), reverse=bigger_first)
        self.items.sort(key=lambda item: (item.getVolume(), item.loadbear, item.level), reverse=True)

        if binding:
            self.sortBinding()

        for bin in self.bins:
            for item in self.items:
                self.pack2Bin(bin, item, fix_point, check_stable, support_surface_ratio)

            bin.gravity = self.gravityCenter(bin)

            if distribute_items:
                for packed_item in bin.items:
                    self.items = [item for item in self.items if item.partno != packed_item.partno]

        self.putOrder()

        if self.items:
            self.unfit_items.extend(self.items)
            self.items.clear()
