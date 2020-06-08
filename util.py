
import numpy as np
import pandas as pd


from settings import *

# class de fonctions utilitaires
class Util:

    # cree une matrice complexe (generalise linspace)
    def arrayspace(a,b,size_x,size_y):
        return np.linspace(0,size_x-1,size_x)-a+1j*(np.linspace(0,size_y-1,size_y).reshape(-1,1)-b)

    def mypos(x):
        return max(x,0)
    mypos = np.frompyfunc(mypos, 1, 1)

    #permet de filtrer par secteur sur une matrice
    def mysector(x,angle,delta):
        return angle/4<np.angle(x)<angle+delta
    mysector = np.frompyfunc(mysector, 3, 1)

    #permet de filtrer par couronnes sur une matrice
    def mycrown(x,ro,delta):
      return ro<np.abs(x)<ro+deta
    mycrown = np.frompyfunc(mycrown, 3, 1)

    #cumule les élements d'une liste
    def cumulative(list):
        cu_list = [sum(list[0:x:1]) for x in range(0, len(list)+1)]
        return cu_list[1:]

    #retourne les index d'un tableau dont le cumul depasse le seuil bas puis le seuil haut
    def get_interval(arr,low,high):
        C,inf,sup = 0,len(arr)-1,len(arr)-1
        for i,x in enumerate(a):
            C+=x
            if inf==-1 :
              if C>low :
                inf=i
                if C>high:
                  sup=i
                  break
            elif C>high :
              sup=i
              break
        return inf, sup

    #decale la matrice vers le haut ou le bas
    def shift(arr, row, col, fill_value=0):
        result = res = np.empty_like(arr)
        if row > 0:
            res[:row,:] = fill_value
            res[row:,:] = arr[:-row,:]
        elif row < 0:
            res[row:,:] = fill_value
            res[:row,:] = arr[-row:,:]
        else : res[:]=arr[:]
        if col > 0:
            result[:,col:] = res[:,:-col]
            result[:,:col] = fill_value
        elif col < 0:
            result[:,:col] = res[:,-col:]
            result[:,col:] = fill_value
        else : result[:]=res[:]
        return result

    # prend une matrice avec des valeurs en fonction de x et y,coordonnees dans la grille
    # et retourne un tableau (DF) qui donne la valeur en fonction de lat et lon en enlevant les cas nuls
    def grid_to_latlon(grid):
        if np.sum(grid)!=0:
            columns=(['lat','lon','value'])
            coord=np.where(grid!=0)
            return pd.DataFrame(
                np.append(
                    Util.m_to_latlon(SCALE*coord[1],SCALE*coord[0]), #Y c'est les lignes, et X les colonnes
                    [grid[grid!=0]],
                    axis=0
                    ).T,
                columns=columns)


    #détermine de combien on sort des clous : 0 si on reste dedans
    def real_outofbound(x,min,max):
        return -np.maximum(min-x,0)+np.maximum(x-max,0)

    #détermine de combien on sort sur l'axe des x et des y (en complexe)
    def complex_outofbound(z,min,max):
        return Util.real_outofbound(np.real(z),min,max)+1j*Util.real_outofbound(np.imag(z),min,max)

    def z_to_latlon(z):
        return Util.m_to_latlon(np.real(z),np.imag(z))

    def m_to_latlon(x,y):
        lat=y*360/(40075*1000)+ZERO_Y
        lon=x*360/(40075*1000*np.cos(np.pi/180*lat))+ZERO_X
        return lat,lon

    def latlon_to_m(lat,lon):
        y=(lat-ZERO_Y)*40075*1000/360
        x=(lon-ZERO_X)*40075*1000*np.cos(np.pi*lat/180)/360
        return x,y
