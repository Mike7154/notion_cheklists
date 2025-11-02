# Import necessary libraries
import notion_fx
import mlfiles
import mldates
from formulas import *



filter = {
    "property": "Status",
    "status": {
        "equals": "Active"
    }
}
settings = mlfiles.load_all_settings()
headers = notion_fx.get_headers()
# Fetch Notion pages based on the new filter
pages = notion_fx.get_pages(settings['notion']["checklist_db"],filter,headers)
# Update minimum date for each fetched page if its ID matches with the list of IDs
i = 0
for p in pages:
    try:
        print(p['properties']['Name']['title'])
        #print(p['properties']['People'])
        pr = p['properties']
        last_date_props = settings['notion']['last_date']
        last_dates = []
        for prop in last_date_props:
            l_date = pr[prop]
            l_date = notion_fx.get_date_from_property(l_date)
            if l_date:
                l_date = mldates.strip_time_from_datetime(l_date)
            last_dates.append(l_date)
        last_date = mldates.get_latest_date(last_dates)
        c_type = notion_fx.property_value(pr[settings['notion']['type']])
        c_unit = notion_fx.property_value(pr[settings['notion']['units']])
        c_number = notion_fx.property_value(pr[settings['notion']['number']])


        next_date = mldates.next_date_matching_list(c_number, c_unit, c_type, last_date)
        next_date = notion_fx.get_date_object_from_datetime(next_date[0])
        prev_value = pr[settings['notion']['next_date']]['date']
        print(last_date)
        print(prev_value)
        print(next_date)
        if prev_value != next_date:
            notion_fx.update_date_property(p['id'], headers, settings['notion']['next_date'], next_date)
            if settings['options']['use_scheduled']:
                notion_fx.update_date_property(p['id'], headers, settings['notion']['scheduled'], next_date)
            print("----------")
            print(last_date)
            print(c_type)
            print(c_unit)
            print(c_number)
            print(next_date)
            print(p)
            i = i + 1
    except Exception as e:
        print(f"An error occurred processing page {p['id']}: {e}")
        # Optionally, log the error details or take other actions
        continue  # Continue to the next page despite the error
print(i)
print("updated")