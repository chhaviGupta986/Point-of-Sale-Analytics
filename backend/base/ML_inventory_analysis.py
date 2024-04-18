import pandas as pd
import numpy as np
from statsmodels.stats.outliers_influence import variance_inflation_factor


def generate_ABC_data(df):
    # print("Entered generate_ABC_data")
    
    # print("hi\n",df.head())
    # print("printing df.info\n",df.info())
    # df= pd.read_csv("D:/STUDIES_or_COLLEGE/All sems/TY/sem 6/MP/MP Project/MP - Copy/MP - Copy/backend/datasets/DataCoSupplyChainDataset.csv", encoding_errors="ignore")
    df.drop("Product Description",axis=1,inplace=True)


    #Converting Date Columns to datetime objects

    df["order date (DateOrders)"]=pd.to_datetime(df["order date (DateOrders)"])
    df["shipping date (DateOrders)"]=pd.to_datetime(df["shipping date (DateOrders)"])
    df=df.sort_values(by="order date (DateOrders)")

    df.drop(["Benefit per order","Sales per customer","Order Item Cardprod Id","Order Item Product Price","Product Category Id","Order Customer Id"],axis=1,inplace=True)

    # vif=pd.DataFrame()
    # vif["columns"]=['Order Item Discount',
    #     'Order Item Discount Rate', 'Order Item Profit Ratio',
    #     'Order Item Quantity', 'Sales', 'Order Item Total',
    #     'Order Profit Per Order','Product Price']
    # vif["vif value"] = [variance_inflation_factor(df[['Order Item Discount',
    #     'Order Item Discount Rate', 'Order Item Profit Ratio',
    #     'Order Item Quantity', 'Sales', 'Order Item Total',
    #     'Order Profit Per Order','Product Price']].values, i) for i in range(len(vif["columns"]))]
    # vif.T

    # df[['Order Item Discount',
    #     'Order Item Discount Rate', 'Order Item Profit Ratio',
    #     'Order Item Quantity', 'Sales', 'Order Item Total',
    #     'Order Profit Per Order','Product Price']].head(5)


    # df1=df.drop(["Order Item Total","Product Price","Order Item Discount Rate","Order Profit Per Order"],axis=1)

    df["Delivery Status"].unique()

    df.groupby("Delivery Status")["Order Id"].count()

    df[df["Delivery Status"]=="Shipping canceled"].groupby("Order Status").agg(tc=("Order Id","count"))

    dF_clean=df[df["Delivery Status"]!="Shipping canceled"].copy()

    dF_clean["Year"]=dF_clean["order date (DateOrders)"].dt.year

    # Total_Products=dF_clean["Product Name"].nunique()
    # print("Total Number of products: "+f"{Total_Products}")

    Revenue_ABC=dF_clean.groupby(["Department Name","Product Name"]).agg(Total_Revenue=("Order Item Total","sum")).sort_values(by="Total_Revenue",ascending=False).reset_index()
    Revenue_ABC["cum_sum"]=Revenue_ABC["Total_Revenue"].cumsum()
    # Revenue_ABC['cum_sum'] = pd.to_numeric(Revenue_ABC['cum_sum'])
    # Revenue_ABC['Total_Revenue'] = pd.to_numeric(Revenue_ABC['Total_Revenue'])

    Revenue_ABC["cum_per"]=Revenue_ABC["cum_sum"]/Revenue_ABC["Total_Revenue"].sum()*100
    Revenue_ABC["per"]=Revenue_ABC["cum_per"]-Revenue_ABC["cum_per"].shift(1)
    Revenue_ABC.loc[0,"per"]=Revenue_ABC["cum_per"][0]

# Create empty lists to store products for each class and revenue generated by each class
    class_A_products = []
    class_B_products = []
    class_C_products = []
    revenue_by_class = [0, 0, 0]  # Index 0: Class A, Index 1: Class B, Index 2: Class C

    def ABC(data):
        if data["cum_per"] <= 75:
            return "A"
        elif data["cum_per"] > 75 and data["cum_per"] <= 95:
            return "B"
        elif data["cum_per"] > 95:
            return "C"

    Revenue_ABC["ABC_Revenue"] = Revenue_ABC.apply(ABC, axis=1)

    # Iterate over each class
    for i, class_label in enumerate(['A', 'B', 'C']):
        # Filter products for each class
        products_with_ABC = Revenue_ABC[Revenue_ABC['ABC_Revenue'] == class_label]

        # Store product names in respective lists
        for product_name in products_with_ABC['Product Name']:
            if class_label == 'A':
                class_A_products.append(product_name)
            elif class_label == 'B':
                class_B_products.append(product_name)
            elif class_label == 'C':
                class_C_products.append(product_name)

        # Calculate revenue for each class and store it in the revenue list
        revenue_by_class[i] = products_with_ABC['Total_Revenue'].sum()

    # Print or use the lists as needed
    # print("Class A Products:", class_A_products)
    # print("Class B Products:", class_B_products)
    # print("Class C Products:", class_C_products)
    # print("Revenue by Class:", revenue_by_class)
    # Filter products for Class A
    class_A_products_df = Revenue_ABC[Revenue_ABC['ABC_Revenue'] == 'A']
    graph_x=class_A_products_df['Product Name']
    graph_y=class_A_products_df['Total_Revenue']
    
    return class_A_products,class_B_products,class_C_products,revenue_by_class,graph_x,graph_y
# generate_ABC_data()