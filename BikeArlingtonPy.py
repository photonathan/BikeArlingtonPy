# -*- coding: utf-8 -*-
"""
BikeArlingtonPy is a python module for downloading Arlington, VA Bike data.

Customizable search parameters: CounterID, 
                                Start/End Date, 
                                Bicycle/Pedestrian/Both, 
                                Hourly/Daily counts, 
                                Inbound/Outbound Direction

Bikeometer will refer to the machine performing the counting while count will 
refer to the number of bikers counted.

@author: Nathan Goldberg
"""

import re
import requests
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine
import os

url = 'http://webservices.commuterpage.com/counters.cfc?wsdl'

#################
# Main Functions#
#################

#TODO Make this function accept parameters to customize functionality

def all_counts_by_date_to_sql():
    '''   
    Queries the Bike Arlington API to pull all counts by day.

    Hardcoded start date that represents the first datapoint in the Bike Arlington API.
    
    Data is parsed, cleaned, and converted to a dataframe with defined columns.
    
    Dataframe is uploaded to MySQL Database

    Returns
    -------
    None.

    '''
    ## Test db Connection##
    # Creates the parameters to drive the connection
    engine = create_new_engine('bikeometers_db')
    # Tests the connection and throws an error if not established
    engine.connect()
    # Bike Arlington API only accepts query ranges of 1 year or less
    # July 1, 2011 was the first data point in their database
    start_date = date(year=2011, month=7, day=1)
    end_date = date(year=2012, month=7, day=1)
    # Create a list to hold count data
    count_in_date_range_list = []   
    while end_date <= date.today() - timedelta(days=1):  
    # Hardcoded the counterID list to not stress the server
        bikeometer_id_list = ['33','30','43','24','59','56','47','48','10','20',
                           '35','57','18','3','58','61','62','38','44','14',
                           '60','5','6','42','37','27','26','8','7','51','52',
                           '45','22','21','36','34','41','9','39','16','15',
                           '54','55','31','28','11','2','25','19']
        for bikeometer_id in bikeometer_id_list:
            # Dates YYYY-MM-DD format converted to MM-DD-YYY and made into a string to search Counter API
            clean_start_date = f'{start_date.month}/{start_date.day}/{start_date.year}'
            clean_end_date = f'{end_date.month}/{end_date.day}/{end_date.year}'
            # Calls the get_count_in_date_range function and passes in hard-coded
            # parameters like the start_date, which is the first datapoint in
            # Bike Arlington server. Optimally, these would not be hardcoded to 
            # make the porgram more future-proof.
            api_counts_to_list(bikeometer_id, clean_start_date, clean_end_date, count_in_date_range_list, interval='d')
        # Adds a year to start date and end date
        start_date = start_date.replace(year = start_date.year + 1)
        end_date = end_date.replace(year = end_date.year + 1)
        # If end date is yesterday's date, congratulations, you pulled all available dates
        # We won't pull today's date in case the data has not been uploaded to their servers yet
        if end_date == date.today() - timedelta(days=1):
            break                
        # If end date is after yesterday's date, set the end date to yesterday and pull the data one last time
        if end_date >= date.today():
            end_date = date.today() - timedelta(days=1)
    columns = ('bikeometer_id', 'date', 'direction', 'count', 'is_weekend', 'year', 'month', 'day', 'month_day')
    df = pd.DataFrame(count_in_date_range_list, columns=columns)
    # Replaces table counts, use if_exists='replace' to replace the table
    df.to_sql('counts_daily', con=engine, index=False, if_exists='replace')
    # Reads the table
    #df2 = pd.read_sql('counters', con=engine)
    with engine.connect() as con:
        date_list = con.execute('SELECT MAX(Date) FROM counts_daily')
        for day in date_list:
            last_day = day[0]
            print(f'The newest date in counts_daily is {last_day}')

