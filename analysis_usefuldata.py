import pandas as pd
from datetime import datetime

# ----------------------------------------------------------------------------------------------------------
# -- #Datapoints/Day ---------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------
'''Adding #datapoints to files with total water usage/day (TF)'''

for i in range(10,27):
    df_cf = pd.read_csv('D:\OneDrive - Habib University\HU\KWP\\Data\DataDaily\ALLCF_Daily'+str(i)+'.csv') #1-26
    df_tf = pd.read_csv('D:\OneDrive - Habib University\HU\KWP\\Data\DataDaily\ALLTF_Daily '+str(i+1)+' .csv') #2-27
    dates = df_cf['Date'].unique()
    dtpts = []
    for date in dates: #for each date of the node
        df_date = df_cf[df_cf["Date"] == date]
        no_dtpts = len(df_date)
        dtpts.append(no_dtpts)
    df_tf['#Datapoints'] = dtpts
    df_tf.to_csv('D:\OneDrive - Habib University\HU\KWP\\Data\DataDaily\ALLTF\ALLTF_Daily'+str(i)+'.csv')

# ----------------------------------------------------------------------------------------------------------
# -- #Days of Data -----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------

'''No. of days in raw data.'''
days = pd.DataFrame(columns=['NodeID','Raw'])
for i in range(1,27):
    row = []
    df = pd.read_csv('Data\ALLSENSORDATA\\N'+str(i)+'.csv') #1-26
    time_sampled = list(df['time_sampled'])
    datetime_obj = []
    for j in time_sampled:
        datetime_obj.append(str(datetime.fromtimestamp(int(j)))) #converts each timestamp to datetime format using computer's local timezone ie KHI
    df['datetime'] = datetime_obj
    df['date'] = df.datetime.str[0:10]
    dates = len(df['date'].unique())
    row.append('N'+str(i))
    row.append(dates)
    days.loc[len(days)] = row
days.to_csv('Data\No.DaysinDataset.csv')

'''Appending #days for filtered dataset to existing file'''
no_days = []
for i in range(1,27):
    df = pd.read_csv('Data\Preprocessed\OldSensorData\\with dvol\\N'+str(i)+'_cleaned.csv')
    df['Date'] = df.datetime.str[0:10]
    no_days.append(len(df['Date'].unique()))
days = pd.read_csv('D:\OneDrive - Habib University\HU\KWP\\Data\\No.DaysinDataset.csv')
days['filtered-with0s'] = no_days
days.to_csv('D:\OneDrive - Habib University\HU\KWP\\Data\\No.DaysinDataset.csv')

# ----------------------------------------------------------------------------------------------------------
# -- Quantiles for Filtering Data --------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------

'''Freq distribution of total daily volume/datapoints for each node.'''
vol_quantiles = pd.DataFrame(columns=['NodeID','5th','10th','50th','90th','95th'])
for i in range(1,27):
    row = []
    df = pd.read_csv('Data\Preprocessed\TF_N'+str(i)+'.csv') #1-26
    row = ['N'+str(i), df.TotalVol.quantile(0.05),df.TotalVol.quantile(0.1),df.TotalVol.quantile(0.5),df.TotalVol.quantile(0.9),df.TotalVol.quantile(0.95)]
    vol_quantiles.loc[len(vol_quantiles)] = row
    # fig = px.histogram(df, x="no_dtpts", nbins=50,title='N'+str(i))
    # # fig.show()
    # pio.write_image(fig, 'Figures\DP-Quant\DailyDP-N'+str(i)+'.png')
vol_quantiles.to_csv('Data\\VolQuantiles.csv')

# ----------------------------------------------------------------------------------------------------------
# -- Filtering Days ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------

'''Filtering days with missing/incomplete/garbage data.'''
def five_mins_missing(df):
    '''Takes dataframe for one day as input. Returns True if more than 5mins of consecutive data is missing in dataframe.'''
    df['datetime'] = df['datetime'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
    ser_diff = df['datetime'].diff()
    ser_diff = ser_diff.dt.total_seconds().div(60, fill_value=0)
    if ser_diff.max() > 5: #if max time difference in datapoints in > 5 minutes
        return True
    return False

for i in range(1,27): # for each node 
    print('Node',i)
    df = pd.read_csv('Data\Preprocessed\OldSensorData\with dvol\\N'+str(i)+'_cleaned.csv') #1-26
    df_tf = pd.read_csv('Data\Preprocessed\OldSensorData\TF_N'+str(i)+'.csv') #1-26
    MIN_DTPTS = 2870 #df_tf.No_dp.quantile(0.10) 
    MIN_DVOL = 200 if df_tf.TotalVol.quantile(0.1) < 20 else df_tf.TotalVol.quantile(0.1) #10th percentile or 200 (if low perc.)
    df['Date'] = df.datetime.str[:10]
    dates = df['Date'].unique()
    for date in dates: #for each date of the node
        df_date = df[df["Date"] == date]
        if len(df_date) < MIN_DTPTS or five_mins_missing(df_date) or list(df_date['DVol'])[-1] < MIN_DVOL: 
            df = df[df["Date"] != date] #remove datapoints from this date from dataset
    df.to_csv('Data\Preprocessed\OldSensorData\\filtered-2870dp\\filtered'+str(i)+'.csv')
