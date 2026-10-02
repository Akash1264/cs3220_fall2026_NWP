from src.locations import loc_A,loc_B, loc_C,loc_D

actionList = ['Right', 'Left', 'Suck', 'NoOp']

table =     {((loc_A, 'Clean'),): 'Right',
             ((loc_A, 'Dirty'),): 'Suck',
             ((loc_B, 'Clean'),): 'Left',
             ((loc_B, 'Dirty'),): 'Suck',
             ((loc_A, 'Dirty'), (loc_A, 'Clean')): 'Right',
             ((loc_A, 'Clean'), (loc_B, 'Dirty')): 'Suck',
             ((loc_B, 'Clean'), (loc_A, 'Dirty')): 'Suck',
             ((loc_B, 'Dirty'), (loc_B, 'Clean')): 'Left',
             ((loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Dirty')): 'Suck',
             ((loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_A, 'Dirty')): 'Suck'
            }


vacuumRules={((0, 0), 'Dirty'): 'Suck', 
       ((1, 0), 'Dirty'): 'Suck', 
       ((0, 0), 'Clean'): 'Right',
       ((1, 0), 'Clean'): 'Left'}



#Rules for your Task1

a2proRules={'Office manager': 'Give mail', 
'IT': 'Give donuts', 
'Student':'Give pizza',
'Clear':'Go ahead',
'Last room':'Stop'
}

#Rules for your Task2
catRules={
'Milk':'Drink',
'Sausage':'Eat',
'Mouse':'Catch',
'Empty':'GoAhead'
}

cat2Rules={
'Clear':'Go ahead',
'Last room':'Check direction',
'Mouse':'Catch',
'Dog':'Fight'
}

mouseAgentLocations = [loc_A,loc_B, loc_C,loc_D]