def all_counts_by_hour_to_sql():
    '''   
    Queries the Bike Arlington API to pull all counts by hour.

    Hardcoded start date that represents the first datapoint in the Bike Arlington API.
    
    Data is parsed, cleaned, and converted to a dataframe with defined columns.
    
    Dataframe is uploaded to MySQL Database

    Returns
    -------
    None.

    '''
    ## Test db Connection##
    # Creates the parameters to drive the connection
    engine = create_new_engine('bikeometers_db')
    # Tests the connection and throws an error if not established
    engine.connect()
    # Establish connection to MySQL database before making all the API calls.
    # Bike Arlington API only accepts query ranges of 1 year or less
    # July 1, 2011 was the first data point in their database
    start_date = date(year=2011, month=7, day=1)
    end_date = date(year=2012, month=7, day=1)
    # Create a list to hold count data
    count_in_date_range_list = []   
    while end_date <= date.today() - timedelta(days=1):  
    # Hardcoded the counterID list to not stress the server
        bikeometer_id_list = ['33','30','43','24','59','56','47','48','10','20',
                           '35','57','18','3','58','61','62','38','44','14',
                           '60','5','6','42','37','27','26','8','7','51','52',
                           '45','22','21','36','34','41','9','39','16','15',
                           '54','55','31','28','11','2','25','19']
        for bikeometer_id in bikeometer_id_list:
            # Dates YYYY-MM-DD format converted to MM-DD-YYY and made into a string to search Counter API
            clean_start_date = f'{start_date.month}/{start_date.day}/{start_date.year}'
            clean_end_date = f'{end_date.month}/{end_date.day}/{end_date.year}'
            # Calls the get_count_in_date_range function and passes in hard-coded
            # parameters like the start_date, which is the first datapoint in
            # Bike Arlington server. Optimally, these would not be hardcoded  
            # make the porgram more future-proof.
            api_counts_to_list(bikeometer_id, clean_start_date, clean_end_date, count_in_date_range_list, interval='h')
        # If end date is yesterday's date, congratulations, you pulled all available dates
        # We won't pull today's date in case the data has not been uploaded to their servers yet
        if end_date == date.today() - timedelta(days=1):
            break               
        # Adds a year to start date and end date
        start_date = start_date.replace(year = start_date.year + 1)
        end_date = end_date.replace(year = end_date.year + 1)
        # If end date is after yesterday's date, set the end date to yesterdayand pull the data one last time
        if end_date >= date.today():
            end_date = date.today() - timedelta(days=1)    
    columns = ('bikeometer_id', 'date', 'direction', 'count', 'hour', 'is_weekend', 'year', 'month', 'day', 'month_day')
    df = pd.DataFrame(count_in_date_range_list, columns=columns)
    # Replaces table counts, use if_exists='replace' to insert new values into the table
    df.to_sql('counts_hourly', con=engine, index=False, if_exists='replace')
    # Reads the table
    #df2 = pd.read_sql('counters', con=engine)
    with engine.connect() as con:
        date_list = con.execute('SELECT MAX(Date) FROM counts_hourly')
        for day in date_list:
            last_day = day[0]
            print(f'The newest date in counts_hourly is {last_day}')


