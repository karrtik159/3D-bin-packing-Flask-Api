import numpy as np
from .constants import RotationType, Axis
from .auxiliary_methods import intersect, set2Decimal,generate_vertices
import numpy as np
from math import sqrt

# required to plot a representation of Bin and contained items
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from typing import Type
import copy


DEFAULT_NUMBER_OF_DECIMALS = 0
START_POSITION = [0, 0, 0]



class Item:

    def __init__(self, partno,name, WHD, weight, level, loadbear=9999, updown=1, color=1):
        ''' '''
        self.partno = partno
        self.name = name
        # self.typeof = typeof
        self.width = WHD[0]
        self.height = WHD[1]
        self.depth = WHD[2]
        self.weight = weight
        # Packing Priority level ,choose 1-3
        self.level = level
        # loadbear
        self.loadbear = loadbear
        # Upside down? True or False
        self.updown = True if updown == 1 else False
        self.valid_rotations= rotate = RotationType.ALL if self.updown == True else RotationType.Notupdown
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
        hover_text=self.name+" "+self.partno 
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
                        text=hover_text,
                        hoverinfo='text',
                        name=hover_text,  # This ensures it appears in the legend
                        legendgroup=hover_text
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
                    name=hover_text,  # This ensures it appears in the legend
                    hoverinfo='none',  # No hover information for edges
                    legendgroup=hover_text
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
                    text=hover_text,
                    hoverinfo='text',
                    name=hover_text,  # This ensures it appears in the legend
                    legendgroup=hover_text
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
                    name=hover_text,  # This ensures it appears in the legend
                    hoverinfo='none',  # No hover information for edges
                    legendgroup=hover_text
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
        self.total_items = 0 # number of total items in one bin
        self.items = []
        self.fit_items = np.array([[0,WHD[0],0,WHD[1],0,0]])
        self.unfitted_items = []
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS
        self.fix_point = False
        self.check_stable = False
        self.support_surface_ratio = 0
        self.put_type = put_type
        self.distances = {}

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


    # def putItem(self, item, pivot,axis=None):
    #     """
    #     Put an item in the bin at a given pivot point.

    #     Args:
    #         item (Item): The item to be placed in the bin.
    #         pivot (list): The pivot point of the item in the bin.
    #         axis (Optional[list]): The axis of rotation for the item. Defaults to None.

    #     Returns:
    #         bool: True if the item is successfully placed in the bin, False otherwise.
    #     """
    #     fit = False
    #     valid_item_position = item.position
    #     item.position = pivot
    #     rotate = RotationType.ALL if item.updown == True else RotationType.Notupdown
    #     for i in range(0, len(rotate)):
    #         item.rotation_type = i
    #         dimension = item.getDimension()
    #         # rotatate
    #         if (
    #             self.width < pivot[0] + dimension[0] or
    #             self.height < pivot[1] + dimension[1] or
    #             self.depth < pivot[2] + dimension[2]
    #         ):
    #             continue

    #         fit = True

    #         for current_item_in_bin in self.items:
    #             if intersect(current_item_in_bin, item):
    #                 fit = False
    #                 break

    #         if fit:
    #             # cal total weight
    #             if self.getTotalWeight() + item.weight > self.max_weight:
    #                 fit = False
    #                 return fit
                
    #             # fix point float prob
    #             if self.fix_point == True :
                        
    #                 [w,h,d] = dimension
    #                 [x,y,z] = [float(pivot[0]),float(pivot[1]),float(pivot[2])]

    #                 for i in range(3):
    #                     # fix height
    #                     y = self.checkHeight([x,x+float(w),y,y+float(h),z,z+float(d)])
    #                     # fix width
    #                     x = self.checkWidth([x,x+float(w),y,y+float(h),z,z+float(d)])
    #                     # fix depth
    #                     z = self.checkDepth([x,x+float(w),y,y+float(h),z,z+float(d)])

    #                 # check stability on item 
    #                 # rule : 
    #                 # 1. Define a support ratio, if the ratio below the support surface does not exceed this ratio, compare the second rule.
    #                 # 2. If there is no support under any vertices of the bottom of the item, then fit = False.
    #                 if self.check_stable == True :
    #                     # Cal the surface area of ​​item.
    #                     item_area_lower = int(dimension[0] * dimension[1])
    #                     # Cal the surface area of ​​the underlying support.
    #                     support_area_upper = 0
    #                     for i in self.fit_items:
    #                         # Verify that the lower support surface area is greater than the upper support surface area * support_surface_ratio.
    #                         if z == i[5]  :
    #                             area = len(set([ j for j in range(int(x),int(x+int(w)))]) & set([ j for j in range(int(i[0]),int(i[1]))])) * \
    #                             len(set([ j for j in range(int(y),int(y+int(h)))]) & set([ j for j in range(int(i[2]),int(i[3]))]))
    #                             support_area_upper += area

    #                     # If not , get four vertices of the bottom of the item.
    #                     if support_area_upper / item_area_lower < self.support_surface_ratio :
    #                         four_vertices = [[x,y],[x+float(w),y],[x,y+float(h)],[x+float(w),y+float(h)]]
    #                         #  If any vertices is not supported, fit = False.
    #                         c = [False,False,False,False]
    #                         for i in self.fit_items:
    #                             if z == i[5] :
    #                                 for jdx,j in enumerate(four_vertices) :
    #                                     if (i[0] <= j[0] <= i[1]) and (i[2] <= j[1] <= i[3]) :
    #                                         c[jdx] = True
    #                         if False in c :
    #                             item.position = valid_item_position
    #                             fit = False
    #                             return fit
                        
    #                 self.fit_items = np.append(self.fit_items,np.array([[x,x+float(w),y,y+float(h),z,z+float(d)]]),axis=0)
    #                 item.position = [set2Decimal(x),set2Decimal(y),set2Decimal(z)]

    #             if fit :
    #                 self.items.append(copy.deepcopy(item))

    #         else :
    #             item.position = valid_item_position

    #         return fit

    #     else :
    #         item.position = valid_item_position

    #     return fit

    def putItem(self, item, pivot, distance_3d):
        """Evaluate whether an item can be placed into a certain bin with which orientation. If yes, perform put action.
        Args:
            item: any item in item list.
            pivot: an (x, y, z) coordinate, the back-lower-left corner of the item will be placed at the pivot.
            distance_3d: a 3D parameter to determine which orientation should be chosen.
        Returns:
            Boolean variable: False when an item couldn't be placed into the bin; True when an item could be placed and perform put action.
        """

        fit = False
        valid_item_position = item.position
        item.position = pivot
        # rotation_type_list = rotate = RotationType.ALL if item.updown == True else RotationType.Notupdown
        rotation_type_list = self.can_hold_item_with_rotation(item, pivot)
        margins_3d_list = []
        margins_3d_list_temp = []
        margin_3d = []
        margin_2d = []
        margin_1d = []

        n = 0
        m = 0
        p = 0

        if not rotation_type_list:
            return fit

        else:
            for rotation in rotation_type_list:
                fit = True
                item.rotation_type = rotation
                dimension = item.getDimension()

                # Check if the item intersects with any other item in the bin
                for current_item_in_bin in self.items:
                    if intersect(current_item_in_bin, item):
                        fit = False
                        break

                if not fit:
                    continue

                # Check if adding this item exceeds the bin's maximum weight
                if self.getTotalWeight() + item.weight > self.max_weight:
                    fit = False
                    continue

                # Fix point floating issues if necessary
                if self.fix_point == True :
                    [w, h, d] = dimension
                    [x, y, z] = [float(pivot[0]), float(pivot[1]), float(pivot[2])]

                    for i in range(3):
                        # Fix height
                        y = self.checkHeight([x, x + float(w), y, y + float(h), z, z + float(d)])
                        # Fix width
                        x = self.checkWidth([x, x + float(w), y, y + float(h), z, z + float(d)])
                        # Fix depth
                        z = self.checkDepth([x, x + float(w), y, y + float(h), z, z + float(d)])

                    # check stability on item
                    # rule :
                    # 1. Define a support ratio, if the ratio below the support surface does not exceed this ratio, compare the second rule.
                    # 2. If there is no support under any vertices of the bottom of the item, then fit = False.
                    if self.check_stable == True :
                        item_area_lower = int(dimension[0] * dimension[1])
                        support_area_upper = 0
                        for i in self.fit_items:
                            if z == i[5]:
                                area = len(set([j for j in range(int(x), int(x + int(w)))]) & set(
                                    [j for j in range(int(i[0]), int(i[1]))])) * \
                                       len(set([j for j in range(int(y), int(y + int(h)))]) & set(
                                           [j for j in range(int(i[2]), int(i[3]))]))
                                support_area_upper += area

                        if support_area_upper / item_area_lower < self.support_surface_ratio:
                            four_vertices = [[x, y], [x + float(w), y], [x, y + float(h)], [x + float(w), y + float(h)]]
                            c = [False, False, False, False]
                            for i in self.fit_items:
                                if z == i[5]:
                                    for jdx, j in enumerate(four_vertices):
                                        if (i[0] <= j[0] <= i[1]) and (i[2] <= j[1] <= i[3]):
                                            c[jdx] = True
                            if False in c:
                                item.position = valid_item_position
                                fit = False
                                continue

                    self.fit_items = np.append(self.fit_items, np.array([[x, x + float(w), y, y + float(h), z, z + float(d)]]), axis=0)
                    item.position = [set2Decimal(x), set2Decimal(y), set2Decimal(z)]

                if fit:
                    margins_3d = [distance_3d[0] - dimension[0],
                                distance_3d[1] - dimension[1],
                                distance_3d[2] - dimension[2]]
                    margins_3d_temp = sorted(margins_3d)
                    margins_3d_list.append(margins_3d)
                    margins_3d_list_temp.append(margins_3d_temp)

            # Process margins to find the best fitting orientation
            while p < len(margins_3d_list_temp):
                margin_3d.append(margins_3d_list_temp[p][0])
                p += 1

            p = 0
            while p < len(margins_3d_list_temp):
                if margins_3d_list_temp[p][0] == min(margin_3d):
                    n += 1
                    margin_2d.append(margins_3d_list_temp[p][1])

                p += 1

            if n == 1:
                p = 0
                while p < len(margins_3d_list_temp):
                    if margins_3d_list_temp[p][0] == min(margin_3d):
                        item.rotation_type = rotation_type_list[p]
                        self.items.append(item)
                        self.total_items += 1
                        return fit

                    p += 1

            else:
                p = 0
                while p < len(margins_3d_list_temp):
                    if (
                        margins_3d_list_temp[p][0] == min(margin_3d) and
                        margins_3d_list_temp[p][1] == min(margin_2d)
                    ):
                        m += 1
                        margin_1d.append(margins_3d_list_temp[p][2])

                    p += 1

            if m == 1:
                p = 0
                while p < len(margins_3d_list_temp):
                    if (
                        margins_3d_list_temp[p][0] == min(margin_3d) and
                        margins_3d_list_temp[p][1] == min(margin_2d)
                    ):
                        item.rotation_type = rotation_type_list[p]
                        self.items.append(item)
                        self.total_items += 1
                        return fit

                    p += 1

            else:
                p = 0
                while p < len(margins_3d_list_temp):
                    if (
                        margins_3d_list_temp[p][0] == min(margin_3d) and
                        margins_3d_list_temp[p][1] == min(margin_2d) and
                        margins_3d_list_temp[p][2] == min(margin_1d)
                    ):
                        item.rotation_type = rotation_type_list[p]
                        self.items.append(item)
                        self.total_items += 1
                        return fit

                    p += 1

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
                    # typeof='cube',
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


    # def can_hold_item_with_rotation(self, item, pivot):
    #     """Evaluate whether one item can be placed into bin with all optional orientations.
    #     Args:
    #         item: any item in item list.
    #         pivot: an (x, y, z) coordinate, the back-lower-left corner of the item will be placed at the pivot.
    #     Returns:
    #         a list containing all optional orientations. If not, return an empty list.
    #     """
    #     # 1. Determine if the item can fit in the bin.
    #     fit = False
    #     valid_item_position = item.position
    #     item.position = pivot
    #     rotation_type_list = []
    #
    #
    #     for i in item.valid_rotations:
    #         item.rotation_type = i
    #         dimension = item.getDimension()
    #         if (
    #             pivot[0] + dimension[0] <= self.width and  # x-axis
    #             pivot[1] + dimension[1] <= self.height and  # y-axis
    #             pivot[2] + dimension[2] <= self.depth     # z-axis
    #         ):
    #
    #             fit = True
    #
    #             for current_item_in_bin in self.items:
    #                 if intersect(current_item_in_bin, item):
    #                     fit = False
    #                     # item.position = [0, 0, 0]
    #                     break
    #
    #             if fit:
    #                 if self.getTotalWeight() + item.weight > self.max_weight: # estimate whether bin reaches its capacity
    #                     fit = False
    #                     # item.position = [0, 0, 0]
    #                     continue
    #
    #                 else:
    #                     rotation_type_list.append(item.rotation_type)
    #
    #         else:
    #             continue
    #
    #     return rotation_type_list

    # def can_hold_item_with_rotation(self, item, pivot, min_distance=0):
    #     """Evaluate whether one item can be placed into bin with all optional orientations, ensuring
    #     it doesn't overlap with existing items, exceeds weight limits, or violates the minimum distance
    #     from other items.
    #
    #     Args:
    #         item: The item to be placed in the bin.
    #         pivot: An (x, y, z) coordinate, where the back-lower-left corner of the item will be placed.
    #         min_distance: The minimum allowable distance from other items (default is 0).
    #
    #     Returns:
    #         A list containing the best rotation type based on the maximum of minimum distances.
    #         If none are valid, returns an empty list.
    #     """
    #
    #     item.position = pivot
    #     valid_rotations = []  # Store valid rotations and their minimum distances
    #
    #     for rotation in item.valid_rotations:
    #         item.rotation_type = rotation
    #         dimension = item.getDimension()
    #
    #         # Check if the item fits within the bin's boundaries
    #         if (
    #                 pivot[0] + dimension[0] <= self.width and  # x-axis
    #                 pivot[1] + dimension[1] <= self.height and  # y-axis
    #                 pivot[2] + dimension[2] <= self.depth  # z-axis
    #         ):
    #             fit = True
    #             min_distance_for_rotation = float('inf')  # Initialize to a large number
    #
    #             # Check for intersection with other items in the bin
    #             for current_item_in_bin in self.items:
    #                 if intersect(current_item_in_bin, item):
    #                     fit = False
    #                     break
    #
    #             if fit:
    #                 # Check if the total weight exceeds the bin's max weight capacity
    #                 if self.getTotalWeight() + item.weight > self.max_weight:
    #                     fit = False
    #                     item.position = [0, 0, 0]
    #                     continue
    #
    #                 # Check the minimum distance constraint
    #                 for placed_item in self.items:  # Assuming self.items is a list of items already in the bin
    #                     placed_item_dim = placed_item.getDimension()
    #
    #                     # Calculate the distance between the pivot points of the two items
    #                     dx = pivot[0] - placed_item.position[0]
    #                     dy = pivot[1] - placed_item.position[1]
    #                     dz = pivot[2] - placed_item.position[2]
    #
    #                     distance = sqrt(dx ** 2 + dy ** 2 + dz ** 2)
    #
    #                     # Save the calculated distance in the dictionary for tracking
    #                     self.distances[f'previous item: {placed_item.partno}, current item: {item.partno}, rotation type: {rotation}'] = distance
    #
    #                     # Track the smallest distance for this rotation
    #                     if distance < min_distance_for_rotation:
    #                         min_distance_for_rotation = distance
    #
    #                     # If the distance is less than the minimum required, invalidate this rotation
    #                     if distance < min_distance:
    #                         fit = False
    #                         break
    #
    #                 # If the item fits within the bin, meets weight, intersection, and distance requirements
    #                 if fit:
    #                     valid_rotations.append((rotation, min_distance_for_rotation))
    #
    #     # If there are valid rotations, select the one with the maximum minimum distance
    #     if valid_rotations:
    #         # Sort by the minimum distance (second element in the tuple) and choose the max
    #         best_rotation = max(valid_rotations, key=lambda x: x[1])[0]
    #         return [best_rotation]
    #
    #     return []
    def can_hold_item_with_rotation(self, item, pivot, min_distance=5):
        """Evaluate whether one item can be placed into a bin with all optional orientations, ensuring
        it doesn't overlap with existing items, exceeds weight limits, or violates the minimum distance
        from other items.

        Args:
            item: The item to be placed in the bin.
            pivot: An (x, y, z) coordinate, where the back-lower-left corner of the item will be placed.
            min_distance: The minimum allowable distance from other items (default is 0).

        Returns:
            A list containing the best rotation type based on the maximum of minimum distances and
            the shortest surface ratio of the longest side.
            If none are valid, returns an empty list.
        """

        item.position = pivot
        valid_rotations = []  # Store valid rotations, their minimum distances, and surface ratios

        for rotation in item.valid_rotations:
            item.rotation_type = rotation
            dimension = item.getDimension()

            # Check if the item fits within the bin's boundaries
            if (
                    pivot[0] + dimension[0] <= self.width and  # x-axis
                    pivot[1] + dimension[1] <= self.height and  # y-axis
                    pivot[2] + dimension[2] <= self.depth  # z-axis
            ):
                fit = True
                min_distance_for_rotation = float('inf')  # Initialize to a large number

                # Check for intersection with other items in the bin
                for current_item_in_bin in self.items:
                    if intersect(current_item_in_bin, item):
                        fit = False
                        break

                if fit:
                    # Check if the total weight exceeds the bin's max weight capacity
                    if self.getTotalWeight() + item.weight > self.max_weight:
                        fit = False
                        continue

                    # Check the minimum distance constraint
                    for placed_item in self.items:
                        placed_item_dim = placed_item.getDimension()

                        # Calculate the distance between the pivot points of the two items
                        dx = pivot[0] - placed_item.position[0]
                        dy = pivot[1] - placed_item.position[1]
                        dz = pivot[2] - placed_item.position[2]

                        distance = sqrt(dx ** 2 + dy ** 2 + dz ** 2)

                        # Save the calculated distance in the dictionary for tracking
                        self.distances[
                            f'"previous item": "{placed_item.partno}", "current item": "{item.partno}", "rotation type": "{rotation}"'] = distance

                        # Track the smallest distance for this rotation
                        if distance < min_distance_for_rotation:
                            min_distance_for_rotation = distance

                        # If the distance is less than the minimum required, invalidate this rotation
                        if distance < min_distance:
                            fit = False
                            break

                    # If the item fits within the bin, meets weight, intersection, and distance requirements
                    if fit:
                        # Calculate surface area ratios
                        longest_side = max(self.width, self.height, self.depth)
                        
                        if longest_side == self.width:
                            # Logic for x (width) being the longest side
                            surface_area_1 = dimension[0] * dimension[1]  # Assuming dimension[0] is along x and dimension[1] is along y
                        elif longest_side == self.height:
                            # Logic for y (height) being the longest side
                            surface_area_1 = dimension[0] * dimension[1]   # Assuming dimension[2] is along z and dimension[0] is along x
                        else:
                            # Logic for z (depth) being the longest side
                            surface_area_1 = dimension[2] * dimension[0]  # Assuming dimension[1] is along y and dimension[2] is along z

                        surface_ratios = [
                            surface_area_1 / longest_side
                        ]

                        valid_rotations.append((rotation, min_distance_for_rotation, surface_ratios))


                            
        # If there are valid rotations, select the one with the best criteria
        if valid_rotations:
            # Sort by minimum distance first (in descending order) and then by surface ratio (in ascending order)
            valid_rotations.sort(key=lambda x: (-x[1],x[2]))
            # print("Valid rotations: ",valid_rotations)
            if valid_rotations[0] is None:
                raise ValueError("Best rotation is None")
            best_rotation = valid_rotations[0][0]
            if best_rotation is None:
                raise ValueError("Best rotation is None")
            return [best_rotation]

        return []

    

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
                    showlegend=False,
                )
            )
        color_list = px.colors.qualitative.Dark24

        for idx, item in enumerate(self.items):
            # Combine the volume and the item's name to create a unique key
            unique_key = int(item.getVolume()) + sum(ord(char) for char in item.name)

            # Select a color based on the unique key
            item_color = color_list[unique_key % len(color_list)]

            # Plot the item with the selected color
            figure = item._plot(item_color, figure)

        camera = dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.25, y=1.25, z=1.25),
        )

        # Update figure properties for improved visualization
        figure.update_layout(
            showlegend=True,
            scene_camera=camera,
            width=1600  ,
            height=900,
            template="plotly_dark",
        )
        max_x = self.position[0] + self.width
        max_y = self.position[1] + self.height
        max_z = self.position[2] + self.depth
        aspect_ratio = dict(
        x=self.width / max([self.width, self.height, self.depth]),
        y=self.height / max([self.width, self.height, self.depth]),
        z=self.depth / max([self.width, self.height, self.depth])
    )
        figure.update_layout(
            scene=dict(
                xaxis=dict(nticks=int(max_x + 2), range=[0, max_x + 5]),
                yaxis=dict(nticks=int(max_y + 2), range=[0, max_y + 5]),
                zaxis=dict(nticks=int(max_z + 2), range=[0, max_z + 5]),
                # aspectmode="cube",
                aspectratio=aspect_ratio
            ),
            width=1600,
            margin=dict(r=10, l=10, b=10, t=10),
        )
        figure.update_scenes(
            xaxis_showgrid=True, yaxis_showgrid=True, zaxis_showgrid=True
        )
        figure.update_scenes(
            xaxis_showticklabels=True,
            yaxis_showticklabels=True,
            zaxis_showticklabels=True,
        )
        # print(self.distances)
        return figure

