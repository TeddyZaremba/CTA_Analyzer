# 
# Python interface for visualizing and getting statistics
# from the CTA2 database
#

import sqlite3
import matplotlib.pyplot as plt

###########################################################  
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    print("General stats:") 
    dbCursor.execute("Select count(*) From Stations;")
    row = dbCursor.fetchone();
    print("  # of stations:", f"{row[0]:,}")

    dbCursor.execute("Select count(*) From Stops;") 
    row = dbCursor.fetchone();
    print("  # of stops:", f"{row[0]:,}")

    dbCursor.execute("Select count(*) From Ridership;")
    row = dbCursor.fetchone();
    print("  # of ride entries:", f"{row[0]:,}")

    dbCursor.execute("select min(strftime('%Y-%m-%d', Ride_Date)), max(strftime('%Y-%m-%d', Ride_Date)) from Ridership;")
    row = dbCursor.fetchone();
    print("  date range:", f"{row[0]} - {row[1]}")

    dbCursor.execute("Select sum(Num_Riders) from Ridership;")
    row = dbCursor.fetchone();
    total_ridership = int(row[0])
    print("  Total ridership:", f"{row[0]:,}")

    dbCursor.execute("Select sum(Num_Riders) from Ridership where Type_of_Day ==  'W';")
    row = dbCursor.fetchone();
    percent = "{:.2f}".format(row[0] / total_ridership * 100)
    print("  Weekday ridership:", f"{row[0]:,} ({percent}%)")

    dbCursor.execute("Select sum(Num_Riders) from Ridership where Type_of_Day ==  'A';")
    row = dbCursor.fetchone();
    percent = "{:.2f}".format(row[0] / total_ridership * 100)
    print("  Saturday ridership:", f"{row[0]:,} ({percent}%)")

    dbCursor.execute("Select sum(Num_Riders) from Ridership where Type_of_Day ==  'U';")
    row = dbCursor.fetchone();
    percent = "{:.2f}".format(row[0] / total_ridership * 100)
    print("  Sunday/holiday ridership:", f"{row[0]:,} ({percent}%)")

###########################################################  
#
# get_bool
#
# Gets a yes or no input from the user 
#
def get_bool():
  print()
  plot_bool_q = input("Plot? (y/n) ")
  if plot_bool_q == 'y':
    return True # yes
  else:
    return False # else they said no

###########################################################  
#
# check_name
#
# Checks if a station name is valid
#
def check_name(station_name):
  dbCursor = dbConn.cursor()

  name_query = """Select station_ID, station_Name
  from stations
  where station_Name like '{}'""" 

  dbCursor.execute(name_query.format(station_name))
  station_id = dbCursor.fetchone()

  if station_id == None:
    print("**No station found...")
    return -1 # query returned nothing, error no. 1
  test_station = dbCursor.fetchone()
  if test_station != None:
    return -2 # query returned nothing, error no. 2
  
  return station_id # else return the station info

###########################################################  
#
# cmd_1
#
# Selects the station id and station name with a similar name to user input
#
def cmd_1():
  print()
  partial_station = input("Enter partial station name (wildcards _ and %): ")
  
  sql = "Select station_id, station_name from stations where station_name like '{}' order by station_name asc;".format(partial_station)

  dbCursor = dbConn.cursor()

  dbCursor.execute(sql)
  row = dbCursor.fetchone()

  if row == None: # fetching returned nothing
    print("**No stations found...")

  while row != None: # else iterate through the data and output the station info
    print(row[0], ':', row[1])
    row = dbCursor.fetchone()

###########################################################  
#
# cmd_2
#
# Selects the sum of the amount of riders 
# from the ridership and the total amount of riders for each station
#
def cmd_2():
  # Finds the amount of riders for all the stations together
  sql_query_1 = "select sum(num_riders) from ridership"

  # Finds the amount of riders for each station
  sql_query_2 = "select station_name, sum(num_riders) from stations join ridership on stations.station_ID == ridership.station_ID group by station_name order by station_name asc;"

  # Fetches the data for the toal amount of riders
  dbCursor = dbConn.cursor()

  dbCursor.execute(sql_query_1)
  row_total = dbCursor.fetchone()
  if row_total != None:
    total_riders = row_total[0]
  else:
    print('Error databasse has no riders')
    return
  
  print("** Ridership all stations **")
  
  dbCursor.execute(sql_query_2)
  row_indv = dbCursor.fetchone()
  while row_indv != None:
    row_indv_total = row_indv[1]
    percent_of_total = "{:.2f}".format(float(row_indv_total) / total_riders * 100)
    print(row_indv[0], ':', '{:,}'.format(int(row_indv_total)), '({}%)'.format(percent_of_total))
    row_indv = dbCursor.fetchone()