def new_counts_by_hour_to_sql():
    '''   
    Queries your database to find the most recent date uploaded.
    
    Uses the most recent date to query the Bike Arlington API to pull all hourly counts 
    until yesterday.
   
    Data is parsed, cleaned, and converted to a dataframe with defined columns.
    
    Dataframe is uploaded to MySQL Database

    Returns
    -------
    None.

    '''
    engine = create_new_engine('bikeometers_db')
    # Establish connection to MySQL database before making all the API calls.
    #TODO: Add except here that will stop code if connection isn't successful
    # Tests the connection and throws an error if not established
    engine.connect()
    #TODO: If no data is in the MySQL database, custom except error
    # This prevents the program from pulling today's date
    start_date = last_sql_date_counts_hourly(engine) + timedelta(days=1)
    if start_date == None:
        print('No data found in MySQL database.')
        print('Please use all_counts_to_sql() function')
        return None
    if start_date >= date.today() - timedelta(days=1):
        #TODO: throw an exception error instead of print
        print('No new data avaiable')
        return None
    end_date = start_date.replace(year = start_date.year + 1)
    if end_date >= date.today():
        end_date = date.today() - timedelta(days=1)
     ## Test db Connection##
    # Creates the parameters to drive the connection

    # Bike Arlington API only accepts query ranges of 1 year or less
    count_in_date_range_list = []   
    while end_date <= date.today() - timedelta(days=1):  
    # Hardcoded the counterID list to not stress the server
        bikeometer_id_list = ['33','30','43','24','59','56','47','48','10','20',
                           '35','57','18','3','58','61','62','38','44','14',
                           '60','5','6','42','37','27','26','8','7','51','52',
                           '45','22','21','36','34','41','9','39','16','15',
                           '54','55','31','28','11','2','25','19']
        for bikeometer_id in bikeometer_id_list:
            # Dates YYYY-MM-DD format converted to MM-DD-YYY and made into a string to search Counter API
            clean_start_date = f'{start_date.month}/{start_date.day}/{start_date.year}'
            clean_end_date = f'{end_date.month}/{end_date.day}/{end_date.year}'
            # Calls the get_count_in_date_range function and passes in hard-coded
            # parameters like the start_date, which is the first datapoint in
            # Bike Arlington server. Optimally, these would not be hardcoded  
            # make the porgram more future-proof.
            api_counts_to_list(bikeometer_id, clean_start_date, clean_end_date, count_in_date_range_list, interval='h')
        # If end date is yesterday's date, congratulations, you pulled all available dates
        # We won't pull today's date in case the data has not been uploaded to their servers yet
        if end_date == date.today() - timedelta(days=1):
            break                
        # Adds a year to start date and end date
        start_date = start_date.replace(year = start_date.year + 1)
        end_date = end_date.replace(year = end_date.year + 1)
        # If end date is after yesterday's date, set the end date to yesterdayand pull the data one last time
        if end_date >= date.today():
            end_date = date.today() - timedelta(days=1)
    # If interval is hours, length of tuple will be 5.
    columns = ('bikeometer_id', 'date', 'direction', 'count', 'hour', 'is_weekend', 'year', 'month', 'day', 'month_day')
    df = pd.DataFrame(count_in_date_range_list, columns=columns)
    # Replaces table counts, use if_exists='append' to insert new values into the table
    df.to_sql('counts_hourly', con=engine, index=False, if_exists='append')
    # Reads the table, returns the newest date, and closes the connection
    with engine.connect() as con:
        date_list = con.execute('SELECT MAX(Date) FROM counts_hourly')
        for day in date_list:
            last_day = day[0]
            print(f'The newest date in counts_hourly is {last_day}')


