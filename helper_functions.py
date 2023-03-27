from datetime import datetime


def unix_to_datetime_local(df):
    '''Uses 'time_sampled' column to generate new column 'datetime' with timestamps of local timezone. 
    Input: Dataframe
    Returns: Dataframe with new 'datetime' column added.'''
    time_sampled = list(df['time_sampled'])
    datetime_obj = []
    for i in time_sampled:
        datetime_obj.append(datetime.fromtimestamp(int(i))) #converts each timestamp to datetime format using computer's local timezone ie KHI
    df['datetime'] = datetime_obj
    return df

def vol_in_interval(df):
    '''Uses 'total_flow' column to calculate volume water used between consecutive measurements.
    Input: Dataframe
    Returns: Dataframe with 'volume' column added. '''
    total_flow = list(df['total_flow'])
    flow_delta = []
    for i in range(len(total_flow)):
        if i != len(total_flow)-1:
            flow_delta.append(float(total_flow[i]) - float(total_flow[i+1]))
        else:
            flow_delta.append(0)
    df['volume'] = flow_delta
    return df

def rem_nonzero_start(df):
    '''Removes initial values in data if 'total_flow' (cumulative) does not start from 0. Cuts off data till first 0 total_flow.
    Input: Dataframe
    Returns: Dataframe with datapoints removed. '''
    totalflow = list(df['total_flow'])
    totalflow.reverse()
    for i in range(len(totalflow)):
        if totalflow[i] == 0:
            break
    df = df.iloc[:len(totalflow)-i]
    return df

def abs_vol(df):
    '''Makes all volume values positive, in case some are negative due to measurement orders being mixed up at server.
    Input: Dataframe
    Returns: Dataframe with all values in 'volume' column made positive.'''
    abs_vol = []
    for v in list(df['volume']):
        if v < 0:
            abs_vol.append(abs(v))
        else:
            abs_vol.append(v)
    df['volume'] = abs_vol
    return df

def clean_flowrate(df, maxflow):
    '''Removing datapoints where 'flow_rate' exceeds sensor capacity.'''
    df = df[df['flow_rate'] <= maxflow]
    # df = df[df['flow_rate'] > 0] #remove 0's
    return df  

def add_days(df):
    '''Generates names for days of the week, as first two letters (e.g. Mo, Tu, ...) using 'time_sampled' column.
    Input: Dataframe
    Returns: Dataframe with 'day' column added.'''
    time_sampled = list(df['time_sampled'])
    days = []
    for i in time_sampled:
        days.append(datetime.fromtimestamp(int(i)).strftime('%A')[:2])
    df['day'] = days
    return df

def get_cum_vol(df):
    '''Generates new column 'cumvol' from 'volume' to store cumulative volume used, where most recent datapoint is at index 0.
    Input: Dataframe
    Returns: Dataframe with 'cumvol' column added.'''
    vol =df['volume']
    vol = vol.iloc[::-1]
    cumvol = vol.cumsum()
    cumvol = cumvol.iloc[::-1]
    df['cumvol'] = cumvol
    return df

def get_daily_cum_vol(df):
    '''Generates column 'DVol' to store cumulative volume of water used for each day, using columns 'date' and 'volume'. This assumes that data is sorted such that most recent datapoint is at the last index.'''
    daily_vol = []
    dates = df['date'].unique()
    for d in dates:
        df_date = df[df["date"] == d]
        vol =df_date['volume']
        # vol = vol.iloc[::-1]
        cumvol = vol.cumsum()
        # cumvol = cumvol.iloc[::-1]
        daily_vol.extend(list(cumvol))
    df['DVol'] = daily_vol
    return df