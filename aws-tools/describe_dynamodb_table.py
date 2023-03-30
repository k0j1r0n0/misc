# -*- coding: utf-8 -*-
"""
- Script Name: describe_dynamodb_table.py
- Author: @k0j1r0n0
- Date: March 30, 2023
- Description
  - This script is to get the configuration of a DynamoDB table using AWS SDK for Python (Boto3)
    and save the result as a JSON file.
    Make sure that you can use Python3 on your CLI.
"""
import argparse
import boto3
import json
from datetime import date, datetime

result_file_path = "./results/dynamodb_config.json"

def parse_dynamodb_parameters():
    parser = argparse.ArgumentParser(
                 prog = "describe_dynamodb_table.py",
                 description = "Get the configuration of the DynamoDB table that you specified",
                 epilog = "end",
                 add_help = True,
             )
    parser.add_argument("--table", type = str, required = True, help = "DynamoDB table name (type: str)")
    parser.add_argument("--profile", type = str, required = True, help = "AWS named profile that is a collection of settings and credentials (type: str)")
    args = parser.parse_args()
    table = args.table
    profile = args.profile

    return table, profile

def json_serial(object):
    #---- transform datetime/date -> isoformat ------------------------#
    if isinstance(object, (datetime, date)):
        return object.isoformat()
    raise TypeError (f"Object of type {object} is not serializable.")

if __name__ == "__main__":
    table, profile = parse_dynamodb_parameters()
    print("[Target DynamoDB Table]")
    print(f"  - {table} (profile: {profile})")
    print("------------------------------------------------------------")
    
    session = boto3.Session(profile_name = profile)
    dynamodb = session.client("dynamodb")
    
    #---- get DynamoDB table configuration -------------------------------------------------------#
    print("Loading the DynamoDB table...")
    response = dynamodb.describe_table(TableName = table)    # type: dict
    #item_number = response.get("Table").get("ItemCount")
    #print(f"ItemCount: {item_number}")
    
    #---- save a result file (.json) -------------------------------------------------------------#
    with open(result_file_path, "w") as file:
        json.dump(response, indent = 4, fp = file, default = json_serial, ensure_ascii = False)
    print("------------------------------------------------------------")
    print("[Output File]")
    print(f"  - {result_file_path}")
    print("Done.")