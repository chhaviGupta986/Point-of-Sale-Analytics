import math
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import warnings
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

def forecast(df_param):
  dataco_supply_chain=df_param
  # Standardize column names for dataco_supply_chain dataset
  dataco_supply_chain.columns = dataco_supply_chain.columns.str.upper().str.replace(' ', '_')
  dataco_supply_chain.head()
  dataco_supply_chain = dataco_supply_chain[['ORDER_DATE_(DATEORDERS)','CATEGORY_NAME','CATEGORY_ID'
      ,'ORDER_ITEM_QUANTITY'
      ,'ORDER_REGION'
      ,'ORDER_STATUS',
      'PRODUCT_NAME',
      'PRODUCT_CARD_ID','CUSTOMER_ID','ORDER_ID'
      ,'DAYS_FOR_SHIPPING_(REAL)','DAYS_FOR_SHIPMENT_(SCHEDULED)','ORDER_ITEM_DISCOUNT','ORDER_ITEM_DISCOUNT_RATE'
      ,'PRODUCT_PRICE','ORDER_COUNTRY','ORDER_STATE','PRODUCT_CATEGORY_ID'
      ]
  ]
  dataco_supply_chain['ORDER_DATE_(DATEORDERS)'] = pd.to_datetime(dataco_supply_chain['ORDER_DATE_(DATEORDERS)'])
  # Extracting year, month, day, and weekday from the order date
  dataco_supply_chain['ORDER_YEAR'] = dataco_supply_chain['ORDER_DATE_(DATEORDERS)'].dt.year
  dataco_supply_chain['ORDER_MONTH'] = dataco_supply_chain['ORDER_DATE_(DATEORDERS)'].dt.month
  dataco_supply_chain['ORDER_DAY'] = dataco_supply_chain['ORDER_DATE_(DATEORDERS)'].dt.day
  dataco_supply_chain['ORDER_WEEKDAY'] = dataco_supply_chain['ORDER_DATE_(DATEORDERS)'].dt.weekday
  dataco_supply_chain['ORDER_DATE'] = pd.to_datetime(dataco_supply_chain['ORDER_DATE_(DATEORDERS)'].dt.date)
  dataco_supply_chain.drop(columns='ORDER_DATE_(DATEORDERS)', inplace=True)
  dataco_supply_chain = dataco_supply_chain[(dataco_supply_chain['ORDER_DATE'] <= pd.to_datetime('2017-07-01'))]
  df=dataco_supply_chain
  # df.info()
  # Make a copy of the DataFrame
  df_encoded = df.copy()
  # Iterate over columns and encode object type columns
  for column in df.columns:
      if df[column].dtype == 'object':
          label_encoder = LabelEncoder()
          df_encoded[column] = label_encoder.fit_transform(df[column])

  # df_encoded.info()
  df =df_encoded.copy()
  df_cust=df_encoded.copy() #for number of customers prediction
  # print(df_cust.head())
  daily_orders_cust = df_cust.drop(columns=['CATEGORY_NAME','CATEGORY_ID','PRODUCT_CARD_ID','PRODUCT_CATEGORY_ID','DAYS_FOR_SHIPPING_(REAL)','ORDER_STATUS','ORDER_ITEM_QUANTITY','ORDER_ID'])
  daily_orders_cust = df_cust.groupby(['ORDER_DATE', 'PRODUCT_NAME']).agg({'CUSTOMER_ID': 'count',
                                                                'ORDER_ITEM_DISCOUNT_RATE': 'mean','PRODUCT_PRICE':'mean'
                                                                ,'DAYS_FOR_SHIPMENT_(SCHEDULED)':'mean'}).reset_index()


  daily_orders_cust.rename(columns={'CUSTOMER_ID': 'NUM_CUSTOMERS'}, inplace=True)

  daily_orders_cust['NUM_CUSTOMERS'] = daily_orders_cust['NUM_CUSTOMERS']
  unique_dates_cust = pd.date_range(start=daily_orders_cust['ORDER_DATE'].min(), end=daily_orders_cust['ORDER_DATE'].max(), freq='D')
  # print("len of unique dates is ",len(unique_dates_cust),unique_dates_cust.shape)
  unique_products = daily_orders_cust['PRODUCT_NAME'].unique()
  date_product_combinations = pd.DataFrame([(date, product) for date in unique_dates_cust for product in unique_products],
                                          columns=['ORDER_DATE', 'PRODUCT_NAME'])
  complete_df_cust = pd.merge(date_product_combinations, daily_orders_cust, on=['ORDER_DATE', 'PRODUCT_NAME'], how='left')

  # List of columns to interpolate
  columns_to_interpolate = ['ORDER_ITEM_DISCOUNT_RATE', 'DAYS_FOR_SHIPMENT_(SCHEDULED)','PRODUCT_PRICE']
  # complete_df_cust[columns_to_interpolate] = complete_df_cust[columns_to_interpolate].fillna(complete_df_cust[columns_to_interpolate].median())
  complete_df_cust['NUM_CUSTOMERS'].fillna(0, inplace=True)
  complete_df_cust.sort_values(by=['ORDER_DATE', 'PRODUCT_NAME'], inplace=True)

  # # Reset index
  complete_df_cust.reset_index(drop=True, inplace=True)

  complete_df_cust['YEAR_MONTH']=complete_df_cust['ORDER_DATE'].dt.month
  # complete_df_cust['YEAR_WEEK']=complete_df_cust['ORDER_DATE'].dt.week
  complete_df_cust['YEAR_WEEK'] = complete_df_cust['ORDER_DATE'].dt.isocalendar().week

  complete_df_cust['DAY_OF_WEEK_NUMERICAL'] = complete_df_cust['ORDER_DATE'].dt.dayofweek

  # Number of unique product name values
  complete_df_cust['IS_WEEKEND'] = complete_df_cust['DAY_OF_WEEK_NUMERICAL'].isin([5, 6]).astype(int)
  # complete_df_cust['ORDER_ITEM_DISCOUNT_RATE'] = complete_df_cust['ORDER_ITEM_DISCOUNT_RATE'] * 100
  complete_df_cust['ORDER_ITEM_DISCOUNT_RATE'] = complete_df_cust['ORDER_ITEM_DISCOUNT_RATE']
  period=7
  # Dictionary to store time series data for each product
  product_time_series_cust = {}
  input_last_few_cust={}
  # import warnings
  i=0
  for prod_name in unique_products:
    product_time_series_cust[i] = complete_df_cust[complete_df_cust['PRODUCT_NAME'] == i].reset_index(drop=True)
    # print(product_time_series_cust[i])

    ts=product_time_series_cust[i]

    # ts = ts.copy()
    lagged_values =  ts['NUM_CUSTOMERS'].shift(periods=period)
    ts['LAGGED_NUM_CUSTOMERS'] = lagged_values

    ts.dropna(subset=['LAGGED_NUM_CUSTOMERS'], inplace=True)

    ts[columns_to_interpolate] = ts[columns_to_interpolate].fillna(ts[columns_to_interpolate].median())
    input_last_few_cust[i]=product_time_series_cust[i][(-1*period):]
    product_time_series_cust[i]=product_time_series_cust[i][:(-1*period)]

    warnings.filterwarnings("ignore")
    i+=1
  daily_orders = df.groupby(['ORDER_DATE', 'PRODUCT_NAME']).agg({'ORDER_ITEM_QUANTITY': 'sum', 'CUSTOMER_ID': 'count'}).reset_index()

  daily_orders.rename(columns={'CUSTOMER_ID': 'NUM_CUSTOMERS'}, inplace=True)

  # Assuming your existing DataFrame is called df_grouped
  # Create a DataFrame with all combinations of dates and products
  unique_dates = pd.date_range(start=daily_orders['ORDER_DATE'].min(), end=daily_orders['ORDER_DATE'].max(), freq='D')
  # print("len of unique dates is ",len(unique_dates),unique_dates.shape)
  unique_products = daily_orders['PRODUCT_NAME'].unique()
  date_product_combinations = pd.DataFrame([(date, product) for date in unique_dates for product in unique_products],
                                          columns=['ORDER_DATE', 'PRODUCT_NAME'])
  # Merge with existing DataFrame to fill in missing values
  complete_df = pd.merge(date_product_combinations, daily_orders, on=['ORDER_DATE', 'PRODUCT_NAME'], how='left')

  # Fill missing values in ORDER_ITEM_QUANTITY with 0
  complete_df['ORDER_ITEM_QUANTITY'].fillna(0, inplace=True)
  # complete_df['NUM_ORDERS'].fillna(0, inplace=True)
  complete_df['NUM_CUSTOMERS'].fillna(0, inplace=True)
  # Sort by ORDER_DATE and PRODUCT_NAME
  complete_df.sort_values(by=['ORDER_DATE', 'PRODUCT_NAME'], inplace=True)

  # Reset index
  complete_df.reset_index(drop=True, inplace=True)
  complete_df['YEAR_MONTH']=complete_df['ORDER_DATE'].dt.month
  # complete_df['YEAR_WEEK']=complete_df['ORDER_DATE'].dt.week
  complete_df_cust['YEAR_WEEK'] = complete_df_cust['ORDER_DATE'].dt.isocalendar().week
  complete_df['DAY_OF_WEEK_NUMERICAL'] = complete_df['ORDER_DATE'].dt.dayofweek

  complete_df.head()
  # num_unique_products = daily_orders['PRODUCT_NAME'].nunique()
  # print("Number of unique product names:", num_unique_products)
  complete_df['IS_WEEKEND'] = complete_df['DAY_OF_WEEK_NUMERICAL'].isin([5, 6]).astype(int)

  product_time_series = {}
  input_last_few={}
  predictions=[]
  actuals=[]
  r2_array=[]
  i=0
  for prod_name in unique_products:
    product_time_series[i] = complete_df[complete_df['PRODUCT_NAME'] == i].reset_index(drop=True)
    ts=product_time_series[i]
    lagged_values =  ts['ORDER_ITEM_QUANTITY'].shift(periods=period)
    ts['LAGGED_ORDER_QTY'] = lagged_values
    ts.dropna(subset=['LAGGED_ORDER_QTY'], inplace=True)
    input_last_few[i]=product_time_series[i][(-1*period):]
    product_time_series[i]=product_time_series[i][:(-1*period)]
    warnings.filterwarnings("ignore")
    i+=1

  top_prod_indexes = {}
  # prod_index=6
  i=0
  for prod_name in unique_products:
    prod_index=i
    # print("\nFOR PRODUCT NAME=",prod_name)
    df=product_time_series[prod_index]
    df_cust=product_time_series_cust[prod_index]

    X_cust = df_cust.drop(columns=['NUM_CUSTOMERS','ORDER_DATE'])# Features
    y_cust = df_cust['NUM_CUSTOMERS'] # Target variable
    # Split the data into train and test sets
    X_train_cust, X_test, y_train, y_test = train_test_split(X_cust, y_cust, test_size=0.2, random_state=42)

    # Initialize Random Forest Regressor
    rf_regressor_cust = RandomForestRegressor(n_estimators=50, random_state=42)
    # Train the model
    rf_regressor_cust.fit(X_train_cust, y_train)

    # Predict on the test set
    y_pred = rf_regressor_cust.predict(X_test)


    r2 = r2_score(y_test, y_pred)

    # print(f"Mean Squared Error (MSE): {mse}")
    # print(f"Mean Absolute Error (MAE): {mae}")
    # print(f"R-squared (R2): {r2}")

    X = df.drop(columns=['ORDER_ITEM_QUANTITY','ORDER_DATE'])# Features
    y = df['ORDER_ITEM_QUANTITY'] # Target variable
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize Random Forest Regressor
    rf_regressor = RandomForestRegressor(n_estimators=20, random_state=42)
    rf_regressor.fit(X_train, y_train)

    # Predict on the test set
    y_pred = rf_regressor.predict(X_test)

    r2 = r2_score(y_test, y_pred)

    # print(f"Mean Squared Error (MSE): {mse}")
    # print(f"Mean Absolute Error (MAE): {mae}")
    # print(f"R-squared (R2): {r2}")
    r2_array.append(r2)

    #UNSEEN INPUTS BEGIN HERE
    #Here period is last 3 days, can change it as u wish
    dates_to_plot=input_last_few_cust[prod_index]['ORDER_DATE'].values
    # Convert the NumPy array of datetime64 objects to pandas Timestamp objects
    dates_to_plot = pd.to_datetime(dates_to_plot)

    # Format the dates as strings in 'YYYY-MM-DD' format
    dates_to_plot = dates_to_plot.strftime('%Y-%m-%d')
    dates_to_plot =dates_to_plot.tolist()
    # print("dates_to_plot is",dates_to_plot)
    df_input_cust=input_last_few_cust[prod_index].drop(columns=['NUM_CUSTOMERS','ORDER_DATE'])
    y_new_cust=rf_regressor_cust.predict(df_input_cust)
    # print("ACTUAL no. of customers who ordered product no.",prod_index,"in last",period,"days are")
    # print(input_last_few_cust[prod_index]['NUM_CUSTOMERS'].values)
    # print("PREDICTED no. of customers who ordered product no.",prod_index,"in last",period,"days are")
    # print(y_new_cust)
    df_input=input_last_few[prod_index].drop(columns=['ORDER_ITEM_QUANTITY','ORDER_DATE'])
    df_input['NUM_CUSTOMERS']=y_new_cust
    y_new=rf_regressor.predict(df_input).tolist()
    # Convert each element to integer by flooring
    y_new = [math.floor(val) for val in y_new]
    # print("ACTUAL quantity of orders placed for product no.",prod_index,"in last",period,"days are")
    # print(input_last_few[prod_index]['ORDER_ITEM_QUANTITY'].values)
    act=input_last_few[prod_index]['ORDER_ITEM_QUANTITY'].values.tolist()
    act = [math.floor(val) for val in act]
    actuals.append(act)
    # print("PREDICTED quantity of orders placed for product no.",prod_index,"in last",period,"days are")
    # print(y_new)
    predictions.append(y_new)
    top_prod_indexes[prod_name]=sum(y_new)
    i+=1
  # Find the top 5 selling prod_indexes
  top_prod_indexes = dict(sorted(top_prod_indexes.items(), key=lambda item: item[1], reverse=True))

  # Print the top 5 selling prod_indexes
  # print(f"Top 5 bestsellers for next {period} days:")
  # for prod_index, total_value in top_prod_indexes.items():
  #     print(f"Product id {prod_index}, Total Predicted Demand={total_value} units")
  return actuals,predictions,dates_to_plot,top_prod_indexes,r2_array

# ip=pd.read_csv("D:/STUDIES_or_COLLEGE/All sems/TY/sem 6/MP/MP Project/MP - Copy/MP - Copy/backend/datasets/DataCoSupplyChainDataset.csv",header= 0,encoding= 'unicode_escape')
# rets=forecast(ip)
# order_of_return=['actuals','predictions','dates_to_plot','top_prod_indexes','r2_array']
# print("PRINTING RETSS\n")
# i=0
# for ret in rets:
#    print("printing the ",order_of_return[i])
#    print(ret)
#    print()
#    i+=1