def new_counts_by_day_to_sql():
    '''   
    Queries your database to find the most recent date uploaded.
    
    Uses the most recent date to query the Bike Arlington API to pull all daily counts 
    until yesterday.
   
    Data is parsed, cleaned, and converted to a dataframe with defined columns.
    
    Dataframe is uploaded to MySQL Database

    Returns
    -------
    None.

    '''
    engine = create_new_engine('bikeometers_db')
    # Establish connection to MySQL database before making all the API calls.
    #TODO: Add except here that will stop code if connection isn't successful
    #TODO: If no data is in the MySQL database, custom except error
    # This prevents the program from pulling today's date
    start_date = last_sql_date_counts_daily(engine) + timedelta(days=1)
    if start_date == None:
        print('No data found in MySQL database.')
        print('Please use all_counts_to_sql() function')
        return None
    if start_date >= date.today() - timedelta(days=1):
        #TODO: throw an exception error instead of print
        print('No new data avaiable')
        return None
    end_date = start_date.replace(year = start_date.year + 1)
    if end_date >= date.today():
        end_date = date.today() - timedelta(days=1)
     ## Test db Connection##
    # Creates the parameters to drive the connection
    # Bike Arlington API only accepts query ranges of 1 year or less
    count_in_date_range_list = []   
    while end_date <= date.today() - timedelta(days=1):  
    # Hardcoded the counterID list to not stress the server
        bikeometer_id_list = ['33','30','43','24','59','56','47','48','10','20',
                           '35','57','18','3','58','61','62','38','44','14',
                           '60','5','6','42','37','27','26','8','7','51','52',
                           '45','22','21','36','34','41','9','39','16','15',
                           '54','55','31','28','11','2','25','19']
        for bikeometer_id in bikeometer_id_list:
            # Dates YYYY-MM-DD format converted to MM-DD-YYY and made into a string to search Counter API
            clean_start_date = f'{start_date.month}/{start_date.day}/{start_date.year}'
            clean_end_date = f'{end_date.month}/{end_date.day}/{end_date.year}'
            # Calls the get_count_in_date_range function and passes in hard-coded
            # parameters like the start_date, which is the first datapoint in
            # Bike Arlington server. Optimally, these would not be hardcoded  
            # make the porgram more future-proof.
            api_counts_to_list(bikeometer_id, clean_start_date, clean_end_date, count_in_date_range_list, interval='d')
        # If end date is yesterday's date, congratulations, you pulled all available dates
        # We won't pull today's date in case the data has not been uploaded to their servers yet
        if end_date == date.today() - timedelta(days=1):
            break                
        # Adds a year to start date and end date
        start_date = start_date.replace(year = start_date.year + 1)
        end_date = end_date.replace(year = end_date.year + 1)
        # If end date is after yesterday's date, set the end date to yesterdayand pull the data one last time
        if end_date >= date.today():
            end_date = date.today() - timedelta(days=1)    
    columns = ('bikeometer_id', 'date', 'direction', 'count', 'is_weekend', 'year', 'month', 'day', 'month_day')
    df = pd.DataFrame(count_in_date_range_list, columns=columns)
    # Replaces table counts, use if_exists='append' to insert new values into the table
    df.to_sql('counts_daily', con=engine, index=False, if_exists='append')
    # Reads the table
    #df2 = pd.read_sql('counters', con=engine)
    with engine.connect() as con:
        date_list = con.execute('SELECT MAX(Date) FROM counts_daily')
        for day in date_list:
            last_day = day[0]
            print(f'The newest date in counts_daily is {last_day}')



def bikeometer_to_sql():
    '''
    Makes a GET request to the Bike Arlington API using the GetAllCounters 
    method as a parameter. The API returns a response object that is first
    converted to a string, cleaned, and converted to an XML object. The XML 
    object is then parsed for the relevant information, and added to a list.
    Each list, representing a Bikeometer, is converted to a tuple and added 
    to a final list which can easily be saved to a csv or dataframe. 
    
    Returns
    -------
    bikeometer_details : list
    
    Returns a list of tuples. Each tuple represents the details of one bikeometer
    '''
    engine = create_new_engine('bikeometers_db')
    url = 'http://webservices.commuterpage.com/counters.cfc?wsdl'
    # Defines the method in a dictionary used to make the request
    counter_reqest_methods = {'method': 'GetAllCounters'}
    # Save the GetAllCounters request to memory
    response = requests.get(url, params=counter_reqest_methods)
    # Save the conent of that request (string) to memory 
    string_data = response.text
    # Clean the string
    clean_string_data = re.sub(r'[\n|\t]', '', string_data)
    # Convert string to XML object
    root = ET.fromstring(clean_string_data)
    # Create the empty list that will include [(Name, counterID, Lat, Long, Region, region_id)(...)]
    bikeometer_details = []
    # Iterate through the children, grandchildren, and great-grandchildren and grab req data  
    for child in root:
        # From child 'counter' gets the attribute 'id' of the counter and adds it to single_list
        single_list = [child.get('id')]
        # Loops through the grandchildren of root
        for grandchild in list(child):   
            if grandchild.text != None and grandchild.tag != 'description' and grandchild.tag != 'trail_id' and grandchild.tag != 'trail_name':
                # If the grandchild is region, loop through region and grab the grandchildren data
                if grandchild.tag == 'region':  
                    for great_grandchild in list(grandchild): 
                        single_list.append(great_grandchild.text)
                # If the grandchild is not region, the data is available in grandchild.text
                else: 
                    single_list.append(grandchild.text)
        # Cast the list into a tuple making it easier to migrate data to the database
        single_tuple = tuple(single_list)
        # Appends tuples to the list
        bikeometer_details.append(single_tuple)
    columns = ('bikeometer_id', 'name', 'latitude', 'longitude', 'region', 'region_id')
    df = pd.DataFrame(data=bikeometer_details, columns = columns)
    df[["name", "latitude", "longitude", "region", 'region_id']] = df[["name", "latitude", "longitude", "region", 'region_id']].astype('string')
    df[["bikeometer_id"]] = df[["bikeometer_id"]].astype('int')
    df.to_sql('bikeometer_details', con=engine, index=False, if_exists='replace')


