from django.forms import ModelForm, widgets
from django import forms
from .models import User, Links
from django.contrib.auth.forms import UserCreationForm
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from oauth2client.tools import run_flow,argparser
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets

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
        fields = ['companyname', 'link']

    def clean(self):
        cleaned_data = super().clean()
        link = cleaned_data.get('link')

        try:
            spreadsheet_id = self.get_spreadsheet_id_from_url(link)

            if spreadsheet_id:
                # Authenticate the user using OAuth2
                flow = flow_from_clientsecrets(
                    '../client_secret_new.json',
                    scope=['https://www.googleapis.com/auth/spreadsheets.readonly'],
                    redirect_uri='http://localhost:8000/uploadsheet')

                # Use the request object to get the user's credentials
                flags = argparser.parse_args(args=[])
                credentials = run_flow(flow, Storage('credentials.json'), flags)

                # Use the access token to access the Google Sheets API
                service = build('sheets', 'v4', credentials=credentials)
                sheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

                # Read values from the first sheet
                result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='A1:B10').execute()
                values = result.get('values', [])

                if values:
                    print('Data:')
                    for row in values:
                        print(row)
                else:
                    print('No data found.')
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