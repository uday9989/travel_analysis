#!/usr/bin/env python
# coding: utf-8

# In[10]:


import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import os

# Path to OneDrive folder where files are stored
one_drive_path = "C:/Users/YourUsername/OneDrive/Desktop/edurekha project/1st mini project"

# Check if the path is accessible
if os.path.exists(one_drive_path) and os.access(one_drive_path, os.R_OK | os.W_OK):
    print("OneDrive folder is accessible with read and write permissions.")
else:
    print("Permission denied or path not accessible. Check OneDrive sync and permissions.")

# Load files if accessible
bookings_file = os.path.join(one_drive_path, "Bookings.csv")
sessions_file = os.path.join(one_drive_path, "Sessions.csv")

# Additional code to load and analyze the data

# Define the file paths
bookings_file = "C:/Users/YourUsername/Documents/Bookings.csv"  # Update this path
sessions_file = "C:/Users/YourUsername/Documents/Sessions.csv"  # Update this path

# Function to check file access permissions
def check_file_access(filepath):
    if os.path.exists(filepath):
        if os.access(filepath, os.R_OK):
            print(f"File '{filepath}' is accessible and ready to load.")
            return True
        else:
            print(f"Permission denied: Unable to read '{filepath}'.")
            return False
    else:
        print(f"File not found: '{filepath}' does not exist.")
        return False

