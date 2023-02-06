import os
import pandas as pd
import numpy as np
import random

from dialog import show_dialog


def generate_number(df):
    # Generate a random 8-digit number
    number = random.randint(10000000, 99999999)

    # Check if the number already exists in the DataFrame
    if np.isin(number, df["Code"].astype(int).values):
        number = generate_number(df)
    return number


def save_number(file_path, id):
    expected_headers = ['ID', 'Code']

    # Load the Excel file into a pandas DataFrame
    if os.path.exists(file_path):
        df = pd.read_excel(file_path, sheet_name=0)

        # Check if the headers are as expected
        if set(df.columns) != set(expected_headers):
            print("The headers of the file are not as expected. Expected headers: {}".format(expected_headers))
            raise ValueError(402, 'فرمت فایل اشتباه است')

        # Check if the given ID already exists in the DataFrame
        if np.isin(id, df["ID"].astype(str).values):
            print("The ID {} already exists.".format(id))
            return df.loc[df['ID'] == int(id), 'Code'].iloc[0]

        # Generate a unique random 8-digit number
        generated_number = generate_number(df)

        # Append the new numbers to the DataFrame
        df = df.append({'ID': id, 'Code': generated_number}, ignore_index=True)

    # Create a new DataFrame if the file does not exist
    else:
        generated_number = generate_number(pd.DataFrame({'Code': []}))
        df = pd.DataFrame({'ID': [id], 'Code': [generated_number]})

    # Save the DataFrame to the Excel file
    df.to_excel(file_path, index=False)
    return generated_number


# Save a given ID and a generated 8-digit number to the Excel file "users.xlsx"
file_path = "users.xlsx"


def assign_subscription_code(users: list):
    try:
        for user in users:
            user += [save_number(file_path, user[0])]
    except ValueError as e:
        show_dialog(error=e)
    return users


def resolve_url(users: list, base_url):
    for user in users:
        user += [f'{base_url}/{str(user[2])}']
    return users
