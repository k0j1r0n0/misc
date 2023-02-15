# -*- coding: utf-8 -*-
"""
- Script: generate_best_standings.py
- Author: @k0j1r0n0
- Date: February 8, 2023 (last updated: February 15, 2023)
- Description
  - For specific AtCoder contests, you can filter the contest results
    by participants' affiliation and generate standings (.json and .html).
    (Note that an AtCoder account is required.)
  - Output files are as follows:
    - ./json/{contest_id}_filtered.json
    - ./html/best_standings.html
      (the standings of the selected AtCoder contests)
"""
import argparse
import json
import pandas as pd
import pwinput
import re
import requests
import sys
import textwrap
import urllib.parse
from time import sleep

json_dir = "./json"
html_dir = "./html"
css_path = "../standings.css"
standings_title = "Standings Title"
atcoder_login_url = "https://atcoder.jp/login"

#----- take arguments from the command line --------------------#
parser = argparse.ArgumentParser()
parser.add_argument("-a", "--affiliation")
parser.add_argument("-c", "--contest_id", nargs = "+")    # accept one ore more arguments
parser.add_argument("-u", "--username")
parser.add_argument("-t", "--title", default = standings_title)
args = parser.parse_args()

def login_to_atcoder(username, password):
    session = requests.session()
    response = session.get(atcoder_login_url)                       # access with GET method to get cookies
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
    try:
        response = session.post(atcoder_login_url, headers = headers, params = login_data)    # log in to AtCoder
        response.raise_for_status()    # detect 4xx/5xx status code
    except requests.exceptions.RequestException as e:
        sys.exit("Error: ", e)
    print("Successfully logged in to Atcoder!")
    
    return session

def filter_by_affiliation(contest_id, affiliation, standings_data):
    userinfo_list = []
    users_number = len(standings_data)

    for user_index in range(0, users_number):
        if standings_data[user_index]["Affiliation"] == affiliation:
            username = standings_data[user_index]["UserName"]
            total_score = int(standings_data[user_index]["TotalResult"]["Score"] / 100)
            userinfo_list.append({"UserName": username, "TotalScore": total_score, "ContestId": contest_id})
    
    new_standings_data = {"UserInfo": userinfo_list}    # type: dict
    with open(f"{json_dir}/{contest_id}_filtered.json", "w") as file:
        json.dump(new_standings_data, fp = file, ensure_ascii = False, indent = 2)
    
    return new_standings_data

def update_best_score(contests_number, standings_data):
    reference_userinfo = standings_data[0]["UserInfo"]

    for contest_index in range(1, contests_number):    # contest_index = 0 is for the reference
        userinfo = standings_data[contest_index]["UserInfo"]    # type: list
        users_number = len(userinfo)

        for user_index in range(0, users_number):
            username = userinfo[user_index]["UserName"]
            total_score = userinfo[user_index]["TotalScore"]
            contest_id = userinfo[user_index]["ContestId"]
            
            #----- check if the same username already exists --------------------------#
            existsUserName = False
            reference_username_index = 0
            for item in reference_userinfo:
                reference_username = item.get("UserName")
                reference_total_score = item.get("TotalScore")
                
                if username == reference_username:
                    existsUserName = True
                    #----- update the TotalScore and the ContestId -------------------------------#
                    if total_score > reference_total_score:
                        standings_data[0]["UserInfo"][reference_username_index]["TotalScore"] = total_score
                        standings_data[0]["UserInfo"][reference_username_index]["ContestId"] = contest_id
                    break
                reference_username_index += 1
            if existsUserName == False:
                standings_data[0]["UserInfo"].append({"UserName": username, "TotalScore": total_score, "ContestId": contest_id})
    
    #----- sort by "Rank" and then by "UserName" --------------------------#
    userinfo = pd.DataFrame(standings_data[0]["UserInfo"])
    userinfo = pd.concat([userinfo, userinfo.rank(ascending = False, method = "min")], axis = 1)
    userinfo = userinfo.iloc[:, [0, 1, 2, 4]]
    userinfo = userinfo.set_axis(["UserName", "TotalScore", "ContestId", "Rank"], axis = 1)
    userinfo = userinfo.sort_values(["Rank", "UserName"])
    userinfo = userinfo.reset_index(drop = True)

    userinfo_list = []
    for user_index in range(0, len(userinfo["UserName"])):
        userinfo_list.append({"UserName": str(userinfo["UserName"][user_index]), "TotalScore": str(userinfo["TotalScore"][user_index]), "ContestId": str(userinfo["ContestId"][user_index]), "Rank": int(userinfo["Rank"][user_index])})
    new_standings_data = {"UserInfo": userinfo_list}    # type: dict
    with open(f"{json_dir}/best_standings.json", "w") as file:
        json.dump(new_standings_data, fp = file, ensure_ascii = False, indent = 2)
    
    return new_standings_data

def generate_standings_html(title, contests_id, affiliation, standings_data):
    user_data = standings_data["UserInfo"]
    users_number = len(user_data)
    
    #----- header -----------------------------------------------------------------#
    headers = ["順位", "ユーザ", "総得点（最大値）"]
    header_html =  "<thead>\n"
    header_html += "  <tr>\n"
    for header in headers:
        header_html += f"    <th>{header}</th>\n"
    header_html += "  </tr>\n"
    header_html += "</thead>\n"
    header_html = textwrap.indent(header_html, "      ")

    #----- table ------------------------------------------------------------------#
    table_html =  "<tbody>\n"
    for user_index in range(users_number):
        table_html += "  <tr>\n"
        username = user_data[user_index].get("UserName")
        total_score = user_data[user_index].get("TotalScore")
        contest_id = user_data[user_index].get("ContestId")
        contest_url = f"https://atcoder.jp/contests/{contest_id}"
        rank = user_data[user_index].get("Rank")

        table_html +=  f"    <td>{rank}</td>\n"
        td_id = ""
        if rank == 1:
            td_id = "first"
        elif rank == 2:
            td_id = "second"
        elif rank == 3:
            td_id = "third"
        table_html +=  f'    <td id="{td_id}">{username}</td>\n'
        table_html +=  f'    <td>{total_score}<div class="contest_id">(<a href={contest_url} target="_blank" rel="noopener noreferrer">{contest_id}</a>)</td>\n'
        table_html += "  </tr>\n"
    table_html += "</tbody>\n"
    table_html = textwrap.indent(table_html, "      ")

    #----- combine into one html text ---------------------------------------------#
    contests_label = ", ".join(map(str, contests_id))
    standings_html = f"""
                      <!DOCTYPE html>
                      <html lang="ja">
                        <head>
                          <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                          <link href="{css_path}" rel="stylesheet" type="text/css" media="all">
                        </head>
                        <body>
                          <h1>{title}</h1>
                          <h2>コンテスト情報</h2>
                          <div>
                            <ul>
                              <li>対象コンテスト：{contests_label}</li>
                              <li>参加者総数：{users_number}名</li>
                            </ul>
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

    with open(f"{html_dir}/best_standings.html", "w") as file:
        file.write(standings_html)

if __name__ == "__main__":
    #----- log in to AtCoder ----------------------------------------------------#
    print("[Enter login information]")
    login_username = args.username
    if login_username != None:
        print("  Username: %s" % login_username)
    else:
        login_username = input("  Username: ")
    login_password = pwinput.pwinput(prompt = "  Password: ")
    session = login_to_atcoder(login_username, login_password)

    #----- enter basic infomation to get contest results ------------------------#
    print("--------------------------------------------------")
    print("[Enter the following basic information]")
    contests_id = args.contest_id
    if contests_id != None:
        print("  Contest ID: " + " ".join(map(str, contests_id)))
    else:
        contests_id = list(map(str, input("  Contest ID: ").split()))
    affiliation = args.affiliation
    if affiliation != None:
        print("  Affiliation: %s" % affiliation)
    else:
        affiliation = input("  Affiliation: ")
    
    standings_url = [f"https://atcoder.jp/contests/{id}/standings/json" for id in contests_id]
    json_filepath = [f"{json_dir}/{id}.json" for id in contests_id]
    
    #----- prepare the standings data and generate json and html files ----------#
    title = args.title
    new_standings_all_data = []
    standings_url_number = len(standings_url)
    try:
        for url_index in range(0, standings_url_number):
            url = standings_url[url_index]
            print(f'Retrieving standings data from "{url}"...')
            standings_data = session.get(url).text
            #sleep(1)
            new_standings_data = filter_by_affiliation(contests_id[url_index], affiliation, json.loads(standings_data)["StandingsData"])
            new_standings_all_data.append(new_standings_data)

        updated_standings_data = update_best_score(len(contests_id), new_standings_all_data)
        print("Generating json and html files...")
        generate_standings_html(title, contests_id, affiliation, updated_standings_data)
    except requests.exceptions.RequestException as e:
        sys.exit("Could not retrieve the standings data (.json) of the contest. Try again.")

    #----- show the information of output files ---------------------------------#
    print("--------------------------------------------------")
    print("[Output]")
    for contest_id in contests_id:
        print(f"  - {json_dir}/{contest_id}_filtered.json")
    print(f"  - {json_dir}/best_standings.json")
    print(f"  - {html_dir}/best_standings.html")
    print("Done.")