###########################################################  
#
# cmd_3
# 
# Outputs the top ten busiest stations
#
def cmd_3():
  # Finds the amount of riders for all the stations together
  sql_query_1 = "select sum(num_riders) from ridership"

  # Gets the total ridership of the top ten busiest stations
  sql_query_2 = "select station_name, sum(num_riders) as total from stations join ridership on stations.station_ID == ridership.station_ID group by station_name order by total desc limit 10;"

  # Fetches the data for the toal amount of riders
  dbCursor = dbConn.cursor()

  dbCursor.execute(sql_query_1)
  row_total = dbCursor.fetchone()
  if row_total != None:
    total_riders = row_total[0]
  else:
    print('Error databasse has no riders')
    return

  print("** top-10 stations **")
  
  dbCursor.execute(sql_query_2)
  row_indv = dbCursor.fetchone()
  while row_indv != None:
    row_indv_total = row_indv[1]
    percent_of_total = "{:.2f}".format(float(row_indv_total) / total_riders * 100)
    print(row_indv[0], ':', '{:,}'.format(int(row_indv_total)), '({}%)'.format(percent_of_total))
    row_indv = dbCursor.fetchone()

###########################################################  
#
# cmd_4
#
# Outputs the top ten least busy stations
#
def cmd_4():
  # Finds the amount of riders for all the stations together
  sql_query_1 = "select sum(num_riders) from ridership"

  # Gets the total ridership of the top ten least busy stations
  sql_query_2 = "select station_name, sum(num_riders) as total from stations join ridership on stations.station_ID == ridership.station_ID group by station_name order by total asc limit 10;"

  # Fetches the data for the toal amount of riders
  dbCursor = dbConn.cursor()

  dbCursor.execute(sql_query_1)
  row_total = dbCursor.fetchone()
  if row_total != None:
    total_riders = row_total[0]
  else:
    print('Error databasse has no riders')
    return

  print("** least-10 stations **")
  
  dbCursor.execute(sql_query_2)
  row_indv = dbCursor.fetchone()
  while row_indv != None:
    row_indv_total = row_indv[1]
    percent_of_total = "{:.2f}".format(float(row_indv_total) / total_riders * 100)
    print(row_indv[0], ':', '{:,}'.format(int(row_indv_total)), '({}%)'.format(percent_of_total))
    row_indv = dbCursor.fetchone()

###########################################################  
#
# cmd_5
#
# Outputs all the stop names that are along a line that user gives
#
def cmd_5():
  print()
  line_color = input('Enter a line color (e.g. Red or Yellow): ')

  # Gets the stops on the line color specified
  sql_query = "select distinct stop_name, direction, ada from stops join stopDetails on stops.stop_id == stopDetails.stop_id join lines on stopDetails.line_ID == lines.line_ID where lower(color) == '{}' order by stop_name asc;".format(line_color.lower())

  dbCursor = dbConn.cursor()
  dbCursor.execute(sql_query) # executes the query to get the stops along the line color
  name_direction_ada = dbCursor.fetchone()

  if name_direction_ada == None:
    print('**No such line...')
    return
  
  while name_direction_ada != None: # else iterate through and gather stop info
    name = name_direction_ada[0]
    direction = name_direction_ada[1]
    ada = name_direction_ada[2]

    # convert the ada to yes or no
    if ada == 1:
      ada_char = 'yes'
    else:
      ada_char = 'no'

    print(name, ':', "direction = {}".format(direction), "(accessible? {})".format(ada_char)) # output the stop info
    name_direction_ada = dbCursor.fetchone()