##################
#Helper Functions#
##################

def create_new_engine(db_name):
    '''
    Uses enviornmental variables to connect to your MySQL database.
    
    Parameters
    ----------
    db_name : string
    Name of the database you want to connect to.
        

    Returns
    -------
    Function engine object
    '''
    return create_engine(f'mysql+mysqldb://{os.environ["arlington_user"]}:{os.environ["arlington_password"]}@localhost/{db_name}', echo=False)

def api_counts_to_list(bikeometer_id, 
                               start_date,
                               end_date, 
                               count_in_date_range_list,
                               mode='B', 
                               interval='d', 
                               start_time='0:00', 
                               end_time= '23:59', 
                               direction='') -> list:
    '''
    Makes a GET request to the Bike Arlington API using the GetCountInDateRange 
    method as a parameter. The API returns a response object that is first
    converted to a string, cleaned, and converted to an XML object. The XML 
    object is then parsed for the relevant information, and added to a list.
    Each list, representing a count, is converted to a tuple and added 
    to a final list which can easily be saved to a csv or dataframe using another funciton. 

    Parameters
    ----------
    bikeometer_id : Str
        ID of the physical Bikeomter counting the bikers
    start_date : Str
        First date to pull data from the API
    end_date : Str
        Last date to pull data from the API
        *Note* Can't be more than 1 year from start_date
    count_in_date_range_list : list
        List to save individual tuples into
    mode : Str, optional
        Specify to pull Bikers using 'B' or Pedestrians using 'P' . The default is 'B'.
        Leave blank to pull both.
    interval : Str, optional
        D for Daily, H for hourly, M for Minute. The default is 'd'.
    start_time : Str, optional
        Military time. The default is '0:00'.
    end_time : Str, optional
        Military time. The default is '23:59'.
    direction : Str, optional
        I for inbound, O for outbound, blank for both. The default is ''.

    Returns
    -------
    List of tuples. Each tuple is a data point.

    '''
    request_parameters = {'method': 'GetCountInDateRange',
            'counterID': str(bikeometer_id),
            'startDate': start_date,
            'endDate': end_date,
            'mode': str(mode),
            'interval': str(interval),
            'direction': direction}
    response = requests.get(url, params=request_parameters)
        #TODO: Add except for non-200 response
    # Convert response to a string
    xml_data = response.text
    # Clean the data
    clean_xml_data = re.sub(r'[\n|\t]', '', xml_data)
    # Cast the string to an XML element
    tree = ET.fromstring(clean_xml_data)
    # Create the empty dictionary to put the data in
    #CountInDateRangeDict = {}
    # Parse the GetCountInDateRange XML file for the count and date and save CountInDateRangeDict
    if interval == 'd':
        for type_tag in tree.findall('count'):
            count = type_tag.get('count')
            date = type_tag.get('date')
            # Converts counter date to a date object
            date = datetime.strptime(date, '%m/%d/%Y').date()
            year = date.year
            month = date.month
            day = date.day
            month_day = f'{month}_{day}'
            direction = type_tag.get('direction')
            if date.weekday() <= 4:
                is_weekend = 0
            else:
                is_weekend = 1
            single_tuple = (bikeometer_id, date, direction, count, is_weekend, year, month, day, month_day)
            count_in_date_range_list.append(single_tuple)
            
    if interval == 'h':
        for type_tag in tree.findall('count'):
            count = type_tag.get('count')
            date = type_tag.get('date')
            # Converts counter date to a date object
            date = datetime.strptime(date, '%m/%d/%Y').date()
            year = date.year
            month = date.month
            day = date.day
            month_day = f'{month}_{day}'
            direction = type_tag.get('direction')
            hour = type_tag.get('hour')
            if date.weekday() <= 4:
                is_weekend = 0
            else:
                is_weekend = 1
            single_tuple = (bikeometer_id, date, direction, count, hour, is_weekend, year, month, day, month_day)
            count_in_date_range_list.append(single_tuple)
    return count_in_date_range_list


