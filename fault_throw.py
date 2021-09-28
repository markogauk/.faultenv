import get_polygon
import SWconnect
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

def fault_throw_viz(proj,cult_name,grid_name,folder_name):
    # Replace null grid values with NaN
    
    cult = get_polygon.getLayer(proj,cult_name)
    grid = SWconnect.get_grid(proj,grid_name)

    bin_size = 50

    grid[grid > 100000000] = np.NaN

    layers = get_polygon.get_polyobjects(cult)

    faultDFlist = []
    count = 0

    for layer in layers:

        count += 1 

        faultDF = get_polygon.get_strikes(layer,count)

        faultDFlist.append(faultDF)


    faultDF = pd.concat(faultDFlist).dropna()
    grid.dropna(inplace=True)
    print(faultDF)


    # NOTE set a max distance for interpolation

    faultDF["Z1x"] = griddata((grid.X,grid.Y),grid.X,(faultDF.X1,faultDF.Y1),method="nearest")
    faultDF["Z1y"] = griddata((grid.X,grid.Y),grid.Y,(faultDF.X1,faultDF.Y1),method="nearest")

    faultDF["Z2x"] = griddata((grid.X,grid.Y),grid.X,(faultDF.X2,faultDF.Y2),method="nearest")
    faultDF["Z2y"] = griddata((grid.X,grid.Y),grid.Y,(faultDF.X2,faultDF.Y2),method="nearest")

    faultDF["Z1"] = griddata((grid.X,grid.Y),grid.Z,(faultDF.X1,faultDF.Y1),method="nearest")
    faultDF["Z2"] = griddata((grid.X,grid.Y),grid.Z,(faultDF.X2,faultDF.Y2),method="nearest")

    # Calculate the difference between the point on polygon and the nearest grid data value
    faultDF["Interp_distance1"] = ((faultDF.Z1x-faultDF.X1)**2+(faultDF.Z1y-faultDF.Y1)**2)**(0.5)

    faultDF["Interp_distance2"] = ((faultDF.Z2x-faultDF.X2)**2+(faultDF.Z2y-faultDF.Y2)**2)**(0.5)

    faultDF["Zdiff"] = faultDF.Z1-faultDF.Z2

    fig,ax = plt.subplots(figsize=(5,5))
    


    for i in faultDF.Object.unique():
        plotDF = faultDF.loc[faultDF['Object'] == i]

        get_polygon.build_plots(plotDF,bin_size,i,folder_name)

        ax.plot(plotDF.X1,plotDF.Y1,color = (1-i / len(faultDF.Object.unique()), i / len(faultDF.Object.unique()), 0, 1))
    
        ax.plot(plotDF.X2,plotDF.Y2,color = (1-i / len(faultDF.Object.unique()), i / len(faultDF.Object.unique()), 0, 1))

        ax.text(plotDF.X1.median(),plotDF.Y1.median(),f"#{i}")

    fig.savefig(f"{folder_name}/Map.png")

    faultDF.reset_index().to_csv(f"{folder_name}/result.csv")

