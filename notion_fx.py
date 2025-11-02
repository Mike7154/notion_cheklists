import requests
import mlfiles
import datetime
import time
from dateutil import parser
from dateutil.tz import tzoffset

def get_headers(token = mlfiles.load_setting('notion','token')):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    return headers


def create_page(database_id, headers, properties):
    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {
            "database_id": database_id
        },
        "properties": properties
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def append_block(page_id, headers, data):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    cdata = {"children": [data]}
    response = requests.patch(url, headers=headers, json=cdata)
    return response.json()

def text_block(string, btype = "paragraph"):
   #btype can be "paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item"
    return {
        "object": "block",
        "type": btype,
        btype: {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": string
                    }
                }
            ]

        }
    }

def file_block(url, caption):
    return {
        "type": "file",
        "file": {
            "caption": [
                {
                    "type": "text",
                    "text": {
                        "content": caption
                    }
                }
            ],
            "type": "external",
            "external": {
                "url": url
            }
        }
    }

def link_block(url, caption):
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                  "type": "text",
                  "text": {
                    "content": caption,
                    "link": {"url": url}
                  },
                  "annotations": {
                    "bold": True
                  },
                  "plain_text": caption,
                  "href": url
                }
            ]

        }
    }



def h3_block(string):
    return text_block(string, "heading_3")

def h1_block(string):
    return text_block(string, "heading_1")

def h2_block(string):
    return text_block(string, "heading_2")

def update_page_icon(page_id, headers):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {
        "icon": {
            "type": "emoji",
            "emoji": "📧"
        }
    }
    response = requests.patch(url, headers=headers, data=data)
    return response.json()

def split_paragraph(paragraph):
    paragraphs = []
    while len(paragraph) > 2000:
        split_index = paragraph.rfind('\n', 0, 2000)
        if split_index == -1:
            # If there's no '\n' in the first 2000 characters, split at the 2000th character
            split_index = 2000
        paragraphs.append(paragraph[:split_index])
        # Skip past the '\n' character for the next paragraph
        paragraph = paragraph[split_index+1:]
    paragraphs.append(paragraph)  # Append the remainder of the paragraph
    return paragraphs



def get_pages(database_id, filters, headers, page_size=100, max_retries=5):
    """Fetch every page in a database, honoring pagination and rate limits."""

    all_results = []
    start_cursor = None

    while True:
        body = {"page_size": page_size}
        if filters:
            body["filter"] = filters
        if start_cursor:
            body["start_cursor"] = start_cursor

        retries = 0
        while True:
            response = requests.post(
                f"https://api.notion.com/v1/databases/{database_id}/query",
                headers=headers,
                json=body,
            )

            if response.status_code == 200:
                data = response.json()
                break

            if response.status_code == 429 and retries < max_retries:
                retry_after = response.headers.get("Retry-After")
                try:
                    wait_time = float(retry_after) if retry_after is not None else 1 + retries
                except ValueError:
                    wait_time = 1 + retries
                time.sleep(wait_time)
                retries += 1
                continue

            response.raise_for_status()

        all_results.extend(data["results"])

        if not data.get("has_more"):
            break

        start_cursor = data.get("next_cursor")

    return all_results


# define a function that takes a Notion property as an argument
def get_date_from_property(property, desired_timezone=tzoffset(None, -7*3600)):
    # check if the property type is date, rollup, or formula
    t = property["type"]
    if t in ["date", "rollup", "formula"]:
        # get the date object from the property
        if t == "date":
            date = property.get("date")
        else:
            date = property[t].get('date', None)
        # check if the date object is not None and has a start attribute
        if date and date.get("start"):
            # parse the start attribute as a datetime object with timezone
            date = parser.parse(date["start"])
            # If a desired timezone is provided, convert the date to that timezone
            if desired_timezone is not None:
                date = date.astimezone(desired_timezone)
            # return the date object with its original timezone or converted timezone
            return date
        else:
            # return None if the date object is None or has no start attribute
            return None
    else:
        # raise an exception if the property type is not valid
        raise ValueError(f"Invalid property type: {t}")




