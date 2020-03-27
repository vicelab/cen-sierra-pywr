import os
import pandas as pd


def sjrrp_below_friant(scenario_path):
    thresholds_taf = [0, 400, 670, 930, 1450, 2500]
    allocations_taf = [116.866, 187.785, 272.280, 330.300, 400.300, 547.400, 673.488]

    inpath = os.path.join(scenario_path, 'preprocessed', 'full_natural_flow_annual_mcm.csv')

    df = pd.read_csv(inpath, index_col=0, header=0)

    wyts = []
    allocations_mcm = []
    allocation_fractions = []
    for i, runoff_mcm in enumerate(df['flow']):
        runoff_taf = runoff_mcm / 1.2335
        wyt = sum([1 for t in thresholds_taf if runoff_taf > t])
        wyts.append(wyt)

        idx = wyt-1
        if wyt in [1, 2, 6]:
            if wyt == 1:
                allocation_taf = allocations_taf[0]
            elif wyt == 2:
                allocation_taf = allocations_taf[1]
            else:
                allocation_taf = allocations_taf[-1]
            allocation_fraction = 1
        else:
            tlow = thresholds_taf[idx]
            thigh = thresholds_taf[idx+1]
            rlow = allocations_taf[idx]
            rhigh = allocations_taf[idx+1]
            slope = (rhigh-rlow)/(thigh-tlow)
            allocation_taf = rlow + slope * (runoff_taf - tlow)
            allocation_taf_middle = (rhigh + rlow) / 2
            allocation_fraction = allocation_taf / allocation_taf_middle

        allocation_mcm = allocation_taf * 1.2335
        allocations_mcm.append(allocation_mcm)
        allocation_fractions.append(allocation_fraction)

    df2 = pd.DataFrame(index=df.index)
    df2['WYT'] = wyts
    df2['Annual allocation mcm'] = allocations_mcm
    df2['Allocation adjustment'] = allocation_fractions

    outpath = os.path.join(scenario_path, 'preprocessed', 'SJ restoration flows.csv')
    df2.to_csv(outpath)
