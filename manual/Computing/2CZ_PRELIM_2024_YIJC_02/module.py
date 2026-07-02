from datetime import *

def convert(string):              #string: date in 'yyyy/mm/dd' format
    return datetime.strptime(string, '%Y/%m/%d').date()

def expirydate(string):           #string: date in 'yyyy/mm/dd' format
    now = convert(string)
    four_weeks = timedelta(weeks=4)
    later = now + four_weeks
    return later
