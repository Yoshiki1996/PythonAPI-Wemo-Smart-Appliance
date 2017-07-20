'''
This Python Code will be the one which dynamically stores the data of the Wemo
Switch when it is executed. The data is stored on average every 2-3 seconds.

This code should not be plagarized nor used for credential/academic purposes
unless stated otherwise by the owner. Modification and usage is accepted upon
approval.

For more details contact: yoshiki.shoji@mail.utoronto.ca
'''

# PYMYSQL MODULES
import pymysql
import pymysql.cursors

# OUIMEAUX MODULES
import ouimeaux
from ouimeaux.environment import Environment
from ouimeaux.signals import receiver, statechange, devicefound

# Connect to the database
connection = pymysql.connect(host="localhost",
                             user='root',
                             passwd='ditpwd',
                             db="DATA")
                            

# Inserting paramater data in mysql
def kv_pairs(dict):
    '''OBTAINING THE KEY-VALUE PAIR PARAMATERS'''
    '''this function will be used to seperate
    key-value pairs in the dictionary for inserting
    data into MYSQL'''
    
    keys = str(list(dict.keys()))[:].replace('[', '(').replace(']', ')')
    vals = str(list(dict.values()))[:].replace('[', '(').replace(']', ')')
    
    keys = keys.replace("'","")
    vals = vals.replace("'","")
    return keys,vals
    
def SWITCH(list_switches):
    '''This function intakes the list of switches
    and returns the attributes given by the environment
    NOTE: Returns a Tuple
    '''
    # Obtaining the switch parameters
    switch_name = list_switches
    switch_wemo = env.get_switch(switch_name)
    # Note: Parameters are stored in dictionary
    switch_param = switch_wemo.insight_params
    # Delete lastchange: Unnecessary Parameter
    switch_param.pop('lastchange')
    
    # Adding DATE and TIME dictionary to SWITCH_PARAM
    switch_param['TIME'] = 'CURTIME()'
    switch_param['DATE'] = 'CURDATE()'
    
    return switch_name,switch_wemo,switch_param
    
# Initializing the ouimeaux environment
env = Environment()

try:
    # Commit every data as by default it is False
    connection.autocommit(True)
    
    # Create a cursor object
    cursorObject = connection.cursor()  
    
    env.start()
    env.discover(3)
        
    '''using MYSQL functions to insert date and time
       USEFUL FUNCTIONS IN MYSQL:
       CURRENT_TIMESTAMP
       CURRENT_DATE
       CURRENT_TIME
    '''
    try:
        env.start()
        env.discover(5)
        
        while True:
            
            for i in range(len(env.list_switches())):
                
                #Calling the helper function
                switch = SWITCH(list(env.list_switches())[i])
                
                # Obtaining the switch parameters
                switch_name = switch[0]
                switch_wemo = switch[1]
                
                # Note: Parameters are stored in dictionary
                switch_param = switch[2]
                
                keys = kv_pairs(switch_param)[0]
                vals = kv_pairs(switch_param)[1]
        
                print('------------')
                
                # 1 indicates switch is on and load is on
                if switch_wemo.get_state() == 1:
                    #print("name:",SWITCH,"STATE:ON")
                    insertStatement = ("INSERT INTO DATA_"+switch[0]+"(DATE,TIME,STATE)"
                                    "VALUES(CURDATE(),CURTIME(),\"S:ON  | L:ON\")")
                    cursorObject.execute(insertStatement)
                    
                # 8 indicates switch is on but load is off 
                elif switch_wemo.get_state() == 8:
                    #print("name:",SWITCH,"STATE:ON")
                    insertStatement = ("INSERT INTO DATA_"+switch[0]+"(DATE,TIME,STATE)"
                                    "VALUES(CURDATE(),CURTIME(),\"S:ON  | L:OFF\")")
                    cursorObject.execute(insertStatement)
                    
                # 0 indicates switch if off 
                else:
                    #print("name:",SWITCH,"STATE:OFF")
                    insertStatement = ("INSERT INTO DATA_"+switch[0]+"(DATE,TIME,STATE)"
                                    "VALUES(CURDATE(),CURTIME(),\"S:OFF | L:OFF\")")
                    cursorObject.execute(insertStatement)
                
                #inserting new params
                cursorObject.execute('INSERT INTO ' +switch[0]+ ' %s VALUES %s' % (keys, vals))
                env.wait(1)
            
    except (KeyboardInterrupt, SystemExit):
        print("Goodbye!")
        sys.exit(0)

    # # List the tables using SQL command
    # sqlShowTablesCommand = "show tables"  
    #  
    # # Execute the SQL command
    # cursorObject.execute(sqlShowTablesCommand)
    
        
except Exception as e:
    print("Exeception occured:{}".format(e))
    pass 
    
finally:
    
    connection.close()
