import datetime
import math
import calendar

def get_next_last_weekday_of_month(year, month, weekday):
    """
    Finds the last occurrence of a specific weekday (e.g., Sunday) in a given month and year.
    """
    # Increment the month to get the first day of the next month
    if month == 12:  # If December, move to January of the next year
        next_month_year = year + 1
        next_month = 1
    else:
        next_month_year = year
        next_month = month + 1

    # The first day of the next month
    first_day_next_month = datetime.date(next_month_year, next_month, 1)

    # Subtract one day to get the last day of the target month
    last_day_of_month = first_day_next_month - datetime.timedelta(days=1)

    # Calculate how many days to subtract to get the last occurrence of the weekday
    days_to_subtract = (last_day_of_month.weekday() - weekday + 7) % 7
    last_weekday_of_month = last_day_of_month - datetime.timedelta(days=days_to_subtract)

    return last_weekday_of_month



def get_last_weekday_of_month(year, month, weekday):
    date = datetime.date(year, month, 1)
    while True:
        next_last_weekday = get_next_last_weekday(date, weekday)
        if next_last_weekday.month != month:
            return next_last_weekday
        date = next_last_weekday + datetime.timedelta(days=1)

# A function that takes a date and finds
#the next date that is then nth day of
#the week of the mth weekofthe oth
#monthofthe quarter
def calculate_next_quarter_start(date):
    # Increment the month until reaching a new quarter
    new_month = date.month
    while new_month <= date.month:
        new_month += 1
        if new_month > 12:  # Reset month to January and increment year if we've passed December
            new_month = 1
            date = date.replace(year=date.year + 1)
        # Check if the new month is at the start of a new quarter
        if new_month in [1, 4, 7, 10]:
            break
    return date.replace(month=new_month, day=1)

def next_quarterly_mwd(date, nth_weekday, nth_week, nth_month):
    # Define quarter start months
    quarter_start = {1: 1, 2: 4, 3: 7, 4: 10}
    # Extract year and month from the given date to determine the quarter
    year, month = date.year, date.month

    # Determine the quarter of the given date
    quarter = math.ceil(month / 3)

    # Adjust for the 'nth_month' within the quarter
    if nth_month == 0:  # If 'nth_month' is 0, target the last month of the quarter
        nth_month = 3
    target_month = quarter_start[quarter] + nth_month - 1

    # Adjust the year and target_month for the calculation
    if target_month > 12:
        target_month -= 12
        year += 1

    # Set 'nth_weekday' to 7 (Sunday) if it's 0
    nth_weekday = 7 if nth_weekday == 0 else nth_weekday

    # Calculate the first day of the target month
    target_date = datetime.date(year, target_month, 1)

    # Find the correct day and week within the month
    days_to_add = (nth_weekday - target_date.isoweekday() + 7) % 7
    target_day = target_date + datetime.timedelta(days=days_to_add)
    if nth_week > 1:  # Adjust for weeks beyond the first
        target_day += datetime.timedelta(weeks=nth_week - 1)
    elif nth_week == 0:  # Find the last occurrence of the day in the month
        while (target_day + datetime.timedelta(weeks=1)).month == target_month:
            target_day += datetime.timedelta(weeks=1)

    # If the calculated date is before the input date, find the next quarter
    if target_day <= date:
        next_quarter_start_month = (quarter % 4) * 3 + 1
        if next_quarter_start_month <= month:
            year += 1
        next_quarter_date = datetime.date(year, next_quarter_start_month, 1)
        # Recursively call the function with the new date
        return next_quarterly_mwd(next_quarter_date, nth_weekday, nth_week, nth_month)
    else:
        return target_day

def get_last_day_of_month(year, month):
    """Return the last day of the given month."""
    next_month = month % 12 + 1
    next_month_first_day = datetime.date(year if month < 12 else year + 1, next_month, 1)
    last_day_of_month = next_month_first_day - datetime.timedelta(days=1)
    return last_day_of_month