###########################################################  
#
# cmd_6
#
# Outputs the total ridership by month with the option of plotting it
#
def cmd_6():
  sql_query = "select strftime('%m', Ride_Date) as month, sum(num_riders) from Ridership group by month;"

  # execute the query to start the process
  dbCursor = dbConn.cursor()
  dbCursor.execute(sql_query)  
  month_riders = dbCursor.fetchone()

  print("** ridership by month **")
  months_list = []
  riders_list = []

  # Iterates through the database getting all the months and total ridership
  while month_riders != None:
    month = month_riders[0]
    riders = month_riders[1]

    months_list.append(month)
    riders_list.append(riders)

    print(month, ':', '{:,}'.format(int(riders))) # output the total riders by month
    month_riders = dbCursor.fetchone()

  plot_bool = get_bool() # gets user input to plot or not

  # if yes plot the riders by month
  if plot_bool:
    fig = plt.figure(figsize=(5, 5))
    plt.xlabel('month')
    plt.ylabel('Number of riders (x * 10^8)')
    plt.title('monthly ridership')
    plt.plot(months_list, riders_list)
    plt.show()
    return

###########################################################  
#
# cmd_7
#
# Outputs the total ridership by year with the option of plotting it
#
def cmd_7():
  sql_query = """select strftime('%Y', Ride_Date) as year, sum(num_riders) from Ridership 
  where year > '2000' and year <= '2021'
  group by year
  order by year asc;"""

  dbCursor = dbConn.cursor()
  dbCursor.execute(sql_query)
  
  yearly_riders = dbCursor.fetchone()

  if yearly_riders == None:
    return
  
  # Iterates through and gathers the riders by year
  print("** ridership by year **")
  yearly_riders_list = []
  while yearly_riders != None:
    year = yearly_riders[0]
    num_riders = int(yearly_riders[1])
    yearly_riders_list.append((year, num_riders))
    print(year, ':', '{:,}'.format(num_riders))
    yearly_riders = dbCursor.fetchone()

  plot_bool = get_bool() # gets user input to plot or not
  if plot_bool: # if yes, plot the riders by year
    fig = plt.figure(figsize=(8, 5))
    plt.xlabel('yearly')
    plt.ylabel('number of riders (x * 10^8)')
    plt.title('yearly ridership')
    plt.plot([x[0][-2:] for x in yearly_riders_list], [x[1] for x in yearly_riders_list])
    plt.show()
    return

###########################################################  
#
# cmd_8
#
# User inputs a year to compare the daily ridership for two stations
# with the otpion of plotting it
#
def cmd_8():
  print()
  year = input("Year to compare against? ")
  print()

  station_1 = input("Enter station 1 (wildcards _ and %): ")
  name_1 = check_name(station_1) # checks if station 1 is a valid station name
  if name_1 == -1:
    return
  elif name_1 == -2:
    print("**Multiple stations found...")
    return
  print()

  station_2 = input("Enter station 2 (wildcards _ and %): ")
  name_2 = check_name(station_2) # checks if station 2 is a valid station name
  if name_2 == -1:
    return
  elif name_2 == -2:
    print("**Multiple stations found...")
    return

  sql_query = """select strftime('%Y-%m-%d', Ride_Date), sum(num_riders) from Ridership
  join Stations
  on Ridership.Station_ID == Stations.Station_ID
  where Station_Name like '{}' and strftime('%Y', Ride_Date) == '{}'
  group by Ride_Date
  order by strftime('%Y-%m-%d', Ride_Date) asc;"""

  sql_query_station_1 = sql_query.format(station_1, year) 

  dbCursor = dbConn.cursor()

  # Gathers daily ridership for station 1
  print('Station 1:', name_1[0], name_1[1])
  dbCursor.execute(sql_query_station_1)
  station_1_riders = dbCursor.fetchone()
  station_1_riders_list = []

  while station_1_riders != None:
    d = station_1_riders[0]
    riders = int(station_1_riders[1])
    station_1_riders_list.append((d, riders))
    station_1_riders = dbCursor.fetchone()

  # outputs first ten and last ten days for station 1
  for i in range(0, 5):
    print(station_1_riders_list[i][0], station_1_riders_list[i][1])
  for i in range(len(station_1_riders_list) - 5, len(station_1_riders_list)):
    print(station_1_riders_list[i][0], station_1_riders_list[i][1])

  # Gathers daily ridership for station 2 
  print('Station 2:', name_2[0], name_2[1])
  sql_query_station_2 = sql_query.format(station_2, year)
  dbCursor.execute(sql_query_station_2)
  station_2_riders = dbCursor.fetchone()
  station_2_riders_list = []

  while station_2_riders != None:
    d = station_2_riders[0]
    riders = int(station_2_riders[1])
    station_2_riders_list.append((d, riders))
    station_2_riders = dbCursor.fetchone()

  # outputs first ten and last ten days for station 2
  for i in range(0, 5):
    print(station_2_riders_list[i][0], station_2_riders_list[i][1])
  for i in range(len(station_2_riders_list) - 5, len(station_2_riders_list)):
    print(station_2_riders_list[i][0], station_2_riders_list[i][1])

  plot_bool = get_bool() # gets user input to plot or not
  if plot_bool: # if yes, plot the riders by day comparing the two stations
    plt.plot([x[1] for x in station_1_riders_list], color = "blue", label = name_1[1])
    plt.plot([x[1] for x in station_2_riders_list], color = "orange", label = name_2[1])
    plt.title('riders each day of {}'.format(year))
    plt.legend(loc="upper left")
    plt.ylabel('number of riders')
    plt.xlabel('day')
    plt.show()
    return

