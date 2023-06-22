# -*- coding: utf-8 -*-
"""
This code is taken from the itertree package:
https://pypi.org/project/itertree/
GIT Home:
https://github.com/BR1py/itertree
The documentation can be found here:
https://itertree.readthedocs.io/en/latest/index.html

The code is published under MIT license incl. human protect patch:

The MIT License (MIT) incl. human protect patch
Copyright © 2022 <copyright holders>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

Human protect patch:
The program and its derivative work will neither be modified or executed to harm any human being nor through
inaction permit any human being to be harmed.

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For more information see: https://en.wikipedia.org/wiki/MIT_License


########################################################################################################################

This file contains an example for the usage of iTree: Calendar

We build an iTree object that contains the structure of a calendar and we fill in some dates.
Afterwards we filter for the date characteristics.
"""
from __future__ import absolute_import

from fnmatch import fnmatch
import datetime
import time
from itertree import *
import datetime
from collections import deque
import random

# define some objects to b placed in the calendar

def get_iso_date(item):
    if item.level==3:
        out_str='%i-%i-%i'%(
            item.parent.parent.tag,
            item.parent.idx,
            item.tag)
    elif item.level==5:
        out_str = '%i-%i-%i %02i:%02i'  % (
            item.parent.parent.parent.parent.tag, #year
            item.parent.parent.parent.idx, #month
            item.parent.parent.idx, #days
            item.parent.idx,#hours
            item.idx)
    else:
        return str(item)
    return out_str


class Birthday():
    def __init__(self,person,year):
        self.person=person
        self.year=year
        self.itree_item_path=None
        self.alarms=[]
        self._hash=random.randint(0, 99999999999)

    def __hash__(self):
        return self._hash

    def repr(self,root):
        item=root.get.single(*self.itree_item_path)
        return 'Birthday %s (%s) [%s]'%(self.person,str(self.year),get_iso_date(item))

    def get_init_args(self):
        return self.itree_item_path,self.person,self.year

class DateStart():
    def __init__(self,title,description):
        self.title=title
        self.description=description
        self.itree_item_path = None
        self.end_object=None
        self.alarms=[]
        self._hash = random.randint(0, 99999999999)

    def __hash__(self):
        return self._hash

    def repr(self,root):
        item=root.get.single(*self.itree_item_path)
        return 'Date (Start) %s: %s [%s]'%(self.title,self.description,get_iso_date(item))

    def get_init_args(self):
        return self.itree_item_path,self.title,self.description

class DateEnd():
    def __init__(self,itree_item_path,start_object):
        self.itree_item_path=itree_item_path
        self.date_object=start_object
        self._hash = random.randint(0, 99999999999)

    def __hash__(self):
        return self._hash

    def repr(self,root):
        item=root.get.single(*self.itree_item_path)
        return 'Date (End) %s: %s [%s]'%(self.date_object.title,self.date_object.description,get_iso_date(item))


class Alarm():
    def __init__(self,itree_item_path,object):
        self.itree_item_path=itree_item_path
        self.date_object=object
        self._hash = random.randint(0, 99999999999)

    def __hash__(self):
        return self._hash

    def repr(self,root):
        item=root.get.single(*self.itree_item_path)
        if type(self.date_object) is Birthday:
            return 'Alarm %s (%s) [%s]' % (self.date_object.person, str(self.date_object.year), get_iso_date(item))
        else:
            return 'Alarm %s: %s [%s]'%(self.date_object.title,self.date_object.description,get_iso_date(item))

    def get_init_args(self):
        return self.itree_item_path

class DateTarget():
    
    def __init__(self,year,month=None,day=None,hour=None,minute=None):
        self.year=year
        self.month=month
        self.day=day
        self.hour=hour
        self.minute=minute
        index_path=[{year}]
        if month:
            index_path.append(month-1)
            if day:
                index_path.append(day - 1)
                if hour:
                    index_path.append(hour)
                    if minute:
                        index_path.append(minute)
        self.idx_path=index_path


