import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import iplot
import plotly.io as pio
import random

hh_members = list(pd.read_excel('Data\HH_Occupancy.xlsx')['Members'])

weekdays = ['Mo','Tu','We','Th','Fr']
weekends = ['Sa','Su']
summer_months = ['04','05','06','07','08','09'] #april - september

for i in range(1,27):
    # Read file for node to plot
    df = pd.read_csv('Data\Preprocessed\OldSensorData\\filtered-2870dp\\filtered'+str(i)+'.csv')
    # Add columns for different time intervals
    df["Time"] = df.datetime.str[11:]
    df['Hour'] = df.Time.str[:2]
    df['Hr-Minute'] = df.Time.str[:5]
    # df['Date'] = df.datetime.str[:10]
    # No. of household occupants of this node (for mentioning in plot)
    no_hh_mem = hh_members[i-1]
    # Get a list of all dates in file, that are weekdays
    df_week = df[df['day'].isin(weekdays)]
    dates = df_week['Date'].unique()
    if len(dates) == 0: # if no data, skip to next node
        continue
    elif len(dates) < 6: # if less than 6 days of data, plot all of them
        dates_plot = dates
    else: # pick 6 random days to plot
        dates_plot = random.choices(dates,k=6)
    # Sort data for better plotting
    dates_plot.sort() # sorts legend labels 
    df = df.sort_values('Hr-Minute') # sorts x-axis labels
    # Plot each of the chosen days as a separate line
    fig = go.Figure()
    for d in dates_plot:
        df_date = df[df["Date"] == d] 
        df_date['DVol'] = df_date['volume'].cumsum()
        df_date = df_date.sort_values('Hr-Minute') # sort for x-axis
        # Different line styles for days in summer and winter months
        if d[5:7] in summer_months:
            fig = fig.add_trace(go.Scatter(x = df_date['Hr-Minute'], y = df_date["DVol"],mode='lines',line=dict(width=2,dash='dash'), name = str(d)[2:]))
        else:
            fig = fig.add_trace(go.Scatter(x = df_date['Hr-Minute'], y = df_date["DVol"],mode='lines',line=dict(width=2), name = str(d)[2:]))
    fig.update_xaxes(categoryorder='array', categoryarray= df['Hr-Minute'].unique())
    fig.update_traces(marker_size=2)
    fig.update_layout(title='N'+str(i)+' - '+str(no_hh_mem)+' Occupants (Weekdays)',yaxis_title = 'Daily Water Usage (L)', xaxis_title ='Time of Day (h:m)')
    # fig.show()
    pio.write_image(fig, "Daily Usage - Plots\\v4 - with zeros\\filtered-2870dp\\N"+str(i)+"-weekdays.png")

'''Faceted Plots'''
for i in range(1,10):
    df = pd.read_csv('Data\DataDaily\ALLCF_Filtered\ALLCF_Daily'+str(i)+'.csv')
    df['Hour'] = df.Time.str[:2] #adding col for hour component of Time
    df['Hr-Minute'] = df.Time.str[:5] #adding minute info in separate column, from Time
    no_hh_mem = hh_members[i-1] #no. of occupants in household for this node
    # Getting relevant info
    df_week = df[df['day'].isin(weekends)] # only taking datapoints for weekdays
    dates = df_week['Date'].unique() 
    rand_dates = random.choices(dates,k=6) # getting 6 random days to visualise
    df_dates = df_week[df_week["Date"].isin(rand_dates)] #getting datapoints of the 6 selected days only
    df_dates=df_dates.sort_values('Hr-Minute') # sort for x-axis
    # Plotting
    dates_plot.sort() # sorts legend labels 
    figtitle = 'N0'+str(i)+' - '+str(no_hh_mem)+' Occupants (Weekdays)'
    fig = px.line(df_dates,x='Hr-Minute',y='DVol',facet_row='Date',title=figtitle,height=1000)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1][2:]))
    for annotation in fig['layout']['annotations']: 
        annotation['textangle']= 0
    fig.update_xaxes(categoryorder='array', categoryarray= df_dates['Hr-Minute'].unique())
    fig.show()
    pio.write_image(fig, "Daily Usage\\faceted\\Weekends\\N0"+str(i)+"-weekends.png")