###########################################################  
#
# cmd_9
# 
# Inputs a line from the user and outputs all stations along that line
# with the option of plotting it
#
def cmd_9():
  print()
  line_color = input("Enter a line color (e.g. Red or Yellow): ")
  sql_query =  """select distinct station_name, Latitude, Longitude from Stations
  join stops
  on Stations.Station_ID == Stops.Station_ID
  join stopDetails
  on stops.stop_id == stopDetails.stop_id
  join lines
  on stopDetails.line_ID == lines.line_ID
  where lower(color) == '{}'
  order by station_name asc;""".format(line_color.lower())

  dbCursor = dbConn.cursor()
  dbCursor.execute(sql_query)
  station_lat_long = dbCursor.fetchone()

  if station_lat_long == None: # line color is invalid 
    print('**No such line...')
    return

  station_names = []
  lat_list = []
  long_list = []

  # Gathers coordinates for stops along the line color
  while station_lat_long != None:
    station_name = station_lat_long[0]
    lat = float(station_lat_long[1])
    long = float(station_lat_long[2])

    station_names.append(station_name)
    lat_list.append(lat)
    long_list.append(long)
    print(station_name, ':', '({}, {})'.format(lat, long))

    station_lat_long = dbCursor.fetchone()

  plot_bool = get_bool() # Asks user to plot or not
  if plot_bool: # if yes plot the stops along the line in the chicago.png image
    image = plt.imread('chicago.png')

    xydims = [-87.9277, -87.5569, 41.7012, 42.0868] # sets the boundaries in terms of coordinates
    plt.imshow(image, extent=xydims)
    plt.title(line_color + " Line")

    if (line_color.lower() == "purple-express"):
      line_color = 'Purple' # changes color to purple from purple-express
    plt.plot(long_list, lat_list, "o", c=line_color)

    for station_name, long, lat in zip(station_names, long_list, lat_list): # labels the stops 
      plt.annotate(station_name, (long, lat))

    plt.xlim([-87.9277, -87.5569])
    plt.ylim([41.7012, 42.0868])
    plt.show()


#
# Main
#
if __name__ == '__main__':
  print('** Welcome to CTA L analysis app **\n')

  # connects the database and prints basic stats about the database
  dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')
  print_stats(dbConn)
  print()

  # Loop accepting commands to plot and view ridership data until command x is enterd
  cmd = input('Please enter a command (1-9, x to exit): ')
  while cmd != 'x':

    if cmd == '1':
      cmd_1()

    elif cmd == '2':
      cmd_2()

    elif cmd == '3':
      cmd_3()

    elif cmd == '4':
      cmd_4()

    elif cmd == '5':
      cmd_5()

    elif cmd == '6':
      cmd_6()

    elif cmd == '7':
      cmd_7()

    elif cmd == '8':
      cmd_8()

    elif cmd == '9':
      cmd_9()

    else:
      print('**Error, unknown command, try again...')

    # Continue to the next command
    print()
    cmd = input('Please enter a command (1-9, x to exit): ')

  #
  # done
  #