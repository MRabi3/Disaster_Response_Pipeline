import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine


def load_data(messages_filepath, categories_filepath):
   """ Load message and categories file, merge and store in a dataframe
   Input:Messages and categories files
   Output:Merged dataframe
   """
   messages = pd.read_csv(messages_filepath, delimiter=",", encoding = 'utf-8')
   categories = pd.read_csv(categories_filepath,  delimiter=",", encoding = 'utf-8')
   df = messages.merge(categories, how='inner', on= 'id')
   return df

def clean_data(df):
    """ Clean the merged dataframe. 
    Input:Merged dataframe
    Output:Dataframe with messages, categories inseperated columns
    """
    categories = df['categories'].str.split(";", expand=True)
    row = categories.iloc[0]
    categories.columns = row.apply(lambda x:x.split('-')[0])
    
    for column in categories:
    # set each value to be the last character of the string
        categories[column] = categories[column] = categories[column].str.split('-').str[-1]
    # convert column from string to numeric
        categories[column] = pd.to_numeric(categories[column])
    #assert that all columns have values 0 or 1
        categories[column] = categories[column].apply(lambda x:1 if x>1 else x)
    # drop the original categories column from `df`
    df.drop('categories', axis=1, inplace=True)
    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df, categories], axis=1)
    # drop duplicates
    df.drop_duplicates(inplace=True)
    # remove nans based on original column (high number of nans)
    df = df[~(df.isnull().any(axis=1))|(df.original.isnull())]
    
    return df
    
def save_data(df, database_filename):
    
    """Saving cleaned dataframe into sql database file. 
    Input: df - cleaned dataframe
    database_filename: your given filename
    """
    engine = create_engine('sqlite:///' + database_filename)
    df.to_sql('DisasterResponse', engine, if_exists='replace', index=False)

    

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()