def next_quarterly_md(from_date, day, month):
    year = from_date.year
    # Find the current quarter of the from_date
    current_quarter = math.ceil(from_date.month / 3.0)
    target_month = (current_quarter - 1) * 3 + month

    # Adjust for year and month if the target month is less than the current month
    if target_month < from_date.month or (target_month == from_date.month and day != 0 and day <= from_date.day):
        target_month += 3  # Move to the next quarter
        if target_month > 12:  # Adjust for the next year
            target_month -= 12
            year += 1

    # If day is 0, find the last day of the target month
    if day == 0:
        target_date = get_last_day_of_month(year, target_month)
    else:
        # Try to create the target date
        try:
            target_date = datetime.date(year, target_month, day)
        except ValueError:
            # If the day is invalid for the month, fallback to the last day of the month
            target_date = get_last_day_of_month(year, target_month)

    # Ensure the target date is after the from_date
    if target_date <= from_date:
        # Recursively call the function with an updated from_date to ensure we get a future date
        from_date += datetime.timedelta(days=1)  # Move from_date to the next day for recursion
        return next_quarterly_md(from_date, day, (month % 3) + 1)
    else:
        return target_date




# A function that finds
#the next date that is then th day of
#the week of them th weekofthe oth
#monthofthe year
def next_yearly_mwd(date, day, week, month):
    year = date.year
    if month == 0:
        month = 12

    # Adjust the day for calculation
    day = day % 7 or 7

    if week == 0:
        # Use the improved function to find the last occurrence of the weekday in the month
        result_date = get_next_last_weekday_of_month(year, month, day - 1)  # Adjust day for 0-based weekday
    else:
        # Calculate the date for other weeks as before
        start_date = datetime.date(year, month, 1)
        weekday_of_first = start_date.isoweekday()
        days_to_first_desired_day = (day - weekday_of_first) % 7
        first_desired_day = start_date + datetime.timedelta(days=days_to_first_desired_day)
        result_date = first_desired_day + datetime.timedelta(weeks=week - 1)

    # If the result is earlier than the input date, look for the next occurrence in the next year
    if result_date < date:
        # Increment the year for the next recursive call
        return next_yearly_mwd(datetime.date(year + 1, month, 1), day, week, month)
    else:
        return result_date

def get_next_weekday(date, weekday):
    days_until_weekday = (weekday - (date.weekday()+3)) % 7
    return date + datetime.timedelta(days=days_until_weekday)

def get_nth_weekday_of_month(date, weekday, n):
    first_day_of_month = date.replace(day=1)
    offset = (weekday - (first_day_of_month.weekday()+1)) % 7
    nth_weekday = first_day_of_month + datetime.timedelta(days=offset + (n - 1) * 7)
    return nth_weekday

def get_next_monthly_wd(date, weekday, nth_week):
    result_date = get_nth_weekday_of_month(date, weekday, nth_week)
     # Check if this date is after or equaltothegiven date
    
    if result_date >= date:
        # Return this date as theresult
        return result_date
    else:
        next_month = result_date.replace(month = result_date.month + 1)
        # Add one month to gettothenextyear
        result_date = get_nth_weekday_of_month(next_month, weekday, nth_week)
        # Repeat steps4to9with thenewdate
        return result_date


def last_day_of_week(year, weekday):
    # A function that returns the date of the last given day of the week for the current year
    # weekday: an integer from 0 (Monday) to 6 (Sunday)
    
    # Get the last day of the year
    last_day = datetime.date(year, 12, 31)
    
    # Get the weekday of the last day of the year
    last_weekday = last_day.weekday() + 1
    
    # Calculate the difference between the desired weekday and the last weekday
    diff = last_weekday - weekday
    
    # Adjust the difference if it is negative or zero
    if diff < 0:
        diff += 7
    
    if diff >= 7:
        diff -= 7
    
    # Subtract the difference from the last day to get the last given day of the week
    return last_day - datetime.timedelta(days=diff)