def get_date_object_from_datetime(datetime_obj):
    # Check if the argument is a valid datetime or date object
    if not isinstance(datetime_obj, (datetime.datetime, datetime.date)):
        raise TypeError(f"Invalid argument type: {type(datetime_obj)}")
    
    # Initialize date_string and time_zone
    date_string = None
    time_zone = None

    if isinstance(datetime_obj, datetime.datetime):
        # Handle timezone for datetime objects
        if datetime_obj.tzinfo is not None and datetime_obj.tzinfo.utcoffset(datetime_obj) is not None:
            time_zone = datetime_obj.tzinfo
        # Check if the time is midnight for datetime objects, and format accordingly
        if datetime_obj.time() == datetime.time(0, 0):
            date_string = datetime_obj.date().isoformat()
        else:
            date_string = datetime_obj.isoformat()
    else:
        # For date objects, directly use the isoformat
        date_string = datetime_obj.isoformat()

    # Create a date object for Notion with the start attribute and potential time_zone
    date_object = {
        "start": date_string,
        "end": None,
        "time_zone": time_zone
    }
    
    # Return the date object
    return date_object

# define a function that takes a list of datetime objects as an argument
def get_earliest_date(datetime_list):
    # Check if the argument is a valid list of datetime objects
    if not (isinstance(datetime_list, list) and all(isinstance(dt, datetime.datetime) for dt in datetime_list)):
        raise TypeError("Invalid argument type: {}".format(type(datetime_list)))

    # Convert all datetime objects to UTC for sorting, while keeping track of original offsets
    utc_datetime_list = []
    original_offsets = {}
    for dt in datetime_list:
        offset = dt.tzinfo.utcoffset(dt) if dt.tzinfo is not None else datetime.timedelta(0)
        original_offsets[dt] = offset
        utc_datetime = dt.astimezone(datetime.timezone.utc)
        utc_datetime_list.append(utc_datetime)

    # Sort the UTC datetime list
    sorted_utc_list = sorted(utc_datetime_list)
    
    # Find the original datetime object that corresponds to the earliest UTC datetime
    earliest_utc = sorted_utc_list[0]
    earliest_original = [dt for dt in datetime_list if dt.astimezone(datetime.timezone.utc) == earliest_utc][0]

    # Return the earliest date with its original offset
    original_offset = original_offsets[earliest_original]
    return earliest_original.replace(tzinfo=tzoffset(None, int(original_offset.total_seconds())))



# define a function that takes the page ID, the headers, the name of the date field, and the date object as arguments
def update_date_property(page_id, headers, date_field, date_object):
    # set the URL for the update page properties endpoint
    url = f"https://api.notion.com/v1/pages/{page_id}"

    # set the body for the request
    body = {
        "properties": {
            date_field: {
                "date": date_object
            }
        }
    }

    # make a patch request to the update page properties endpoint
    response = requests.patch(url, headers=headers, json=body)

    # check if the request was successful
    if response.status_code == 200:
        # print a success message
        print(f"Successfully updated {date_field} property")
    else:
        # print an error message
        print(f"Error: {response.status_code}")

def calculate_duration(date_obj):
    # Check if start time is provided
    if date_obj is None:
        return 0
    if 'start' in date_obj['date'] and date_obj['date']['start']:
        start_time = parser.parse(date_obj['date']['start'])
    else:
        raise ValueError("Start time is missing")
    end_time_str = date_obj['date'].get('end')
    if end_time_str:
        end_time = parser.parse(end_time_str)
    else:
        # If end time is None, return a duration of 0
        return 0
    # Calculate duration in minutes
    duration = (end_time - start_time).total_seconds() / 60
    return duration

def update_number_property(page_id, headers, number_field, number_value):
    # set the URL for the update page properties endpoint
    url = f"https://api.notion.com/v1/pages/{page_id}"

    # set the body for the request
    body = {
        "properties": {
            number_field: {
                "number": number_value
            }
        }
    }

    # make a patch request to the update page properties endpoint
    response = requests.patch(url, headers=headers, json=body)

    # check if the request was successful
    if response.status_code == 200:
        # print a success message
        print(f"Successfully updated {number_field} property")
    else:
        # print an error message
        print(f"Error: {response.status_code}")
 
def property_value(property):
    try:
        ptype = property['type']
        if ptype == 'select':
            return property[ptype]['name']
        if ptype == 'rich_text':
            return property[ptype][0]['plain_text']
    except Exception as e:
        return None
        