def last_sql_date_counts_hourly(engine):
    ''' Returns the last date in the MySQL database as a datetime object'''
    with engine.connect() as con:
        date = con.execute('SELECT MAX(Date) FROM counts_hourly')
    for day in date:
            date = day[0]
    return date



def last_sql_date_counts_daily(engine):
    ''' Returns the last date in the MySQL database as a datetime object'''
    with engine.connect() as con:
        date = con.execute('SELECT MAX(Date) FROM counts_daily')
    for day in date:
            date = day[0]
    return date


def first_sql_date_counts_daily(engine):
    ''' Returns the first date in the MySQL database as a datetime object'''
    with engine.connect() as con:
        date = con.execute('SELECT MIN(Date) FROM counts_daily')
        for day in date:
            date = day[0]
    return date

def first_sql_date_counts_hourly(engine):
    ''' Returns the first date in the MySQL database as a datetime object'''
    with engine.connect() as con:
        date = con.execute('SELECT MIN(Date) FROM counts_hourly')
        for day in date:
            date = day[0]
    return date

###########################
#Not Implemented Functions#
###########################


def bikeometer_to_dataframe(CounterLocationsList):
    '''
    Returns a dataframe

    Parameters
    ----------
    CounterLocationsList : list
        accepts a list of tuples.

    Returns
    -------
    df : TYPE
        DESCRIPTION.

    '''
    pass

def dataframe_to_sql(dataframe, schema_name, table_name, if_exists_behavior):
    '''
    Copies a pandas dataframe into MySQL.

    Parameters
    ----------
    dataframe : pandas dataframe object
        DESCRIPTION.
    schema_name : String
        DESCRIPTION.
    table_name : String
        DESCRIPTION.
    if_exists_behavior : String
        fail: Raise a ValueError
        replace: Drop the table before inserting new values
        append: Insert new values to the existing table

    Returns
    -------
    None.

    '''
    pass




# data = CountToDataFrame()
def get_weather():
    '''
    Returns the weather

    Returns
    -------
    None.

    '''
    pass

def save_to_text():
    pass
    # with open('allcountsandhours2.txt', 'a') as f:
#     f.write(str(df))

def save_to_sql():
    pass

def save_to_csv():
    pass

def save_to_pickle():
    pass


def count_dataframe_to_sql(columns):
    pass

def bikeometer_dataframe_to_sql():
    pass

def count_dataframe_to_pickle():
    pass

def CounterDataframeToPickle():
    pass

def upsert_sql():
    '''
    Adds rows to your MySQL database

    Returns
    -------
    None.

    '''
    pass

def upsert_pickle():
    '''
    Adds rows to the pickled dataframe

    Returns
    -------
    None.

    '''
    pass



#all_counts_by_date_to_sql()
#print(last_sql_date_counts_daily())
new_counts_by_day_to_sql()
#new_counts_by_hour_to_sql()
#bikeometer_to_sql()
# df = get_new_counts()
# dataframe_to_sql(df, 'bikeometers_db', 'counts and hours', 'append')

