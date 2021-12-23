from urllib.request import urlopen
from bs4 import  BeautifulSoup
import json
import requests
import pandas as pd

headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
          
          "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}

def connect(url,headers):
        try:
            req = requests.get(url,timeout=30,headers=headers)
            req_json = req.json()
            return req_json
        except requests.ConnectionError as e:
            print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
            print(str(e))            
            #renewIPadress()
            #continue
        except requests.Timeout as e:
            print("OOPS!! Timeout Error")
            print(str(e))
            #renewIPadress()
            #continue
        except requests.RequestException as e:
            print("OOPS!! General Error")
            print(str(e))
            #renewIPadress()
            #continue
        except KeyboardInterrupt:
            print("Someone closed the program")

def sportpesa():
  print('Downloading sportpesa data...')
  print()
  sportpesa_lst = []
  team_id_lst = []

  api_page = 1

  while True:
      api_url = f'https://www.ke.sportpesa.com/api/todays/1/games?type=prematch&section=today&markets_layout=multiple&o=startTime&pag_count=15&pag_min={api_page}'
      full_data = connect(api_url,headers)
      data_length = len(full_data)
      if data_length == 0:
          break
      
      for data in full_data:
          team_id = data.get('id')
          home_team = data.get('competitors')[0].get('name')
          away_team = data.get('competitors')[1].get('name')
          date = data.get("date").split("T")[1]
          home_win = data.get('markets')[0].get('selections')[0].get('odds')
          draw_ = data.get('markets')[0].get('selections')[1].get('odds')
          away_win = data.get('markets')[0].get('selections')[2].get('odds')
          url_2 = f'https://www.ke.sportpesa.com/api/games/markets?games={team_id}&markets=all'
          team_id_str = f'{team_id}'


          markets_ = connect(url_2,headers=headers)
          odds_ = markets_.get(team_id_str)
          odds_len = len(odds_)
          GG_ = 'NA'
          NGG_ = 'NA'
          over_ = 'NA'
          under_ = 'NA'
          for i in range(1,odds_len):
              if odds_[i].get('name') == "Both Teams To Score":
                  GG_ = odds_[i].get('selections')[0].get('odds')
                  NGG_ = odds_[i].get('selections')[1].get('odds')
                      #print(NGG_)

              if odds_[i].get('name')== "Total Goals Over/Under - Full Time" and odds_[i].get('selections')[0].get('name') == 'OVER 2.50':
                  over_ = odds_[i].get('selections')[0].get('odds')
                  under_ = odds_[i].get('selections')[1].get('odds')

          team_dic = {'team id':team_id,'home team':home_team,'away team':away_team,'date':date,'home win':home_win,'draw':draw_,'away win':away_win,'gg':GG_,'ngg':NGG_,'over 2.5':over_,'under 2.5':under_}

          sportpesa_lst.append(team_dic)
      api_page = api_page + 15   

  sportpesa_df = pd.DataFrame(sportpesa_lst)
  return sportpesa_df
 
def sportybet():
  print("Downloading Sportybet data....")
  print()
  sporty_lst = []

  id_lst = [(1,1621759762164),(2,1621759941083),(3,1621760129060),(4,1621760417314),(5,1621760503181)]

  for page_num,page_id in id_lst:
      url = f'https://www.sportybet.com/api/ke/factsCenter/pcUpcomingEvents?sportId=sr%3Asport%3A1&marketId=1%2C18%2C10%2C29%2C11%2C26%2C36%2C14&pageSize=100&pageNum={page_num}&todayGames=true&_t={page_id}' 
    
      data = connect(url,headers) 
      tournaments_ = data.get('data')
    
      if len(tournaments_) != 0:
          tournaments = tournaments_.get('tournaments')     
          for tournament in tournaments:
              events = tournament.get('events')
              for teams in events:
                  home_team = teams.get('homeTeamName')
                  away_team = teams.get('awayTeamName')
                  markets = teams.get('markets')  
                  hdw_ = markets[0].get('outcomes')
                  home = hdw_[0].get('odds')
                  draw = hdw_[1].get('odds')
                  away = hdw_[2].get('odds')
                  
                  over = 'NA'
                  under = 'NA'
                  gg = 'NA'
                  ngg = 'NA'
                  for i in range(1,15):
                      try:
                          ovun = markets[i].get('outcomes')[0].get('desc')  

                          if ovun == 'Over 2.5':
                              over = markets[i].get('outcomes')[0].get('odds')
                              under = markets[i].get('outcomes')[1].get('odds')

                          ygg = markets[i].get('desc')    
                          if ygg == 'GG/NG':
                              gg = markets[i].get('outcomes')[0].get('odds')
                              ngg = markets[i].get('outcomes')[1].get('odds')                    
                      except IndexError:
                          pass
                  team_dic = {"home team":home_team,"away team":away_team,"home win":home,"draw":draw,"away win":away,"over 2.5":over,"under 2.5":under,"gg":gg,"ngg":ngg}

                  sporty_lst.append(team_dic) 
              
  sporty_df = pd.DataFrame(sporty_lst) 
  return sporty_df

def betika():
  sportpesa_df = sportpesa()
  print("Downloading Betika Data....")
  print()
  betika_lst = []
  page_number = 1
  max_page_number = (len(sportpesa_df)//10) + 2
  while page_number <= max_page_number:
      betika_api_url = f'https://api.betika.com/v1/uo/matches?page={page_number}&limit=10&tab=&sub_type_id=1,186&sport_id=14&tag_id=&sort_id=1&period_id=-1&esports=false'
      betika_data = connect(betika_api_url,headers)

      page_data = betika_data.get('data')
      for data in page_data:
          home_team = data.get("home_team")
          match_id = data.get("match_id")
          away_team = data.get("away_team")
          home_odd = data.get("home_odd")
          draw_odd = data.get("neutral_odd")
          away_odd = data.get("away_odd")
          gg = 'NA'
          ngg = 'NA'
          over = 'NA'
          under = 'NA'
          
          other_mkts_url = f'https://api.betika.com/v1/uo/match?id={match_id}'
          other_mkts_data = connect(other_mkts_url,headers)
          mkts_data = other_mkts_data.get('data')
          if mkts_data is not None:
              for mkt_data in mkts_data:
                  mkt_name = mkt_data.get('name')
                  if mkt_name == 'BOTH TEAMS TO SCORE (GG/NG)':
                      odds = mkt_data.get('odds')
                      gg = odds[0].get("odd_value")
                      ngg = odds[1].get('odd_value')

                  if mkt_name == 'TOTAL':
                      odds = mkt_data.get('odds')
                      for odd in odds:
                          display = odd.get("display")
                          if display == 'OVER 2.5':
                              over = odd.get("odd_value")
                              #print(over)
                          if display == 'UNDER 2.5':
                              under = odd.get('odd_value')
                              #print(under)
          team_dic = {'home team':home_team,'away team':away_team,'home win':home_odd,'draw':draw_odd,'away win':away_odd,'gg':gg,'ngg':ngg,'over 2.5':over,'under 2.5':under}
          betika_lst.append(team_dic)
      page_number += 1   

  betika_df = pd.DataFrame(betika_lst)
  return sportpesa_df,betika_df

def save_to_csv():
  sport_bet = betika()
  sportpesa_df = sport_bet[0]
  betika_df = sport_bet[1]
  sporty_df = sportybet()
  sportpesa_df.to_csv('sportpesa.csv')
  sporty_df.to_csv('sportybet.csv')
  betika_df.to_csv('betika.csv')
  print('Saving Downloaded files to csv....')
  print()
  print("All Files Successfully Saved")

save_to_csv()  