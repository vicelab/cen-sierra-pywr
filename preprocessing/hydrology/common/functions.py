import os
import shutil
import pandas as pd

def extract_precipitation_at(src, dst, lat, lon, start, end):
    # source dir

    dstdir = os.path.split(dst)[0]
    if not os.path.exists(dstdir):
        os.makedirs(dstdir)

    srcpath = dst
    src_df = pd.read_csv(srcpath, header=0)
    dst_df = src_df[['dates', 'obs']].set_index('dates')
    dst_df.columns = ['precip (mm)']
    dst_df.to_csv(dst.replace('mcm', 'mm').replace('rainfall', 'precipitation'))

    # firstfile = os.path.join(src, "rainfall.2006.v0.CA_NV.nc")


    # get values at location lonlat
    # obsoutput < - ncvar_get(obsdata, varid='rainfall',
    #                         start=c(which.min(abs(obsdata$dim$Lon$vals - lon)),  # look for closest long
    # which.min(abs(obsdata$dim$Lat$vals - lat)),  # look for closest lat
    # 1),
    # count = c(1, 1, -1))  # count '-1' means 'all values along that dimension'that dimension'
    # # create dataframe
    # datafinal < - data.frame(dates=obsdatadates, obs=obsoutput)
    #
    # # get dates
    # # obsdatadates <- as.Date(obsdata$dim$Time$vals, origin = '1950-01-01')
    # date.start < - start
    # date.end < - end
    # d < - seq(as.Date(date.start), as.Date(date.end), 1)
    # datafinal$dates < - d
    # datafinal$month < - month(d)
    # datafinal$year < - year(d)
    # datafinal$day < - day(d)
    # datafinal$WY < - datafinal$year + (datafinal$month % in % 10:12)  # this method is called vectorization
    #
    # write.csv(datafinal, outpath)
