import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import iplot
import plotly.io as pio

hh_members = list(pd.read_excel('Data\HH_Occupancy.xlsx')['Members'])

# ----------------------------------------------------------------------------------------------------------
# -- Peak Water Usage --------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------

peak = pd.DataFrame(columns=['NodeID','total_days','peak_days','total_vol','peak_vol','occupants'])
for i in range(1,27):
    df = pd.read_csv('Data\DailyUsage\ALLTF_Daily'+str(i)+'.csv') #1-26
    # Filtering out days with peak water usage i.e. in top 10%
    df_peak = df[df['TotalVol'] > df.TotalVol.quantile(0.90)] 
    no_hh_mem = hh_members[i-1]
    row = ['N'+str(i),len(df),len(df_peak),df['TotalVol'].sum(),df_peak['TotalVol'].sum(),no_hh_mem]
    peak.loc[len(peak)]= row
peak.to_csv('Data\PeakWU.csv') #1-26

# ----------------------------------------------------------------------------------------------------------
# -- Water Usage at different times of the day (Morning, Afternoon, Evening) -------------------------------
# ----------------------------------------------------------------------------------------------------------

period_day = pd.DataFrame(columns=['NodeID','mornings_tot(%)','afternoons_tot(%)','evenings_tot(%)'])
nodes = []
morns = []
noons = []
eve = []

for i in range(1,27):
    # Read relevant files
    df = pd.read_csv('Data\DailyUsage\ALLCF_Daily'+str(i)+'.csv') # data with DVol columne
    df_tf = pd.read_csv('Data\DailyUsage\ALLTF_Daily'+str(i)+'.csv') # data with only total daily water usage

    # Group data based on different times of the day (hours)
    df['Hour'] = df.Time.str[:2]
    df_morn = df[df['Hour'].isin(['04','05','06','07','08','09','10','11'])].groupby('Date').max()
    df_eve = df[df['Hour'].isin(['17','18','19','20','21','22','23'])].groupby('Date').max()
    df_aftnoon = df[df['Hour'].isin(['12','13','14','15','16'])].groupby('Date').max()

    # Subtracting volume of previous period of day, as dvol is cumulative daily volume
    df_eve['DVol'] = df_eve['DVol'] - df_aftnoon['DVol']
    df_aftnoon['DVol'] = df_aftnoon['DVol'] - df_morn['DVol']

    # Total volume used by node in period of day as % of total vol used by node
    morns.append(df_morn['DVol'].sum()/df_tf['TotalVol'].sum()*100) 
    noons.append(df_aftnoon['DVol'].sum()/df_tf['TotalVol'].sum()*100)
    eve.append(df_eve['DVol'].sum()/df_tf['TotalVol'].sum()*100)
    
    # # Plotting figures for each node's usage during each period of day
    # fig = px.line(df_aftnoon,x=df_aftnoon.index,y='DVol',title='N'+str(i)+' - Afternoons')
    # pio.write_image(fig, 'Figures\Afternoons\\afternoons-N'+str(i)+'.png')
    # fig = px.line(df_eve,x=df_eve.index,y='DVol',title='N'+str(i)+' - Evenings')
    # pio.write_image(fig, 'Figures\Evenings\\evenings-N'+str(i)+'.png')

    # # Plotting all time periods of each node on same figure
    # fig = go.Figure()
    # fig = fig.add_trace(go.Scatter(x = df_morn.index, y = df_morn["DVol"], name = 'Mornings'))
    # fig = fig.add_trace(go.Scatter(x = df_aftnoon.index, y = df_aftnoon["DVol"], name = 'Afternoons'))
    # fig = fig.add_trace(go.Scatter(x = df_eve.index, y = df_eve["DVol"], name = 'Evenings'))
    # fig.update_layout(title='N'+str(i)+' - '+str(hh_members[i-1])+' Occupants (Weekends)')
    # pio.write_image(fig, 'Figures\\timesofday\\periods-N'+str(i)+'.png')

period_day['mornings_tot(%)'] = morns
period_day['afternoons_tot(%)'] = noons
period_day['evenings_tot(%)'] = eve
period_day.to_csv('Data\PeriodsWU.csv')