def nth_weekday(year, weekday, n):
    """
    Gets the nth occurrence of a specific weekday in each month of the specified year.
    
    Parameters:
    - year: The year as an integer.
    - n: The nth occurrence of the weekday in the month.
    - weekday: The day of the week as an integer, where 0=Sunday, 1=Monday, ..., 6=Saturday.
    
    Returns:
    A list of datetime.date objects representing the nth occurrence of the specified weekday in each month of the year.
    """
    # Adjust weekday to match Python's datetime.weekday() where Monday=0, ..., Sunday=6
    if weekday == 0:
        weekday = 6  # Adjust for Sunday
    else:
        weekday -= 1  # Adjust for other days to align with datetime.weekday()
    
    nth_occurrences = []
    
    for month in range(1, 13):  # Iterate through all months
        first_day_of_month = datetime.date(year, month, 1)
        # Find the weekday of the first day of the month
        first_day_weekday = first_day_of_month.weekday()
        
        # Calculate the difference to get to the first occurrence of the specified weekday
        days_to_first_occurrence = (weekday - first_day_weekday + 7) % 7
        
        # Calculate the date of the nth occurrence
        nth_occurrence = first_day_of_month + datetime.timedelta(days=days_to_first_occurrence + (n-1)*7)
        
        # Check if the nth occurrence is within the same month
        if nth_occurrence.month == month:
            nth_occurrences.append(nth_occurrence)
        else:
            # If the nth occurrence falls into the next month, it means there is no nth occurrence in the current month
            break  # Or handle accordingly
    
    return nth_occurrences
def nth_day(year, n):
    # A function that returns the date of the nth day of the current year
    # n: an integer from 1 to 365 or 366
    
    
    # Get the first day of the year
    first_day = datetime.date(year, 1, 1)
    
    # Add (n-1) days to the first day to get the nth day
    return first_day + datetime.timedelta(days=n-1)

def get_nth_day_of_quarter(date, n):
    # get the current year and quarter
    year = date.year
    quarter = (date.month - 1) // 3 + 1
    
    # get the first month of the current quarter
    first_month_of_quarter = 3 * quarter - 2
    
    # get the first day of the current quarter
    qstart = datetime.date(year, first_month_of_quarter, 1)
    
    # add n - 1 days to get the nth day of the quarter
    qnth = qstart + datetime.timedelta(days = n - 1)
    
    # if the nth day is before or equal to the given date, move to the next quarter
    if qnth <= date:
        # if the current quarter is the last one, move to the next year
        if quarter == 4:
            year += 1
            quarter = 1
        else:
            # otherwise, increment the quarter by one
            quarter += 1
        
        # get the first month of the next quarter
        first_month_of_quarter = 3 * quarter - 2
        
        # get the first day of the next quarter
        qstart = datetime.date(year, first_month_of_quarter, 1)
        
        # add n - 1 days to get the nth day of the next quarter
        qnth = qstart + datetime.timedelta(days = n - 1)
    
    # return the next date that is the nth day of a quarter
    return qnth


def get_next_nth_weekday_of_month(date, n, weekday):
    # get the current year and month
    year = date.year
    month = date.month
    
    # get the first day of the current month
    first_day = datetime.date(year, month, 1)
    
    # get the first weekday of the current month
    first_weekday = first_day.isoweekday()
    
    # calculate the offset to get the first occurrence of the given weekday
    offset = (weekday - first_weekday) % 7
    
    # add n - 1 weeks to get the nth occurrence of the given weekday
    nth_weekday = first_day + datetime.timedelta(days = offset + (n - 1) * 7)
    
    # if the nth weekday is before or equal to the given date, move to the next month
    if nth_weekday <= date:
        # if the current month is December, move to the next year
        if month == 12:
            year += 1
            month = 1
        else:
            # otherwise, increment the month by one
            month += 1
        
        # get the first day of the next month
        first_day = datetime.date(year, month, 1)
        
        # get the first weekday of the next month
        first_weekday = first_day.isoweekday()
        
        # calculate the offset to get the first occurrence of the given weekday
        offset = (weekday - first_weekday) % 7
        
        # add n - 1 weeks to get the nth occurrence of the given weekday
        nth_weekday = first_day + datetime.timedelta(days = offset + (n - 1) * 7)
    
    # return the next day that is the nth weekday of a month
    return nth_weekday

def get_next_nth_day_of_month(date, n):
    # get the current year and month
    year = date.year
    month = date.month
    
    # get the number of days in the current month
    days_in_month = calendar.monthrange(year, month)[1]
    
    # if n is 0, use the number of days in the month as n
    if n == 0:
        n = days_in_month
    
    # if n is larger than the number of days in the month, return None
    if n > days_in_month:
        n = days_in_month
    
    # get the nth day of the current month
    nth_day = datetime.date(year, month, n)
    
    # if the nth day is before or equal to the given date, move to the next month
    if nth_day < date:
        # if the current month is December, move to the next year
        if month == 12:
            year += 1
            month = 1
        else:
            # otherwise, increment the month by one
            month += 1
        
        # get the number of days in the next month
        days_in_month = calendar.monthrange(year, month)[1]
        
        # if n is 0, use the number of days in the month as n
        if n == 0:
            n = days_in_month
        
        # if n is larger than the number of days in the next month, return None
        if n > days_in_month:
            return None
        
        # get the nth day of the next month
        nth_day = datetime.date(year, month, n)
    
    # return the next date that is the nth day of a month
    return nth_day

