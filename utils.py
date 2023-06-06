import os
from copy import deepcopy

import pandas as pd
import numpy as np
import random

from dialog import show_dialog

import hashlib

from settings import user_excel_file


def generate_number(df):
    # Generate a random 8-digit number
    number = random.randint(10000000, 99999999)

    # Check if the number already exists in the DataFrame
    if np.isin(number, df["Code"].astype(int).values):
        number = generate_number(df)
    return number


def save_number(file_path, id):
    expected_headers = ['ID', 'Code', 'Hashed Code']

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
            return df.loc[df['ID'] == int(id), 'Code'].iloc[0], df.loc[df['ID'] == int(id), 'Hashed Code'].iloc[
                0], False

        # Generate a unique random 8-digit number
        generated_number = generate_number(df)

        # Hash the generated code
        hashed_code = hashlib.md5(str(generated_number).encode()).hexdigest()[:16]

        # Append the new numbers to the DataFrame
        temp_df = pd.DataFrame({'ID': [id], 'Code': [generated_number], 'Hashed Code': [hashed_code]})
        df = pd.concat([df, temp_df], ignore_index=True)

    # Create a new DataFrame if the file does not exist
    else:
        generated_number = generate_number(pd.DataFrame({'Code': []}))
        hashed_code = hashlib.md5(str(generated_number).encode()).hexdigest()[:16]
        df = pd.DataFrame({'ID': [id], 'Code': [generated_number], 'Hashed Code': [hashed_code]})

    # Save the DataFrame to the Excel file
    df.to_excel(file_path, index=False)
    return generated_number, hashed_code, True


def delete_number(codes, file_path=user_excel_file):
    df = pd.read_excel(file_path, sheet_name=0)
    for code in codes:
        df = df.drop(df[df['Code'] == code].index)
    df.to_excel(file_path, index=False)
    return df


def assign_subscription_code(users: list, signal):
    try:
        for i, user in enumerate(users):
            user['code'], user['hashed_code'], user['created'] = save_number(user_excel_file, user['id'])
            if signal:
                signal.emit((i + 1) * 100 / (len(users)))
    except ValueError as e:
        show_dialog(error=e)

    user = deepcopy(users)
    users = []
    for u in user:
        if u['created']:
            users.append(u)
    return users


def resolve_url(users: list, signal, base_url):
    for i, user in enumerate(users):
        user['url'] = f"{base_url}/{str(user['hashed_code'])}"
        if signal:
            signal.emit((i + 1) * 100 / (len(users)))
    return users
