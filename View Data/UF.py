import numpy.ma as ma
class UF:
    def __init__(self,radar,shape_grid,lat_0, lon_0):
        self.radar = radar
        self.shape = shape_grid
        self.lat_0 = lat_0
        self.lon_0 = lon_0
    def noise_rejection(self):
        mask_noises_CC=ma.masked_less(self.radar.fields['cross_correlation_ratio']['data'],0.85)
        mask_noises_Z=ma.masked_less(self.radar.fields['reflectivity']['data'],0)
        rm_noises_Z_=np.ma.masked_array(self.radar.fields['reflectivity']['data'],mask_noises_CC.mask)
        rm_noises_Z=np.ma.masked_array(rm_noises_Z_,mask_noises_Z.mask)
        self.radar.add_field_like('reflectivity','Z_removed_noises',rm_noises_Z,replace_existing=True)
    def convert_grid(self):
        grid = pyart.map.grid_from_radars(
            self.radar,
            grid_shape=self.shape, #Number of points in the grid (z, y, x)
            grid_limits=((0, 15000), (-300000, 300000), (-300000, 300000)), # min-max tuong duong z,y,x
            grid_origin = (self.lat_0, self.lon_0),
            fields=['Z_removed_noises'],
            roi_func='dist_beam',
            weighting_function='cressman')
        return grid
    def convert_lat_lon(self, grid):
        #conver distance to lat/lon
        for i in range(self.shape[1]):
            geog = pyart.core.cartesian_to_geographic_aeqd(grid.x["data"][i],grid.y["data"][i],self.lon_0, self.lat_0, R=6370997.0)
            grid.x["data"][i] = geog[0]
            grid.y["data"][i] = geog[1]
        return grid
    def plot_MAX_product(self,lons,lats,Zh_max,linkOUT):
        #plot map with datas
        fig=plt.figure(figsize=(10,7),dpi=80)
        ax1=fig.add_subplot(1,1,1, projection=ccrs.PlateCarree())
        ax1.add_feature(cfeat.OCEAN.with_scale('10m'))
        ax1.add_feature(cfeat.BORDERS.with_scale('10m'),lw=0.5)
        ax1.add_feature(states_geom, facecolor="none", edgecolor="k",lw=0.5)
        ax1.set_extent((grid.x['data'][0],grid.x['data'][-1],grid.y['data'][0],grid.y['data'][-1]),crs=ccrs.PlateCarree())
        z1_plot=ax1.pcolormesh(lons,lats,Zh_max,cmap=cmap,norm=norm)
        ax1.scatter(x=103.51694002747536,y=21.571390070021152,color="black",s=10, alpha=1,marker='P')
        ax1.set(title="MAX(Z) Product "+"\n"+ radar.time['units'][25:30]+" UTC "+radar.time['units'][14:24])
        ax1.title.set_size(20)
        plt.colorbar(z1_plot,ax=ax1,ticks=ticks,extend='both',label="dBZ")    
        linkPIC=linkOUT+radar.time['units'][14:-10]+radar.time['units'][-10:-7]+'-'+radar.time['units'][-6:-4]
        plt.savefig(linkPIC)