# Check access to both files
if check_file_access(bookings_file) and check_file_access(sessions_file):
    try:
        # Load datasets
        bookings = pd.read_csv(bookings_file)
        sessions = pd.read_csv(sessions_file)

        # 1. Number of distinct bookings, sessions, and searches
        distinct_bookings = bookings["booking_id"].nunique()
        distinct_sessions = sessions["session_id"].nunique()
        distinct_searches = sessions["search_id"].nunique()
        print("Distinct bookings:", distinct_bookings)
        print("Distinct sessions:", distinct_sessions)
        print("Distinct searches:", distinct_searches)

        # 2. Sessions with more than one booking
        sessions_with_bookings = sessions.dropna(subset=["booking_id"])
        multiple_booking_sessions = sessions_with_bookings.groupby("session_id")["booking_id"].nunique().loc[lambda x: x > 1].count()
        print("Sessions with more than one booking:", multiple_booking_sessions)

        # 3. Days of the week with the highest number of bookings (pie chart)
        bookings["booking_time"] = pd.to_datetime(bookings["booking_time"])
        bookings["day_of_week"] = bookings["booking_time"].dt.day_name()
        day_counts = bookings["day_of_week"].value_counts()
        day_counts.plot(kind="pie", autopct="%1.1f%%", startangle=140, title="Bookings by Day of the Week")
        plt.show()

        # 4. Total bookings and gross booking value by service name
        service_stats = bookings.groupby("service_name").agg(
            total_bookings=("booking_id", "count"),
            total_gross_value=("INR_Amount", "sum")
        )
        print("Service Stats:\n", service_stats)

        # 5. Most booked route (from_city to to_city) for customers with more than 1 booking
        multi_booking_customers = bookings["customer_id"].value_counts().loc[lambda x: x > 1].index
        multi_booking_data = bookings[bookings["customer_id"].isin(multi_booking_customers)]
        most_booked_route = multi_booking_data.groupby(["from_city", "to_city"]).size().idxmax()
        print("Most booked route for multi-booking customers:", most_booked_route)

        # 6. Top 3 departure cities for advance bookings with at least 5 departures
        advance_bookings = bookings[bookings["days_to_departure"] > 1]
        city_advance_avg = advance_bookings.groupby("from_city").agg(
            avg_days_to_departure=("days_to_departure", "mean"),
            departures=("from_city", "size")
        ).loc[lambda x: x["departures"] >= 5].nlargest(3, "avg_days_to_departure")
        print("Top 3 advance departure cities:\n", city_advance_avg)

        # 7. Correlation heatmap of numerical columns
        numerical_columns = bookings.select_dtypes(include="number")
        correlation_matrix = numerical_columns.corr()
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm")
        plt.title("Correlation Matrix")
        plt.show()
        max_correlation = correlation_matrix.unstack().drop_duplicates().sort_values(ascending=False)
        max_pair = max_correlation.index[1]
        print("Most correlated pair:", max_pair, "with correlation", max_correlation[max_pair])

        # 8. Most used device type for each service
        most_used_device = bookings.groupby("service_name")["device_type_used"].agg(lambda x: x.mode()[0])
        print("Most used device by service:\n", most_used_device)

        # 9. Quarterly trends by device type
        bookings.set_index("booking_time", inplace=True)
        bookings["quarter"] = bookings.index.to_period("Q")
        quarterly_trends = bookings.groupby(["quarter", "device_type_used"]).size().unstack().fillna(0)
        quarterly_trends.plot(kind="line", marker="o", title="Quarterly Booking Trends by Device Type")
        plt.ylabel("Number of Bookings")
        plt.show()

        # 10. Overall Booking to Search Ratio (oBSR) Analysis
        total_searches = sessions["search_id"].nunique()
        total_bookings = bookings["booking_id"].nunique()

        # Average oBSR per month
        sessions["month"] = pd.to_datetime(sessions["search_time"]).dt.month
        monthly_searches = sessions.groupby("month")["search_id"].nunique()
        monthly_bookings = bookings.groupby(bookings["booking_time"].dt.month)["booking_id"].nunique()
        monthly_obsr = (monthly_bookings / monthly_searches).fillna(0)
        print("Monthly oBSR:\n", monthly_obsr)

        # Average oBSR per day of the week
        sessions["day_of_week"] = pd.to_datetime(sessions["search_time"]).dt.day_name()
        daily_searches = sessions.groupby("day_of_week")["search_id"].nunique()
        daily_bookings = bookings.groupby(bookings["day_of_week"])["booking_id"].nunique()
        daily_obsr = (daily_bookings / daily_searches).fillna(0)
        print("Daily oBSR:\n", daily_obsr)

        # Plot oBSR time series
        daily_session_counts = sessions.groupby(sessions["search_time"].str[:10])["search_id"].nunique()
        daily_booking_counts = bookings.groupby(bookings["booking_time"].dt.date)["booking_id"].nunique()
        obsr_timeseries = (daily_booking_counts / daily_session_counts).fillna(0)
        obsr_timeseries.plot(title="Daily oBSR Time Series", ylabel="oBSR")
        plt.show()

    except PermissionError as e:
        print(f"PermissionError: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
else:
    print("Please check file paths and permissions before proceeding.")


# In[15]:


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load datasets
bookings = pd.read_csv(r"C:\Users\udayv\OneDrive\Desktop\edurekha project\1st mini  project\Bookings.csv")
sessions = pd.read_csv(r"C:\Users\udayv\OneDrive\Desktop\edurekha project\1st mini  project\Sessions.csv")

# 1. Number of distinct bookings, sessions, and searches
distinct_bookings = bookings["booking_id"].nunique()
distinct_sessions = sessions["session_id"].nunique()
distinct_searches = sessions["search_id"].nunique()
print("Distinct bookings:", distinct_bookings)
print("Distinct sessions:", distinct_sessions)
print("Distinct searches:", distinct_searches)

# 2. Sessions with more than one booking
sessions_with_bookings = sessions.dropna(subset=["booking_id"])
multiple_booking_sessions = sessions_with_bookings.groupby("session_id")["booking_id"].nunique().loc[lambda x: x > 1].count()
print("Sessions with more than one booking:", multiple_booking_sessions)

# 3. Days of the week with the highest number of bookings (pie chart)
bookings["booking_time"] = pd.to_datetime(bookings["booking_time"])
bookings["day_of_week"] = bookings["booking_time"].dt.day_name()
day_counts = bookings["day_of_week"].value_counts()
day_counts.plot(kind="pie", autopct="%1.1f%%", startangle=140, title="Bookings by Day of the Week")
plt.show()

# 4. Total bookings and gross booking value by service name
service_stats = bookings.groupby("service_name").agg(
    total_bookings=("booking_id", "count"),
    total_gross_value=("INR_Amount", "sum")
)
print(service_stats)

# 5. Most booked route (from_city to to_city) for customers with more than 1 booking
multi_booking_customers = bookings["customer_id"].value_counts().loc[lambda x: x > 1].index
multi_booking_data = bookings[bookings["customer_id"].isin(multi_booking_customers)]
most_booked_route = multi_booking_data.groupby(["from_city", "to_city"]).size().idxmax()
print("Most booked route for multi-booking customers:", most_booked_route)

# 6. Top 3 departure cities for advance bookings with at least 5 departures
advance_bookings = bookings[bookings["days_to_departure"] > 1]
city_advance_avg = advance_bookings.groupby("from_city").agg(
    avg_days_to_departure=("days_to_departure", "mean"),
    departures=("from_city", "size")
).loc[lambda x: x["departures"] >= 5].nlargest(3, "avg_days_to_departure")
print("Top 3 advance departure cities:", city_advance_avg)

# 7. Correlation heatmap of numerical columns
numerical_columns = bookings.select_dtypes(include="number")
correlation_matrix = numerical_columns.corr()
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm")
plt.title("Correlation Matrix")
plt.show()
max_correlation = correlation_matrix.unstack().drop_duplicates().sort_values(ascending=False)
max_pair = max_correlation.index[1]
print("Most correlated pair:", max_pair, "with correlation", max_correlation[max_pair])

# 8. Most used device type for each service
most_used_device = bookings.groupby("service_name")["device_type_used"].agg(lambda x: x.mode()[0])
print("Most used device by service:", most_used_device)

# 9. Quarterly trends by device type
bookings.set_index("booking_time", inplace=True)
bookings["quarter"] = bookings.index.to_period("Q")
quarterly_trends = bookings.groupby(["quarter", "device_type_used"]).size().unstack().fillna(0)
quarterly_trends.plot(kind="line", marker="o", title="Quarterly Booking Trends by Device Type")
plt.ylabel("Number of Bookings")
plt.show()

# 10. Overall Booking to Search Ratio (oBSR) Analysis
total_searches = sessions["search_id"].nunique()
total_bookings = bookings["booking_id"].nunique()

# Average oBSR per month
sessions["month"] = pd.to_datetime(sessions["search_time"]).dt.month
monthly_searches = sessions.groupby("month")["search_id"].nunique()
monthly_bookings = bookings.groupby(bookings["booking_time"].dt.month)["booking_id"].nunique()
monthly_obsr = (monthly_bookings / monthly_searches).fillna(0)
print("Monthly oBSR:", monthly_obsr)

# Average oBSR per day of the week
sessions["day_of_week"] = pd.to_datetime(sessions["search_time"]).dt.day_name()
daily_searches = sessions.groupby("day_of_week")["search_id"].nunique()

daily_bookings = bookings.groupby(bookings["day_of_week"])["booking_id"].nunique()
daily_obsr = (daily_bookings / daily_searches).fillna(0)
print("Daily oBSR:", daily_obsr)

# Plot oBSR time series
daily_session_counts = sessions.groupby(sessions["search_time"].str[:10])["search_id"].nunique()
daily_booking_counts = bookings.groupby(bookings["booking_time"].dt.date)["booking_id"].nunique()
obsr_timeseries = (daily_booking_counts / daily_session_counts).fillna(0)
obsr_timeseries.plot(title="Daily oBSR Time Series", ylabel="oBSR")
plt.show()



# In[18]:


import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define the file paths
bookings_file = r"C:\Users\udayv\OneDrive\Desktop\edurekha project\1st mini  project\Bookings.csv"  # Update this path
sessions_file = r"C:\Users\udayv\OneDrive\Desktop\edurekha project\1st mini  project\Sessions.csv"  # Update this path

# Function to check file access permissions
def check_file_access(filepath):
    if os.path.exists(filepath):
        if os.access(filepath, os.R_OK):
            print(f"File '{filepath}' is accessible and ready to load.")
            return True
        else:
            print(f"Permission denied: Unable to read '{filepath}'.")
            return False
    else:
        print(f"File not found: '{filepath}' does not exist.")
        return False

# Check access to both files
if check_file_access(bookings_file) and check_file_access(sessions_file):
    try:
        # Load datasets
        bookings = pd.read_csv(bookings_file)
        sessions = pd.read_csv(sessions_file)

        # 1. Number of distinct bookings, sessions, and searches
        distinct_bookings = bookings["booking_id"].nunique()
        distinct_sessions = sessions["session_id"].nunique()
        distinct_searches = sessions["search_id"].nunique()
        print("Distinct bookings:", distinct_bookings)
        print("Distinct sessions:", distinct_sessions)
        print("Distinct searches:", distinct_searches)

        # 2. Sessions with more than one booking
        sessions_with_bookings = sessions.dropna(subset=["booking_id"])
        multiple_booking_sessions = sessions_with_bookings.groupby("session_id")["booking_id"].nunique().loc[lambda x: x > 1].count()
        print("Sessions with more than one booking:", multiple_booking_sessions)

        # 3. Days of the week with the highest number of bookings (pie chart)
        bookings["booking_time"] = pd.to_datetime(bookings["booking_time"], errors='coerce')
        bookings["day_of_week"] = bookings["booking_time"].dt.day_name()
        day_counts = bookings["day_of_week"].value_counts()
        day_counts.plot(kind="pie", autopct="%1.1f%%", startangle=140, title="Bookings by Day of the Week")
        plt.show()

        # 4. Total bookings and gross booking value by service name
        service_stats = bookings.groupby("service_name").agg(
            total_bookings=("booking_id", "count"),
            total_gross_value=("INR_Amount", "sum")
        )
        print("Service Stats:\n", service_stats)

        # 5. Most booked route (from_city to to_city) for customers with more than 1 booking
        multi_booking_customers = bookings["customer_id"].value_counts().loc[lambda x: x > 1].index
        multi_booking_data = bookings[bookings["customer_id"].isin(multi_booking_customers)]
        most_booked_route = multi_booking_data.groupby(["from_city", "to_city"]).size().idxmax()
        print("Most booked route for multi-booking customers:", most_booked_route)

        # 6. Top 3 departure cities for advance bookings with at least 5 departures
        advance_bookings = bookings[bookings["days_to_departure"] > 1]
        city_advance_avg = advance_bookings.groupby("from_city").agg(
            avg_days_to_departure=("days_to_departure", "mean"),
            departures=("from_city", "size")
        ).loc[lambda x: x["departures"] >= 5].nlargest(3, "avg_days_to_departure")
        print("Top 3 advance departure cities:\n", city_advance_avg)

        # 7. Correlation heatmap of numerical columns
        numerical_columns = bookings.select_dtypes(include="number")
        correlation_matrix = numerical_columns.corr()
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm")
        plt.title("Correlation Matrix")
        plt.show()
        max_correlation = correlation_matrix.unstack().drop_duplicates().sort_values(ascending=False)
        max_pair = max_correlation.index[1]
        print("Most correlated pair:", max_pair, "with correlation", max_correlation[max_pair])

        # 8. Most used device type for each service
        most_used_device = bookings.groupby("service_name")["device_type_used"].agg(lambda x: x.mode()[0])
        print("Most used device by service:\n", most_used_device)

        # 9. Quarterly trends by device type
        bookings.set_index("booking_time", inplace=True)
        bookings["quarter"] = bookings.index.to_period("Q")
        quarterly_trends = bookings.groupby(["quarter", "device_type_used"]).size().unstack().fillna(0)
        quarterly_trends.plot(kind="line", marker="o", title="Quarterly Booking Trends by Device Type")
        plt.ylabel("Number of Bookings")
        plt.show()

        # 10. Overall Booking to Search Ratio (oBSR) Analysis
        total_searches = sessions["search_id"].nunique()
        total_bookings = bookings["booking_id"].nunique()

        # Convert search_time to datetime with flexible date format parsing
        sessions["search_time"] = pd.to_datetime(sessions["search_time"], format='ISO8601', errors='coerce')

        # Check for and handle any parsing errors (NaT values)
        if sessions["search_time"].isna().any():
            print("Warning: Some dates in 'search_time' couldn't be parsed and are set as NaT.")

        # Average oBSR per month
        sessions["month"] = sessions["search_time"].dt.month
        monthly_searches = sessions.groupby("month")["search_id"].nunique()
        monthly_bookings = bookings.groupby(bookings["booking_time"].dt.month)["booking_id"].nunique()
        monthly_obsr = (monthly_bookings / monthly_searches).fillna(0)
        print("Monthly oBSR:\n", monthly_obsr)

        # Average oBSR per day of the week
        sessions["day_of_week"] = sessions["search_time"].dt.day_name()
        daily_searches = sessions.groupby("day_of_week")["search_id"].nunique()
        daily_bookings = bookings.groupby(bookings["day_of_week"])["booking_id"].nunique()
        daily_obsr = (daily_bookings / daily_searches).fillna(0)
        print("Daily oBSR:\n", daily_obsr)

        # Plot oBSR time series
        daily_session_counts = sessions.groupby(sessions["search_time"].dt.date)["search_id"].nunique()
        daily_booking_counts = bookings.groupby(bookings["booking_time"].dt.date)["booking_id"].nunique()
        obsr_timeseries = (daily_booking_counts / daily_session_counts).fillna(0)
        obsr_timeseries.plot(title="Daily oBSR Time Series", ylabel="oBSR")
        plt.show()

    except PermissionError as e:
        print(f"PermissionError: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
else:
    print("Please check file paths and permissions before proceeding.")


# In[ ]:




