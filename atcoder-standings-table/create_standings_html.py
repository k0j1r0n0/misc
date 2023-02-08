# -*- coding: utf-8 -*-
"""
- Script: create_standings_html.py
- Author: @k0j1r0n0
- Date: February 3, 2023 (last updated: February 8, 2023)
- Description
  - For a specific AtCoder contest, you can filter results by affiliation 
    and output a table of results. (Note that an AtCoder account is required.)
  - Output files are as follows:
    - ./json/{contest_id}.json
    - ./html/{contest_id}.html (the standings of the selected AtCoder contest)
"""

import datetime
import json
import pwinput
import re
import requests
import sys
import textwrap
import urllib.parse
from bs4 import BeautifulSoup
from time import sleep

login_url = "https://atcoder.jp/login"
json_dir = "./json"
html_dir = "./html"
css_path = "../standings.css"

def login(username, password):
    session = requests.session()
    response = session.get(login_url)                               # access with GET to get cookies
    revel_session = response.cookies.get_dict()["REVEL_SESSION"]    # get the cookie "REVEL_SESSION"
    revel_session = urllib.parse.unquote(revel_session)             # decode "revel_session"
    
    try:
        csrf_token = re.search(r"csrf_token\:(.*)_TS", revel_session).groups()[0].replace("\x00\x00", "")    # randomly generated CSRF token when accessing login page (sometimes "AttributeError" occurs, then re-run the script when the error occurs)
        sleep(1)
    except AttributeError:
        sys.exit("Could not retrieve csrf_token from the web page. Try again.")
    headers = {"content-type": "application/x-www-form-urlencoded"}
    login_data = {
      "username": username,
      "password": password,
      "csrf_token": csrf_token,
    }
    data = {
      "continue": "https://atcoder.jp/"
    }
    try:
        response = session.post(login_url, headers = headers, params = login_data, data = data)
    except requests.exceptions.RequestException as e:
        sys.exit("Requests error: ", e)
    print("Successfully logged in to Atcoder!")
    
    return session

def arrange_standings_html(contest_id, affiliation, standings_all_json):
    standings_data = standings_all_json["StandingsData"]
    problems_data = standings_all_json["TaskInfo"]
    participants_number = len(standings_data)
    problems_number = len(problems_data)
    problems_urls =  [f"https://atcoder.jp/contests/{contest_id}/tasks/{contest_id}_" + chr(i + 97) for i in range(0, problems_number)]
    
    #----- retrieve the contest date and time --------------------------------------------------#
    contest_url = f"https://atcoder.jp/contests/{contest_id}/"
    soup = BeautifulSoup(urllib.request.urlopen(contest_url), "html.parser")
    contest_title = soup.title.string
    contest_datetime = soup.find_all("time", class_ = "fixtime fixtime-full")    # refer to the tag <time class="fixtime fixtime-full"> to get the AtCoder contest date
    time_format = "%Y/%m/%d %H:%M"
    contest_start_time = datetime.datetime.strptime(contest_datetime[0].string, "%Y-%m-%d %H:%M:%S%z").strftime(time_format)    # e.g. 2023-01-01 23:59:59+09:00 -> 2023/01/01 23:59:59
    contest_end_time = datetime.datetime.strptime(contest_datetime[1].string, "%Y-%m-%d %H:%M:%S%z").strftime(time_format)
    
    #----- prepare table header html texts -----------------------------------------------------#
    headers = ["順位", "ユーザ", "総得点"]
    for i in range(0, problems_number):
        headers.append(chr(i + 65))    # e.g. i = 0 -> A, i = 1 -> B, ...
    header_html =  "<thead>\n"
    header_html += "  <tr>\n"
    for header_index in range(len(headers)):
        if header_index <= 2:
            header_html += f"    <th>{headers[header_index]}</th>\n"
        else:
            header_html += f'    <th><a href="{problems_urls[header_index - 3]}" target="_blank" rel="noopener noreferrer">{headers[header_index]}</a></th>\n'
    header_html += "  </tr>\n"
    header_html += "</thead>\n"
    header_html = textwrap.indent(header_html, "      ")
    
    #----- prepare table html texts ------------------------------------------------------------#
    table_html = "<tbody>\n"
    filtered_json_filepath = f"{json_dir}/{contest_id}_filtered.json"
    with open(filtered_json_filepath, "w") as f:
        print("")    # create an empty file
    for participant_index in range(0, participants_number):
        if standings_data[participant_index]["Affiliation"] == affiliation:
            with open(filtered_json_filepath, "a") as f:    # save filtered standings json data
                json.dump(standings_data[participant_index], fp = f, ensure_ascii = False, indent = 2)

            contents = []
            rank = standings_data[participant_index]["Rank"]
            username = standings_data[participant_index]["UserName"]
            total_score = int(standings_data[participant_index]["TotalResult"]["Score"] / 100)
            total_elapsed = standings_data[participant_index]["TotalResult"]["Elapsed"]    # nano second
            total_elapsed_hhmmss = str(datetime.timedelta(microseconds = total_elapsed * 1.0e-3))
            contents = [rank, username, total_score, total_elapsed_hhmmss]

            #----- get score and time for each problem ------------------------------#
            for problem_number in range(0, problems_number):
                problem_name = contest_id + "_" + chr(problem_number + 97)
                user_task_results_each_problem = standings_data[participant_index]["TaskResults"].get(problem_name)    # if the data doesn't exist, return None using get method
                if user_task_results_each_problem != None:
                    score = user_task_results_each_problem["Score"]
                    time = user_task_results_each_problem["Elapsed"]
                    contents.append(int(score * 1.0e-2))                                      # score
                    contents.append(str(datetime.timedelta(microseconds = time * 1.0e-3)))    # time
                else:
                    contents += ["-", "-"]

            #----- format html texts ------------------------------------------------#
            table_html += "  <tr>\n"
            for header_index in range(len(headers)):
                if header_index <= 1:
                    table_html +=  f"    <td>{contents[header_index]}</td>\n"
                else:
                    score, time = contents[2 * header_index - 2], contents[2 * header_index - 1]
                    if score == 0 or time == "0:00:00" or score == "-" or time == "-":
                        table_html += "    <td>-</td>\n"
                    elif score != "-":
                        if header_index == 2:
                            table_html +=  f'    <td><div class="total-score">{score}</div><div class="time">{time}</font></td>\n'
                        else:
                            table_html +=  f'    <td><div class="score">{score}</div><div class="time">{time}</div></td>\n'
            table_html += "  </tr>\n"
    table_html += "</tbody>\n"
    table_html = textwrap.indent(table_html, "      ")
    
    #----- combine into one html text ----------------------------------------------------------#
    standings_html = f"""
                      <!DOCTYPE html>
                      <html lang="ja">
                        <head>
                          <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                          <link href="{css_path}" rel="stylesheet" type="text/css" media="all">
                        </head>
                        <body>
                          <h1>{contest_title}</h1>
                          <h2>コンテスト情報</h2>
                          <div>
                            <ul>
                              <li>開催日時：{contest_start_time} - {contest_end_time}</li>
                              <li>参加者総数：{participants_number}名</li>
                            </ul>
                            ※詳細は<a href="{contest_url}" target="_blank" rel="noopener noreferrer">公式ページ</a>を参照のこと。
                          </div>
                          <h2>ランキング表（所属：{affiliation}）</h2>
                          <table class="stripe-table">\n
                      """
    standings_html = textwrap.dedent(standings_html)[1:-1]
    standings_html += header_html
    standings_html += table_html
    standings_html += "    </table>\n"
    standings_html += "  </body>\n"
    standings_html += "</html>"
    
    return standings_html

if __name__ == "__main__":
    #----- log in to AtCoder --------------------------------------------------#
    print("[Enter login information]")
    login_username = input("  Username: ")
    login_password = pwinput.pwinput(prompt = "  Password: ")
    session = login(login_username, login_password)
    
    #----- enter basic infomation to get the certain contest results ----------#
    print("--------------------------------------------------")
    print("[Enter the following basic information]")
    contest_id = input("  Contest ID: ")
    affiliation = input("  Affiliation: ")
    standings_url = f"https://atcoder.jp/contests/{contest_id}/standings/json"
    
    json_filepath = f"{json_dir}/{contest_id}.json"    
    try:
        standings_all_data = session.get(standings_url).text
        with open(json_filepath, "w") as f:    # save the all standings data of the specific contest
            json.dump(json.loads(standings_all_data), fp = f, ensure_ascii = False, indent = 2)
    except requests.exceptions.RequestException as e:
        sys.exit("Could not retrieve the ranking data (.json) of the contest. Try again.")

    print("Generating files...")
    standings_all_json = json.loads(standings_all_data)
    arranged_standings_html = arrange_standings_html(contest_id, affiliation, standings_all_json)

    html_filepath = f"{html_dir}/{contest_id}.html"
    with open(html_filepath, "w") as f:
        print(arranged_standings_html, file = f)
    print("--------------------------------------------------")
    print("[Output]")
    print("  (1) %s" % html_filepath)
    print("  (2) %s" % json_filepath)
    print("Done.")