def get_next_date_by_weekday(date, weekday):
    # Convert Sunday from 0 to 7 to match Python's datetime.isoweekday() convention
    if weekday == 0:
        weekday = 7
    
    # get the current weekday of the date, adjusting because isoweekday() returns 1 for Monday and 7 for Sunday
    current_weekday = date.isoweekday()
    
    # Calculate the difference; if the target weekday is less than or equal to the current weekday, adjust by adding 7
    diff = (weekday - current_weekday) % 7
    if diff == 0:
        diff = 7  # Ensure the next date is always in the future
    
    # add the difference to the date to get the next date that matches the given weekday
    next_date = date + datetime.timedelta(days=diff)
    
    # return the next date
    return next_date




def next_date_matching_pattern(from_date, day_pattern, pattern, interval):
    #print(day_pattern)
    if interval == "Yearly":
        year = from_date.year
        if pattern == "Month-Day":
            # Parse the day as a month and a day
            month, day = map(int, day_pattern.split("-"))
            # Get the year of the from_date
            
            # Create a new date object with the same month and day as the day parameter
            next_date = datetime.date(year, month, day)
            
        
        if pattern == "Month-Week-Day":
            month, week, day = map(int, day_pattern.split("-"))
            next_date = next_yearly_mwd(from_date, day, week, month)
            return next_date
        if pattern == "Month":
            month = int(day_pattern)
            day = 1
            next_date = datetime.date(year, month, day)
            return next_date
            
        if pattern == "Week":
            week = int(day_pattern)
            next_date = nth_weekday(year, week, 0)
            return next_date
        
        if pattern == "Week-Day":
            week, day = map(int, day_pattern.split("-"))
            next_date = nth_weekday(year, week, day)
            if next_date < from_date:
                next_date = nth_weekday(year+1, week, day)

        if pattern == "Day":
            day = int(day_pattern)
            next_date = nth_day(year,day)
            if next_date < from_date:
                next_date = nth_day(year + 1, day)
        
        if next_date < from_date:
            next_date = next_date.replace(year=year + 1)
        return next_date
    
    if interval == "Quarterly":
        if pattern == "Month-Week-Day":
            month, week, day = map(int, day_pattern.split("-"))
            next_date = next_quarterly_mwd(from_date, day, week, month)
            return next_date
        if pattern == "Month-Day":
            month, day = map(int, day_pattern.split("-"))
            next_date = next_quarterly_md(from_date, day, month)
            return next_date
        if pattern == "Day":           
            day = int(day_pattern)
            if day == 0:
                day = 1
                last = True
            else:
                last = False
            next_date = get_nth_day_of_quarter(from_date, day)
            if last:
                next_date = next_date - datetime.timedelta(days = 1)    
        else:
            next_date = get_nth_day_of_quarter(from_date, 1)
        return next_date
    if interval == "Monthly":
        if pattern == "Week-Day":
            week, day = map(int, day_pattern.split("-"))
            if week == 0:
                tomrrow = from_date + datetime.timedelta(days = 1)
                first_wd = get_next_monthly_wd(tomrrow, day, 1)
                next_date = first_wd - datetime.timedelta(days = 7)
                return next_date
            next_date = get_next_monthly_wd(from_date, day, week)
            return next_date
        if pattern == "Day":
            day = int(day_pattern)
            next_date = get_next_nth_day_of_month(from_date,day)
            return next_date
        else:
            next_date = get_next_nth_day_of_month(from_date,1)
            return next_date
    if interval == "Weekly":
        if pattern == "Day":
            day = int(day_pattern)
            next_date = get_next_date_by_weekday(from_date, day)
            return next_date
        else:
            next_date = get_next_date_by_weekday(from_date, 0)
            return next_date
    elif interval == "Interval":
        # New interval handling based on 'Day', 'Week', or 'Month'
        increment = int(day_pattern)  # Convert day_pattern to an integer
        if pattern == "Day":
            next_date = from_date + datetime.timedelta(days=increment)
        elif pattern == "Week":
            next_date = from_date + datetime.timedelta(weeks=increment)
        elif pattern == "Month":
            # For months, since timedelta doesn't support months, manually calculate the new date
            new_month = from_date.month + increment - 1  # -1 since month indices start at 1
            new_year = from_date.year + new_month // 12
            new_month = new_month % 12 + 1
            try:
                next_date = from_date.replace(year=new_year, month=new_month)
            except ValueError:
                # Handle day out of range for month (e.g., February 30)
                # Roll over to the first day of the next month
                next_date = from_date.replace(year=new_year, month=new_month + 1, day=1)
        return next_date
    elif interval == "Daily":
        next_date = from_date + datetime.timedelta(days=1)
        return next_date
    else:
        next_date = from_date
    return next_date