class Calendar():
    
    def __init__(self,years):
        self.calendar_tree=iTree('CALENDAR')
        self.build_years(years)

    def build_years(self, years):
        root=self.calendar_tree
        for year in years:
            print('Construct year: %i' % year)
            i = -1
            for i, y in enumerate(root):
                if y.tag == year:
                    print('The year; %s exists already in the calendar' % str(year))
                    return root[year]
                elif y.tag > year:
                    break
            if i == -1:
                year_item = root.append(iTree(year))
            else:
               year_item = root.insert(i, iTree(year))
            # month
            days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            # leap_year?
            if year % 4 == 0:
                if year % 100 == 0:
                    if year % 400 == 0:
                        days[1] += 1
                else:
                    days[1] += 1

            dt = datetime.date(year, 1, 1)
            first_weekday_year = dt.strftime("%A")
            if first_weekday_year=='Monday':
                cw = 0
            else:
                cw=1

            week_days = deque(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
            i = week_days.index(first_weekday_year)
            week_days.rotate(i)
            for i, m in enumerate(['January', 'February', 'March', 'April', 'May',
                                   'June', 'July', 'August', 'September', 'October', 'November', 'December']):
                print('Construct month: %s' % str((m, year)))
                month = year_item.append(iTree(m))
                # days
                for i in range(days[i]):
                    day_name=week_days[0]
                    if  day_name == 'Monday':
                        cw += 1
                    day = month.append(iTree(cw))
                    day.set_coupled_object(day_name)
                    week_days.rotate(-1)
                    # here we add hours,minutes:
                    day.extend([iTree(i,
                                      subtree=[iTree(i) for i in range(60)]  # minutes
                                      ) for i in range(24)])  # hours

    def insert_date(self,start_date_target,end_date_target,title,description=''):
        start=DateStart(title,description)
        start.itree_item_path=start_date_target.idx_path
        end=DateEnd(end_date_target.idx_path,start)
        start.end_object=end
        start_item=self.calendar_tree.get.single(*start_date_target.idx_path)
        if start_item.value is NoValue:
            start_item.set_value({start})
        else:
            start_item.value.add(start)
        #print('Date inserted at %s'%str(start_item.key_path))
        end_item = self.calendar_tree.get.single(*end_date_target.idx_path)
        if end_item.value is NoValue:
            end_item.set_value({end})
        else:
            end_item.value.add(end)
        #print('End inserted at %s' % str(end_item.key_path))
        return start

    def insert_alarm(self,date_target,date_object):
        alarm=Alarm(date_target.idx_path,date_object)
        date_object.alarms.append(alarm)
        item=self.calendar_tree.get.single(*date_target.idx_path)
        if item.value is NoValue:
            item.set_value({alarm})
        else:
            item.value.add(alarm)
        #print('Alarm inserted at %s'%str(item.idx_path))
        return alarm

    def insert_birthday(self,date_target,person,year):
        birthday=Birthday(person,year)
        birthday.itree_item_path=idx_path=date_target.idx_path
        item=self.calendar_tree.get.single(*idx_path)
        day_index=item.idx_path[1:]
        for year in item.root:
            year_item=year.get(*day_index)
            if year_item.value is NoValue:
                year_item.set_value({birthday})
            else:
                year_item.value.add(birthday)
        #print('Birthday inserted at %s'%str(item.idx_path))
        return birthday

    def del_date(self,date_object):
        item = self.calendar_tree.get.single(*date_object.itree_item_path)
        if type(date_object) is Alarm:
            item.value.remove(date_object)
            date_object.date_object.alarms.remove(date_object)
            #print('Alarm deleted at %s' % str(item.idx_path))
        if type(date_object) is DateEnd:
            date_object=date_object.date_object
            item = self.calendar_tree.get.single(*date_object.itree_item_path)
        item.value.remove(date_object)
        #print('Date deleted at %s' % str(item.idx_path))
        for alarm in date_object.alarms:
            alarm_item=self.calendar_tree.get.single(*alarm.itree_item_path)
            alarm_item.value.remove(alarm)
            #print('Alarm deleted at %s' % str(alarm_item.idx_path))
        if type(date_object) is DateStart:
            end_itree_item=self.calendar_tree.get.single(*date_object.end_object.itree_item_path)
            end_itree_item.value.remove(date_object.end_object)
            #print('Date end deleted at %s' % str(end_itree_item.idx_path))
        if type(date_object) is Birthday:
            day_index = date_object.itree_item_path[1:]
            year=date_object.itree_item_path[0]
            for year_item in self.calendar_tree:
                if year.tag==year:
                    continue
                sub_item=year_item.get(*day_index)
                sub_item.value.remove(date_object)
                #print('Birthday entry deleted in year %s' % str(year))




if __name__ == '__main__':
    """
    During the execution of the module we build an itertree and we fill the iTree objects with the data module and in a 
    second step with the data values. Some exceptions are generated for non matching values and the formatted string 
    representation of the data model is printed out
    """
    print('Run itertree calendar_example.py example')
    print('Build the calendar structure')

    YEARS=[2022,2023,2024]
    NUMBER_OF_BIRTHDAYS=100
    NUMBER_OF_30MIN_DATES = 10000
    NUMBER_OF_90MIN_DATES = 10000


    calendar=Calendar(YEARS)
    print('The calendar contains %i time-points' % len(calendar.calendar_tree.deep))
    # now we fill the calendar with alot of dates

    # Birthdays with alarms

    for i in range(NUMBER_OF_BIRTHDAYS):
        person='Person%i'%i
        birth_year=1900+1
        year=YEARS[random.randint(0,2)]
        month=random.randint(1,12)
        if month==2:
            day = random.randint(1, 28)
        else:
            day = random.randint(1, 30)
        c_item=calendar.insert_birthday(DateTarget(year, month, day), person, birth_year)
        alarm_day=day-1
        if alarm_day>0:
            calendar.insert_alarm(DateTarget(year, month, alarm_day),c_item)
    print('Calendar filled with %i randomly placed birthdays' % NUMBER_OF_BIRTHDAYS)

    # Fill 30 min dates
    for i in range(NUMBER_OF_30MIN_DATES):
        title = '30min date %i' % i
        description = '30min date'
        year = random.randint(2022, 2024)
        month = random.randint(1, 12)
        if month == 2:
            day = random.randint(1, 27)
        else:
            day = random.randint(1, 29)
        hour=random.randint(1, 23)
        minute=random.randint(0, 59)
        until=minute+30
        until_hour=hour
        until_day=day
        if until>59:
            until=until-59
            until_hour+=1
            if until_hour>23:
                until_hour-=23
                until_day=until_day+1
                # To make it easier we do not put dates on last day of the month
        if hour>1:
            alarm_hour = hour - 1
        else:
            alarm_hour=hour

        #print('Create entry:',year, month, day,hour,minute,'until:',until_day,until_hour,until )

        c_item = calendar.insert_date(DateTarget(year, month, day,hour,minute),
                                      DateTarget(year, month, until_day, until_hour, until),
                                      title, description)
        calendar.insert_alarm(DateTarget(year, month, day,alarm_hour,minute), c_item)

    print('Calendar filled with %i randomly placed 30min dates' % NUMBER_OF_30MIN_DATES)


    # Fill 1:30 min dates
    for i in range(NUMBER_OF_90MIN_DATES):
        title = '30min date %i' % i
        description = '30min date'
        year = random.randint(2022, 2024)
        month = random.randint(1, 12)
        if month == 2:
            day = random.randint(1, 27)
        else:
            day = random.randint(1, 29)
        hour=random.randint(1, 23)
        minute=random.randint(0, 59)
        until=minute+30
        until_hour=hour+1
        until_day=day
        if until>59:
            until=until-59
            until_hour+=1
        if until_hour>23:
            until_hour-=23
            until_day=until_day+1
            # To make it easier we do not put dates on last day of the month
        if hour>1:
            alarm_hour = hour - 1
        else:
            alarm_hour=hour

        #print('Create entry:',year, month, day,hour,minute,'until:',until_day,until_hour,until )

        c_item = calendar.insert_date(DateTarget(year, month, day,hour,minute),
                                      DateTarget(year, month, until_day, until_hour, until),
                                      title, description)
        calendar.insert_alarm(DateTarget(year, month, day,alarm_hour,minute), c_item)



    print('Calendar filled with %i randomly placed 90min dates' % NUMBER_OF_90MIN_DATES)


    # We do some analysis
    print('The calendar contains %i calendar entries '
          '(start and end points counted separately)' % sum(1 for _ in
                                                          filter(lambda i: i.value!=NoValue,
                                                                 calendar.calendar_tree.deep)))
    print('The calendar contains %i calendar alarm entries'
          % sum(i.value!=NoValue and sum(1 for ii in i.value if type(ii) is Alarm)
               for i in filter(lambda i: i.level==5, calendar.calendar_tree.deep)))


    print('The calendar contains %i calendar entries '
          "at night time in (between 20-6 o'clock)" % sum(1 for _ in
                                            filter(lambda i: i[1].value!=NoValue and len(i[0])==5 and (i[0][-2]>20 or i[0][-2]<6),
                                                   calendar.calendar_tree.deep.idx_paths())))


    # Here we use a hierarchical filtering to get the days only out (we skip hours and minutes in the iteration)
    iterator=calendar.calendar_tree.get.single({2022}).deep.iter(lambda i: i.level < 4)
    counts=[0]*6
    for i in iterator:
        cnt=0
        if i.value is NoValue:
            counts[0] += 1
            continue
        for ii in i.value:
            if type(ii) is Birthday:
                cnt += 1
        counts[cnt]+=1
    print('We have the following statistic related to birthday '
          'occurrences:\n%s'%''.join(['- %i times on %i days\n'%(b,c) for b,c in enumerate(counts)])[:-1])

    CW=5
    print('\nAnalysis of  CW%i/2023:'%CW)
    cw_items=calendar.calendar_tree.get({2023}, iter, {CW}) # give build-in Ellipsis to target all children in a specific level
    for day_item in cw_items:
        print('DAY: Year: %i Month: %s (%i); CW: %i; Day: %i (%s):'%(
            day_item.parent.parent.tag,
            day_item.parent.tag,
            day_item.parent.idx,
            day_item.tag,
            day_item.idx,
            day_item.coupled_object))
        if day_item.value != NoValue:
            print('- Birthdays:')
            alarms=[]
            for i,ii in enumerate(day_item.value):
                if type(ii) is Birthday:
                    print('  * %s'%(ii.repr(calendar.calendar_tree)))
                else:
                    alarms.append(ii)
            if alarms:
                print('- Birthday Alarms:')
                for i,ii in enumerate(alarms):
                    print('  * %s' % ( ii.repr(calendar.calendar_tree)))

        i=1
        for minutes in filter(lambda i: i.level==5, day_item.deep):
            if minutes.value != NoValue:
                if i==1:
                    print('- Dates/Alarms:')
                for ii in minutes.value:
                    print('  * %i. %s' % (i, ii.repr(calendar.calendar_tree)))
                    i+=1

    day_item=calendar.calendar_tree.get.single({2023},10,1)
    print('\nAnalysis of %s:' % get_iso_date(day_item))
    if day_item.value != NoValue:
        print('- Birthdays:')
        alarms = []
        for i, ii in enumerate(day_item.value):
            if type(ii) is Birthday:
                print('  * %s' % (ii.repr(calendar.calendar_tree)))
            else:
                alarms.append(ii)
        if alarms:
            print('- Birthday Alarms:')
            for i, ii in enumerate(alarms):
                print('  * %s' % (ii.repr(calendar.calendar_tree)))

    i = 1
    for minutes in filter(lambda i: i.level == 5, day_item.deep):
        if minutes.value != NoValue:
            if i == 1:
                print('- Dates/Alarms:')
            for ii in minutes.value:
                print('  * %i. %s' % (i, ii.repr(calendar.calendar_tree)))
                i += 1
    print('Delete last date')
    calendar.del_date(ii)
    print('Dates after delete:')
    i=1
    for minutes in filter(lambda i: i.level == 5, day_item.deep):
        if minutes.value != NoValue:
            for ii in minutes.value:
                print('  * %i. %s' % (i, ii.repr(calendar.calendar_tree)))
                i += 1

    #calendar.render()