class Packer:

    def __init__(self):
        ''' '''
        self.bins = []
        self.items = []
        self.unfit_items = []
        self.total_items = 0
        self.binding = []
        # self.apex = []


    def addBin(self, bin):
        ''' '''
        return self.bins.append(bin)


    def addItem(self, item):
        ''' '''
        self.total_items = len(self.items) + 1

        return self.items.append(item)

    def pivot_list(self, bin, item):
        """Obtain all optional pivot points that one item could be placed into a certain bin.
        Args:
            bin: a bin in bin list that a certain item will be placed into.
            item: an unplaced item in item list.
        Returns:
            a pivot_list containing all optional pivot points that the item could be placed into a certain bin.
        """

        pivot_list = []

        for axis in range(0, 3):
            items_in_bin = bin.items

            for ib in items_in_bin:
                pivot = [0, 0, 0]
                if axis == Axis.WIDTH: # axis = 0/ x-axis
                    pivot = [ib.position[0] + ib.getDimension()[0],
                            ib.position[1],
                            ib.position[2]]
                elif axis == Axis.HEIGHT: # axis = 1/ y-axis
                    pivot = [ib.position[0],
                            ib.position[1] + ib.getDimension()[1],
                            ib.position[2]]
                elif axis == Axis.DEPTH: # axis = 2/ z-axis
                    pivot = [ib.position[0],
                            ib.position[1],
                            ib.position[2] + ib.getDimension()[2]]

                pivot_list.append(pivot)

        return pivot_list

    def choose_pivot_point(self, bin, item):
        """Choose the optimal one from all optional pivot points of the item after comparison.
        Args:
            bin: a bin in bin list that a certain item will be placed into.
            item: an unplaced item in item list.
        Returns:
            the optimal pivot point that a item could be placed into a bin.
        """

        can_put = False
        pivot_available = []
        pivot_available_temp = []
        vertex_3d = []
        vertex_2d = []
        vertex_1d = []

        n = 0
        m = 0
        p = 0

        pivot_list = self.pivot_list(bin, item)

        for pivot in pivot_list:
            try_put_item = bin.can_hold_item_with_rotation(item, pivot)

            if try_put_item:
                can_put = True
                pivot_available.append(pivot)
                pivot_temp = sorted(pivot)
                pivot_available_temp.append(pivot_temp)

        if pivot_available:
            while p < len(pivot_available_temp):
                vertex_3d.append(pivot_available_temp[p][0])
                p += 1

            p = 0
            while p < len(pivot_available_temp):
                if pivot_available_temp[p][0] == min(vertex_3d):
                    n += 1
                    vertex_2d.append(pivot_available_temp[p][1])

                p += 1

            if n == 1:
                p = 0
                while p < len(pivot_available_temp):
                    if pivot_available_temp[p][0] == min(pivot_available_temp[p]):
                        return pivot_available[p]

                    p += 1

            else:
                p = 0
                while p < len(pivot_available_temp):
                    if (
                        pivot_available_temp[p][0] == min(pivot_available_temp[p]) and
                        pivot_available_temp[p][1] == min(vertex_2d)
                    ):
                        m += 1
                        vertex_1d.append(pivot_available_temp[p][2])

                    p += 1

            if m == 1:
                p = 0
                while p < len(pivot_available_temp):
                    if (
                        pivot_available_temp[p][0] == min(pivot_available_temp[p]) and
                        pivot_available_temp[p][1] == min(vertex_2d)
                    ):
                        return pivot_available[p]

                    p += 1

            else:
                p = 0
                while p < len(pivot_available_temp):
                    if (
                        pivot_available_temp[p][0] == min(pivot_available_temp[p]) and
                        pivot_available_temp[p][1] == min(vertex_2d) and
                        pivot_available_temp[p][2] == min(vertex_1d)
                    ):
                        return pivot_available[p]

                    p += 1

        if not pivot_available:
            return can_put

    def pack2Bin(self, bin, item,fix_point,check_stable,support_surface_ratio):
        """
        Packs an item into a bin.

        Args:
            bin (Bin): The bin to pack the item into.
            item (Item): The item to be packed.
            fix_point (bool): Whether to fix the item's position at (0, 0, 0).
            check_stable (bool): Whether to check if the bin is stable after packing.
            support_surface_ratio (float): The ratio of the item's support surface to the bin's surface.

        Returns:
            None

        """

        fitted = False
        bin.fix_point = fix_point
        bin.check_stable = check_stable
        bin.support_surface_ratio = support_surface_ratio

        # first put item on (0,0,0) , if corner exist ,first add corner in box.
        if bin.corner != 0 and not bin.items:
            corner_lst = bin.addCorner()
            for i in range(len(corner_lst)) :
                bin.putCorner(i,corner_lst[i])

        elif not bin.items:
            response = bin.putItem(item, START_POSITION, [bin.width, bin.height, bin.depth])

            if not response:
                bin.unfitted_items.append(item)

            return

        else:
            pivot_point = self.choose_pivot_point(bin, item)
            pivot_dict = self.pivot_dict(bin, item)

            if not pivot_point:
                bin.unfitted_items.append(item)
                return

            distance_3D = pivot_dict[tuple(pivot_point)]
            response = bin.putItem(item, pivot_point, distance_3D)
            if not response:
                bin.unfitted_items.append(item)
            return

    def sortBinding(self,bin):
        ''' sorted by binding '''
        b,front,back = [],[],[]
        for i in range(len(self.binding)):
            b.append([])
            for item in self.items:
                if item.name in self.binding[i]:
                    b[i].append(item)
                elif item.name not in self.binding:
                    if len(b[0]) == 0 and item not in front:
                        front.append(item)
                    elif item not in back and item not in front:
                        back.append(item)

        min_c = min([len(i) for i in b])

        sort_bind =[]
        for i in range(min_c):
            for j in range(len(b)):
                sort_bind.append(b[j][i])

        for i in b:
            for j in i:
                if j not in sort_bind:
                    self.unfit_items.append(j)

        self.items = front + sort_bind + back
        return

    def putOrder(self):
        '''Arrange the order of items '''
        r = []
        for i in self.bins:
            # open top container
            if i.put_type == 2:
                i.items.sort(key=lambda item: item.position[0], reverse=False)
                i.items.sort(key=lambda item: item.position[1], reverse=False)
                i.items.sort(key=lambda item: item.position[2], reverse=False)
            # general container
            elif i.put_type == 1:
                i.items.sort(key=lambda item: item.position[1], reverse=False)
                i.items.sort(key=lambda item: item.position[2], reverse=False)
                i.items.sort(key=lambda item: item.position[0], reverse=False)
            else :
                pass
        return


    def gravityCenter(self,bin):
        '''
        Deviation Of Cargo gravity distribution
        '''
        w = int(bin.width)
        h = int(bin.height)
        d = int(bin.depth)

        area1 = [set(range(0,w//2+1)),set(range(0,h//2+1)),0]
        area2 = [set(range(w//2+1,w+1)),set(range(0,h//2+1)),0]
        area3 = [set(range(0,w//2+1)),set(range(h//2+1,h+1)),0]
        area4 = [set(range(w//2+1,w+1)),set(range(h//2+1,h+1)),0]
        area = [area1,area2,area3,area4]

        for i in bin.items:

            x_st = int(i.position[0])
            y_st = int(i.position[1])
            if i.rotation_type == 0:
                x_ed = int(i.position[0] + i.width)
                y_ed = int(i.position[1] + i.height)
            elif i.rotation_type == 1:
                x_ed = int(i.position[0] + i.height)
                y_ed = int(i.position[1] + i.width)
            elif i.rotation_type == 2:
                x_ed = int(i.position[0] + i.height)
                y_ed = int(i.position[1] + i.depth)
            elif i.rotation_type == 3:
                x_ed = int(i.position[0] + i.depth)
                y_ed = int(i.position[1] + i.height)
            elif i.rotation_type == 4:
                x_ed = int(i.position[0] + i.depth)
                y_ed = int(i.position[1] + i.width)
            elif i.rotation_type == 5:
                x_ed = int(i.position[0] + i.width)
                y_ed = int(i.position[1] + i.depth)

            x_set = set(range(x_st,int(x_ed)+1))
            y_set = set(range(y_st,y_ed+1))

            # cal gravity distribution
            for j in range(len(area)):
                if x_set.issubset(area[j][0]) and y_set.issubset(area[j][1]) :
                    area[j][2] += int(i.weight)
                    break
                # include x and !include y
                elif x_set.issubset(area[j][0]) == True and y_set.issubset(area[j][1]) == False and len(y_set & area[j][1]) != 0 :
                    y = len(y_set & area[j][1]) / (y_ed - y_st) * int(i.weight)
                    area[j][2] += y
                    if j >= 2 :
                        area[j-2][2] += (int(i.weight) - x)
                    else :
                        area[j+2][2] += (int(i.weight) - y)
                    break
                # include y and !include x
                elif x_set.issubset(area[j][0]) == False and y_set.issubset(area[j][1]) == True and len(x_set & area[j][0]) != 0 :
                    x = len(x_set & area[j][0]) / (x_ed - x_st) * int(i.weight)
                    area[j][2] += x
                    if j >= 2 :
                        area[j-2][2] += (int(i.weight) - x)
                    else :
                        area[j+2][2] += (int(i.weight) - x)
                    break
                # !include x and !include y
                elif x_set.issubset(area[j][0])== False and y_set.issubset(area[j][1]) == False and len(y_set & area[j][1]) != 0  and len(x_set & area[j][0]) != 0 :
                    all = (y_ed - y_st) * (x_ed - x_st)
                    y = len(y_set & area[0][1])
                    y_2 = y_ed - y_st - y
                    x = len(x_set & area[0][0])
                    x_2 = x_ed - x_st - x
                    area[0][2] += x * y / all * int(i.weight)
                    area[1][2] += x_2 * y / all * int(i.weight)
                    area[2][2] += x * y_2 / all * int(i.weight)
                    area[3][2] += x_2 * y_2 / all * int(i.weight)
                    break

        r = [area[0][2],area[1][2],area[2][2],area[3][2]]
        result = []
        for i in r :
            result.append(round(i / sum(r) * 100,2))
        return result


    def pivot_dict(self, bin, item):
        """For each item to be placed into a certain bin, obtain a corresponding comparison parameter of each optional pivot that the item can be placed.
        Args:
            bin: a bin in bin list that a certain item will be placed into.
            item: an unplaced item in item list.
        Returns:
            a pivot_dict contain all optional pivot point and their comparison parameter of the item.
            a empty dict may be returned if the item couldn't be placed into the bin.
        """

        pivot_dict = {}
        can_put = False

        for axis in range(0, 3):
            items_in_bin = bin.items
            items_in_bin_temp = items_in_bin[:]

            n = 0
            while n < len(items_in_bin):
                pivot = [0, 0, 0]

                if axis == Axis.WIDTH: # axis = 0/ x-axis
                    ib = items_in_bin[n]
                    pivot = [ib.position[0] + ib.getDimension()[0],
                            ib.position[1],
                            ib.position[2]]
                    try_put_item = bin.can_hold_item_with_rotation(item, pivot)

                    if try_put_item:
                        can_put = True
                        q = 0
                        q = 0
                        ib_neigh_x_axis = []
                        ib_neigh_y_axis = []
                        ib_neigh_z_axis = []
                        right_neighbor = False
                        front_neighbor = False
                        above_neighbor = False

                        while q < len(items_in_bin_temp):
                            if items_in_bin_temp[q] == items_in_bin[n]:
                                q += 1

                            else:
                                ib_neighbor = items_in_bin_temp[q]

                                if (
                                    ib_neighbor.position[0] > ib.position[0] + ib.getDimension()[0] and
                                    ib_neighbor.position[1] + ib_neighbor.getDimension()[1] > ib.position[1] and
                                    ib_neighbor.position[2] + ib_neighbor.getDimension()[2] > ib.position[2]
                                ):
                                    right_neighbor = True
                                    x_distance = ib_neighbor.position[0] - (ib.position[0] + ib.getDimension()[0])
                                    ib_neigh_x_axis.append(x_distance)

                                elif (
                                    ib_neighbor.position[1] >= ib.position[1] + ib.getDimension()[1] and
                                    ib_neighbor.position[0] + ib_neighbor.getDimension()[0] > ib.position[0] + ib.getDimension()[0] and
                                    ib_neighbor.position[2] + ib_neighbor.getDimension()[2] > ib.position[2]
                                ):
                                    front_neighbor = True
                                    y_distance = ib_neighbor.position[1] - ib.position[1]
                                    ib_neigh_y_axis.append(y_distance)

                                elif (
                                    ib_neighbor.position[2] >= ib.position[2] + ib.getDimension()[2] and
                                    ib_neighbor.position[0] + ib_neighbor.getDimension()[0] > ib.position[0] + ib.getDimension()[0] and
                                    ib_neighbor.position[1] + ib_neighbor.getDimension()[1] > ib.position[1]
                                ):
                                    above_neighbor = True
                                    z_distance = ib_neighbor.position[2] - ib.position[2]
                                    ib_neigh_z_axis.append(z_distance)

                                q += 1

                        if not right_neighbor:
                            x_distance = bin.width - (ib.position[0] + ib.getDimension()[0])
                            ib_neigh_x_axis.append(x_distance)

                        if not front_neighbor:
                            y_distance = bin.height - ib.position[1]
                            ib_neigh_y_axis.append(y_distance)

                        if not above_neighbor:
                            z_distance = bin.depth - ib.position[2]
                            ib_neigh_z_axis.append(z_distance)

                        distance_3D = [min(ib_neigh_x_axis), min(ib_neigh_y_axis), min(ib_neigh_z_axis)]
                        pivot_dict[tuple(pivot)] = distance_3D

                elif axis == Axis.HEIGHT: # axis = 1/ y-axis
                    ib = items_in_bin[n]
                    pivot = [ib.position[0],
                            ib.position[1] + ib.getDimension()[1],
                            ib.position[2]]
                    try_put_item = bin.can_hold_item_with_rotation(item, pivot)

                    if try_put_item:
                        can_put = True
                        q = 0
                        ib_neigh_x_axis = []
                        ib_neigh_y_axis = []
                        ib_neigh_z_axis = []
                        right_neighbor = False
                        front_neighbor = False
                        above_neighbor = False

                        while q < len(items_in_bin_temp):
                            if items_in_bin_temp[q] == items_in_bin[n]:
                                q += 1

                            else:
                                ib_neighbor = items_in_bin_temp[q]

                                if (
                                    ib_neighbor.position[0] >= ib.position[0] + ib.getDimension()[0] and
                                    ib_neighbor.position[1] + ib_neighbor.getDimension()[1] > ib.position[1] + ib.getDimension()[1] and
                                    ib_neighbor.position[2] + ib_neighbor.getDimension()[2] > ib.position[2]
                                ):
                                    right_neighbor = True
                                    x_distance = ib_neighbor.position[0] - ib.position[0]
                                    ib_neigh_x_axis.append(x_distance)

                                elif (
                                    ib_neighbor.position[1] > ib.position[1] + ib.getDimension()[1] and
                                    ib_neighbor.position[0] + ib_neighbor.getDimension()[0] > ib.position[0] and
                                    ib_neighbor.position[2] + ib_neighbor.getDimension()[2] > ib.position[2]
                                ):
                                    front_neighbor = True
                                    y_distance = ib_neighbor.position[1] - (ib.position[1] + ib.getDimension()[1])
                                    ib_neigh_y_axis.append(y_distance)

                                elif (
                                    ib_neighbor.position[2] >= ib.position[2] + ib.getDimension()[2] and
                                    ib_neighbor.position[0] + ib_neighbor.getDimension()[0] > ib.position[0] and
                                    ib_neighbor.position[1] + ib_neighbor.getDimension()[1] > ib.position[1] + ib.getDimension()[1]
                                ):
                                    above_neighbor = True
                                    z_distance = ib_neighbor.position[2] - ib.position[2]
                                    ib_neigh_z_axis.append(z_distance)

                                q += 1

                        if not right_neighbor:
                            x_distance = bin.width - ib.position[0]
                            ib_neigh_x_axis.append(x_distance)

                        if not front_neighbor:
                            y_distance = bin.height - (ib.position[1] + ib.getDimension()[1])
                            ib_neigh_y_axis.append(y_distance)

                        if not above_neighbor:
                            z_distance = bin.depth - ib.position[2]
                            ib_neigh_z_axis.append(z_distance)

                        distance_3D = [min(ib_neigh_x_axis), min(ib_neigh_y_axis), min(ib_neigh_z_axis)]
                        pivot_dict[tuple(pivot)] = distance_3D

                elif axis == Axis.DEPTH: # axis = 2/ z-axis
                    ib = items_in_bin[n]
                    pivot = [ib.position[0],
                            ib.position[1],
                            ib.position[2] + ib.getDimension()[2]]
                    try_put_item = bin.can_hold_item_with_rotation(item, pivot)

                    if try_put_item:
                        can_put = True
                        q = 0
                        ib_neigh_x_axis = []
                        ib_neigh_y_axis = []
                        ib_neigh_z_axis = []
                        right_neighbor = False
                        front_neighbor = False
                        above_neighbor = False

                        while q < len(items_in_bin_temp):
                            if items_in_bin_temp[q] == items_in_bin[n]:
                                q += 1

                            else:
                                ib_neighbor = items_in_bin_temp[q]

                                if (
                                    ib_neighbor.position[0] >= ib.position[0] + ib.getDimension()[0] and
                                    ib_neighbor.position[1] + ib_neighbor.getDimension()[1] > ib.position[1] and
                                    ib_neighbor.position[2] + ib_neighbor.getDimension()[2] > ib.position[2] + ib.getDimension()[2]
                                ):
                                    right_neighbor = True
                                    x_distance = ib_neighbor.position[0] - ib.position[0]
                                    ib_neigh_x_axis.append(x_distance)

                                elif (
                                    ib_neighbor.position[1] > ib.position[1] + ib.getDimension()[1] and
                                    ib_neighbor.position[0] + ib_neighbor.getDimension()[0] > ib.position[0] and
                                    ib_neighbor.position[2] + ib_neighbor.getDimension()[2] > ib.position[2] + ib.getDimension()[2]
                                ):
                                    front_neighbor = True
                                    y_distance = ib_neighbor.position[1] - (ib.position[1] + ib.getDimension()[1])
                                    ib_neigh_y_axis.append(y_distance)

                                elif (
                                    ib_neighbor.position[2] >= ib.position[2] + ib.getDimension()[2] and
                                    ib_neighbor.position[1] + ib_neighbor.getDimension()[1] > ib.position[1] and
                                    ib_neighbor.position[0] + ib_neighbor.getDimension()[0] > ib.position[0]
                                ):
                                    above_neighbor = True
                                    z_distance = ib_neighbor.position[2] - ib.position[2]
                                    ib_neigh_z_axis.append(z_distance)

                                q += 1

                        if not right_neighbor:
                            x_distance = bin.width - ib.position[0]
                            ib_neigh_x_axis.append(x_distance)

                        if not front_neighbor:
                            y_distance = bin.height - ib.position[1]
                            ib_neigh_y_axis.append(y_distance)

                        if not above_neighbor:
                            z_distance = bin.depth - (ib.position[2] + ib.getDimension()[2])
                            ib_neigh_z_axis.append(z_distance)

                        distance_3D = [min(ib_neigh_x_axis), min(ib_neigh_y_axis), min(ib_neigh_z_axis)]
                        pivot_dict[tuple(pivot)] = distance_3D

                n += 1

        return pivot_dict


    def pack(self, bigger_first=False,distribute_items=True,fix_point=True,check_stable=True,support_surface_ratio=0.75,binding=[],number_of_decimals=DEFAULT_NUMBER_OF_DECIMALS):
        '''pack master func '''
        # set decimals
        for bin in self.bins:
            bin.formatNumbers(number_of_decimals)

        for item in self.items:
            item.formatNumbers(number_of_decimals)
        # add binding attribute
        self.binding = binding
        # Bin : sorted by volumn
        self.bins.sort(key=lambda bin: bin.getVolume(), reverse=bigger_first)
        # Item : sorted by volumn -> sorted by loadbear -> sorted by level -> binding
        self.items.sort(key=lambda item: item.getVolume(), reverse=bigger_first)
        # self.items.sort(key=lambda item: item.getMaxArea(), reverse=bigger_first)
        self.items.sort(key=lambda item: item.loadbear, reverse=True)
        self.items.sort(key=lambda item: item.level, reverse=False)
        # sorted by binding
        if binding != []:
            self.sortBinding(bin)

        for idx,bin in enumerate(self.bins):
            # pack item to bin
            for item in self.items:
                self.pack2Bin(bin, item, fix_point, check_stable, support_surface_ratio)

            if binding != []:
                # resorted
                self.items.sort(key=lambda item: item.getVolume(), reverse=bigger_first)
                self.items.sort(key=lambda item: item.loadbear, reverse=True)
                self.items.sort(key=lambda item: item.level, reverse=False)
                # clear bin
                bin.items = []
                bin.unfitted_items = self.unfit_items
                bin.fit_items = np.array([[0,bin.width,0,bin.height,0,0]])
                # repacking
                for item in self.items:
                    self.pack2Bin(bin, item,fix_point,check_stable,support_surface_ratio)
            
            # Deviation Of Cargo Gravity Center 
            self.bins[idx].gravity = self.gravityCenter(bin)

            if distribute_items :
                for bitem in bin.items:
                    no = bitem.partno
                    for item in self.items :
                        if item.partno == no :
                            self.items.remove(item)
                            break

        # put order of items
        self.putOrder()

        if self.items != []:
            self.unfit_items = copy.deepcopy(self.items)
            self.items = []
        # for item in self.items.copy():
        #     if item in bin.unfitted_items:
        #         self.items.remove(item)