# ----------------------------------------------------------------------------------------------------------
# -- Moving Average ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------

fig = go.Figure()
for i in range(1,27):
    df = pd.read_csv('Data\DataDaily\ALLTF_Daily '+str(i)+' .csv') # data with only total daily water usage (ie each row is a unique day)
    # df['date'] = df.datetime.str[:10]
    df['mov_avg'] = df['TotalVol'].rolling(window=30).mean()
    fig = fig.add_trace(go.Scatter(x = df['Date'], y = df["mov_avg"], name = 'N'+str(i-1)))
fig.update_layout(title='Monthly Moving Average')
fig.show()

# ----------------------------------------------------------------------------------------------------------
# -- Sleeping Patterns -------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------

def get_time_wake(df,threshold=5,ref_win=60):
    '''Returns index of df to indicate when household woke up. Ref window is 30 mins long.'''
    timewake_index = 0
    # Stable region ending ie waking up
    for i in range(1, len(df)):
        increasing = []
        diff = abs(df['DVol'][i] - df['DVol'][i-1])
        # if diff > threshold:
        if diff > 0: # water is being used
            timewake_index = i # people may be waking up now
            if (i + ref_win) < (len(df)-1): # see if people are using water in the succeeding time interval
                window = i + ref_win
            else:
                window = len(df)-1
            for j in range(i,window): # is water being used in next 30 mins
                # if abs(df['DVol'][j] - df['DVol'][j+1]) > threshold:
                if abs(df['DVol'][j] - df['DVol'][j+1]) > 0: # is water being used
                    increasing.append(j)
            if len(increasing) < (0.5*window): # if water is not being used > 30% of the window, people aren't awake yet
                timewake_index = 0 # resetting
            else:
                break
    return timewake_index

def get_time_sleep(df,threshold=5,ref_win=30):
    '''Returns index of df to indicate when household sleeps. Ref window is defaulted at 30 mins long.'''
    # Stable start ie going to sleep
    timesleep_index = len(df)-1
    for i in range(1, len(df)):
        sleeping = []
        # if abs(df['DVol'][i] - df['DVol'][i-1]) < threshold:
        if abs(df['DVol'][i] - df['DVol'][i-1]) == 0: # water is not being used
            timesleep_index = i
            if (i + ref_win) < (len(df)-1):
                window = i + ref_win
            else:
                window = len(df)-1
            for j in range(i,window):
                # if abs(df['DVol'][j] - df['DVol'][j+1]) < threshold:
                if abs(df['DVol'][j] - df['DVol'][j+1]) == 0: # water is not being used
                    sleeping.append(j)
            if len(sleeping) < (0.8*window): # if water is being used > 20% of the window, people aren't asleep yet 
                timesleep_index = len(df)-1 #resetting
            else: # if water usage is 0 for more than 80% of the window, people may be going to sleep now, so stop loop and return current index
                break
    return timesleep_index

'''For each day/date, group data by minute and calculate when the household woke up and went to sleep on that day. Add these values of each day to new dataframe.'''
for i in range(10,27): # for each node 
    # df = pd.read_csv('Data\DataDaily\ALLCF_Daily0'+str(i)+'.csv')
    df = pd.read_csv('Data\DailyUsage\ALLCF_Useful\\ALLCF_Useful'+str(i)+'.csv')
    dates = df['Date'].unique()
    wake_sleep_times = pd.DataFrame(columns = ['Node','Date','TimeWake','TimeSleep'])
    df['Hr-Minute'] = df.Time.str[:5]
    for date in dates: #for each date of the node
        df_date = df[df["Date"] == date]
        df_date = df_date.groupby('Hr-Minute').max() 
        timesleep_index = get_time_sleep(df_date)
        timewake_index = get_time_wake(df_date)
        # Add new row to final df
        new_row = [df_date['NodeID'][timewake_index], date, df_date['Time'][timewake_index], df_date['Time'][timesleep_index]]
        wake_sleep_times.loc[len(wake_sleep_times)] = new_row
    wake_sleep_times.to_csv('Data\DailyWakeSleepTimes/DailyWS_N'+str(i)+'.csv')