def next_date_matching_list(day_list, pattern, interval, from_date = datetime.date.today()):
    if day_list:
        word_list = day_list.split(",")
    else:
        word_list = ["1"]
    result_list = [next_date_matching_pattern(from_date,day_pattern, pattern, interval) for day_pattern in word_list]
    return sorted(result_list)

def check_dates(date_list, d):
    # Convert the current date and time to a date object
    today = datetime.datetime.now().date()

    # Add 7 days to the current date using timedelta
    seven_days_later = today + datetime.timedelta(days=d)

    # Loop through the date list and compare each date with seven_days_later
    for date in date_list:
        # Convert the date string to a date object
        date_obj = date
        
        # Check if the date is later than seven_days_later
        if date_obj > seven_days_later:
            return True # Return True as soon as one date is found
    
    return False # Return False if no date is found

def all_dates_matching_lsit(day_list, pattern, interval, days = 7, from_date = datetime.date.today()):
    total_list = []
    cont = True
    start_date = from_date
    while cont == True:
        total_list.extend(next_date_matching_list(day_list, pattern, interval, start_date))
        start_date = start_date + datetime.timedelta(days=1)
        if check_dates(total_list, days):
            cont = False
    date_set = set(total_list)
    date_list = list(date_set)
    date_list = sorted(date_list)
    return date_list

def strip_time_from_datetime(datetime_input):
    """
    Strips the time from a datetime string or datetime object and returns it as a date object.

    Args:
    datetime_input (str or datetime.datetime): A datetime string in ISO format or a datetime object.

    Returns:
    datetime.date: A date object representing the date part of the input.
    """
    # Check if the input is a string and parse it into a datetime object
    if isinstance(datetime_input, str):
        datetime_obj = datetime.datetime.fromisoformat(datetime_input)
    elif isinstance(datetime_input, datetime.datetime):
        datetime_obj = datetime_input
    else:
        raise ValueError("Input must be a string or datetime.datetime object")
    
    # Extract and return the date part of the datetime object
    return datetime_obj.date()

def get_latest_date(datetime_list):
    # Filter out None values
    filtered_datetime_list = [dt for dt in datetime_list if dt is not None]

    # Check if the filtered list is empty
    if not filtered_datetime_list:
        return None  # Or raise an exception, depending on desired behavior

    # Check if the argument contains valid date or datetime objects
    if not all(isinstance(dt, (datetime.datetime, datetime.date)) for dt in filtered_datetime_list):
        raise TypeError("List must contain datetime.date or datetime.datetime objects")

    # Since datetime.date objects don't have timezone info, we convert all to datetime.datetime at midnight in UTC
    utc_datetime_list = [
        datetime.datetime(dt.year, dt.month, dt.day, tzinfo=datetime.timezone.utc)
        if isinstance(dt, datetime.date) else dt.astimezone(datetime.timezone.utc)
        for dt in filtered_datetime_list
    ]

    # Sort the UTC datetime list
    sorted_utc_list = sorted(utc_datetime_list)

    # The latest datetime object
    latest_utc = sorted_utc_list[-1]

    # If the original was a date object, return it as such, otherwise return the datetime object
    latest_original_index = utc_datetime_list.index(latest_utc)
    latest_original = filtered_datetime_list[latest_original_index]

    return latest_original