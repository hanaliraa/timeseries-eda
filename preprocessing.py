import pandas as pd
import helper_functions

max_node_capacity = list(pd.read_csv('\InstalledNodes.csv')['MaxFlow'])

for i in range(1,10): # looping through all data files to remove garbage data and add useful columns
    df = pd.read_csv('Data\ALLSENSORDATA\\N0'+str(i)+'.csv') # nodes 1 - 9
    # df = pd.read_csv('Data\ALLSENSORDATA\\N'+str(i)+'.csv') # nodes 10 - 26
    df = df[['time_sampled','flow_rate','total_flow']]
    print('Node:',i)
    og_len = len(df)
    print('# datapoints in raw data:',og_len)
    df = helper_functions.unix_to_datetime_local(df)
    df = helper_functions.rem_nonzero_start(df)
    print('# datapoints removed - non-zero start:',len(df))
    df = helper_functions.vol_in_interval(df)
    df = helper_functions.abs_vol(df)
    df = helper_functions.clean_flowrate(df,max_node_capacity[i-1])
    print('# datapoints removed - flow_rate:',len(df))
    df = helper_functions.add_days(df)
    # df = helper_functions.get_cum_vol(df)
    print('# datapoints remaining:', len(df))
    print('# datapoints removed (total):',(og_len - len(df)))
    # df = get_daily_cum_vol(df)
    df = df.drop(columns=['total_flow'])
    df = df.iloc[::-1] #reversing data order so that most recent datapoint is at the last index
    df.insert(0,'NodeID','N'+str(i))
    df.to_csv('Preprocessed/N'+str(i)+'_cleaned.csv')

'''Adding DVol to preprocessed data'''
for i in range(10,27):
    df = pd.read_csv('Data\Preprocessed\\N'+str(i)+'_cleaned.csv')
    df['date'] = df.datetime.str[:10]
    df = helper_functions.get_daily_cum_vol(df)
    df = df.drop(columns=['Unnamed: 0','date'])
    df.to_csv('Data\Preprocessed\with dvol\\N'+str(i)+'_cleaned.csv')


'''Generating TF Files for storing only total water usage of each day.
Reads data for each node one by one and exports new files to specified location.'''
for i in range(1,27):
    df_tf = pd.DataFrame(columns=['NodeID','Date','TotalVol','No_dp'])
    df = pd.read_csv('Data\Preprocessed\with dvol\\N'+str(i)+'_cleaned.csv')
    df['Date'] = df.datetime.str[:10]
    temp = df.groupby('Date').max()
    df_tf['NodeID'] = temp['NodeID']
    df_tf['TotalVol'] = temp['DVol']
    df_tf['Date'] = temp.index
    df_tf['No_dp'] = df.groupby('Date').size()
    df_tf.to_csv('Data\Preprocessed\\TF_N'+str(i)+'.csv')