from django.forms import ModelForm, widgets
from django import forms
from .models import User, Links
from django.contrib.auth.forms import UserCreationForm
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from oauth2client.tools import run_flow, argparser
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
import pandas as pd

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['company_name', 'email', 'username', 'type', 'years', 'password1', 'password2']
        
class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['email','password']

class LinkForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(LinkForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Links
        fields = ['link']

    def clean(self):
        cleaned_data = super().clean()
        link = cleaned_data.get('link')

        try:
            spreadsheet_id = self.get_spreadsheet_id_from_url(link)

            if spreadsheet_id:
                print('hi')
                # Authenticate the user using OAuth2
                flow = flow_from_clientsecrets(
                    '../client_secret_new2.json',
                    scope=['https://www.googleapis.com/auth/spreadsheets.readonly'],
                    redirect_uri='http://localhost:8000/uploadsheet')

                print('hi2')
                # Use the request object to get the user's credentials
                flags = argparser.parse_args(args=[])
                credentials = run_flow(flow, Storage('credentials2.json'), flags)

                print('hi3')
                # Use the access token to access the Google Sheets API
                service = build('sheets', 'v4', credentials=credentials)
                sheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

                # Read values from the first sheet
                result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='A:BA').execute()
                values = result.get('values', [])

                # Define the data types for the columns
                column_dtypes = {
                    'order date (DateOrders)': 'datetime64[ns]',
                    'Days for shipping (real)': 'int64',
                    'Days for shipment (scheduled)': 'int64',
                    'Benefit per order': 'float64',
                    'Sales per customer': 'float64',
                    'Late_delivery_risk': 'int64',
                    'Category Id': 'int64',
                    'Customer Id': 'int64',
                    # 'Customer Zipcode': 'float64',
                    # 'Customer Zipcode': 'float64',
                    'Department Id': 'int64',
                    'Order Customer Id': 'int64',
                    'Order Id': 'int64',
                    'Order Item Cardprod Id': 'int64',
                    'Order Item Discount': 'float64',
                    'Order Item Discount Rate': 'float64',
                    'Order Item Id': 'int64',
                    'Order Item Product Price': 'float64',
                    'Order Item Profit Ratio': 'float64',
                    'Order Item Quantity': 'int64',
                    'Sales': 'float64',
                    'Order Item Total': 'float64',
                    'Order Profit Per Order': 'float64',
                    # 'Order Zipcode': 'float64',
                    'Product Card Id': 'int64',
                    'Product Category Id': 'int64',
                    'Product Price': 'float64',
                    'Product Status': 'int64'
                }

                # Create a pandas DataFrame from the sheet data
                df = pd.DataFrame(values[1:], columns=values[0])

                # Convert the data types of the columns
                df = df.astype(column_dtypes)

                cleaned_data['link_data'] = df
            else:
                raise forms.ValidationError('Invalid spreadsheet URL.')
        except Exception as e:
            raise forms.ValidationError(f'Error accessing spreadsheet: {e}')

        return cleaned_data    

    def get_spreadsheet_id_from_url(self, url):
        try:
            parts = url.split('/')
            spreadsheet_id = parts[-2]
            return spreadsheet_id
        except Exception as e:
            # Handle any errors that occur during ID extraction
            print("Error extracting Spreadsheet ID:", e)
            return None