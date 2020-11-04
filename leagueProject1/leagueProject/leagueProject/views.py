from django.http import HttpResponse
from django.shortcuts import render
from collections import defaultdict
#from djongo import models
from riotwatcher import LolWatcher, ApiError
import pymongo

from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://wyatt6388:Verient2020!@lolmondodb.pu87h.mongodb.net/league_DB?ssl=true&ssl_cert_reqs=CERT_NONE")

db= cluster["league_DB"]

col = db["champs"]

gID = db["gameID"]

def add_record(champ_id, name, games, wins, opponents):
    post={"_id":champ_id, "name":name, "games":games,"wins": wins, "opponents": opponents}
    col.insert_one(post)
    
    #current_champ_list = lol_watcher.data_dragon.champions(champions_version)
def find_game(gameID):
    return gID.find({"_id":gameID})

def add_game(gameID):
    gID.insert_one({"_id": gameID})

def delete_record(champ_id):
    col.deleteOne({"champ_id":champ_id} )

def update_record_win(winner):
    col.update({"name":winner}, {"$inc":{"games":1, "wins":1}}, upsert=True)
    #col.update({"_id":winner, "opponents.id":loser}, {"$inc": {"opponents.$.games":1}}, {"$inc": {"opponents.$.wins":1}})

def update_record_lose(loser):
    col.update({"name":loser}, {"$inc":{"games":1}}, upsert=True)
    #col.update({"_id":loser, "opponents.id":winner}, {"$inc": {"opponents.$.games":1}} )

def getLOLinfo():
    lol_watcher = LolWatcher('RGAPI-9f463573-1130-4bd6-8926-9d153479293a')

    my_region = 'na1'

    me = lol_watcher.summoner.by_name(my_region, 'Alipoopoo')
    #print(me)

# all objects are returned (by default) as a dict
# lets see if i got diamond yet (i probably didnt)
    my_ranked_stats = lol_watcher.league.by_summoner(my_region, me['id'])
    return my_ranked_stats

# First we get the latest version of the game from data dragon
    #versions = lol_watcher.data_dragon.versions_for_region(my_region)
    #champions_version = versions['n']['champion']

def getMatchList():

    lol_watcher = LolWatcher('RGAPI-08461858-fd1b-4530-982c-32836a406836')

    my_region = 'na1'

    

    me = lol_watcher.summoner.by_name(my_region, 'Alipoopoo')

    matchL=lol_watcher.match.matchlist_by_account(my_region, me['accountId'])
    matchI=matchL['matches']
    #print(matchL)
    versions = lol_watcher.data_dragon.versions_for_region(my_region)
    champions_version = versions['n']['champion']

# Lets get some champions
    current_champ_list = lol_watcher.data_dragon.champions(champions_version)
    
    curr_champ=current_champ_list['data']

    #for key in curr_champ:
     #   print(key,": ", curr_champ[key])
    champ_info={}

    for key in curr_champ:
        champ_data=curr_champ[key]
        champ_info[int(champ_data['key'])]=champ_data['id']
    
    

    
    i=1

    champ_winrate=defaultdict(list)
    for m in matchI: 
        if m['queue']!=420 :
            continue
        if gID.find({"_id": m['gameId']}).count()!=0:
            continue
        add_game(m['gameId'])
        gameInfo=lol_watcher.match.by_id(my_region, m['gameId'])
        participants=gameInfo['participants']
        winners=[]
        losers=[]
        for p in participants:
            ch=p['championId']
            stats=p['stats']
            if stats['win']:
                winners.append(ch)
            else:
                losers.append(ch)
            #print(champ_info[ch])
            #print(stats['win'])
            
            if len(champ_winrate[champ_info[ch]])==0:
                if stats['win']:
                    champ_winrate[champ_info[ch]]=[1,1]
                else:
                    champ_winrate[champ_info[ch]]=[0,1]
            else:
                if stats['win']:
                    champ_winrate[champ_info[ch]][0]+=1
                    champ_winrate[champ_info[ch]][1]+=1
                else:
                    champ_winrate[champ_info[ch]][1]+=1
            
        print(winners)
        print(losers)
        
        for w in winners:
            #for l in losers:
            update_record_win(champ_info[w])
        for l in losers:
            #for w in winners:
            update_record_lose(champ_info[l])
        for w in winners:
            for l in losers:
                col.update({"_id":w, "opponents.id":l}, {"$inc": {"opponents.$.games":1,"opponents.$.wins":1}}, upsert=True)
        
    
        for l in losers:
            for w in winners:
                col.update({"_id":l, "opponents.id":w}, {"$inc": {"opponents.$.games":1}} , upsert=True)
    
        
        if i==5:
            break
        i+=1
        
    return curr_champ
    '''    
    print("champ winrates of most recent 50 ranked games: ")
    for k in champ_winrate:
        l=champ_winrate[k]
        print(k,": ",int(l[0]/l[1]*100),"%"," out of ", l[1], " games.")

        
        for key in curr_champ:
            champ_data=curr_champ[key]
            #print(champ_data['key'],": ",champ_data['id'])
            if int(champ_data['key'])== m['champion']:
                print(i,": ",champ_data['id'], ": ", team['win'])
                i+=1
   
    #print(current_champ_list)
    '''

def getChampCounters(champ):

    record= col.find_one({"_id":champ})
    arr=record["opponents"]
   
    res={}
    for p in arr:
        if p["wins"]==0:
            res[p["name"]]=0
        else:
            res[p["name"]]=p["wins"]/p["games"]
   
    sorted_orders=sorted(res.items(), key=lambda x:x[1], reverse=True)
    
    

    return sorted_orders


    



def about(request):
    #opponents=[{"id":103, "name":"Ahri", "games":1, "wins": 1}]
    #add_record(266, "Aatrox", 1, 1, opponents)
    #current_champ_list = lol_watcher.data_dragon.champions(champions_version)

    #add_record(15, "tripleGay", 13)
    #col.remove({})
    
    '''
    winner=[201, 245, 777, 17, 18]
    loser=[84, 106, 31, 50, 81]
    for w in winner:
        for l in loser:
            col.update({"_id":w, "opponents.id":l}, {"$inc": {"opponents.$.games":1,"opponents.$.wins":1}}, upsert=True)
        
    
    for l in loser:
        for w in winner:
            col.update({"_id":l, "opponents.id":w}, {"$inc": {"opponents.$.games":1}} , upsert=True)
    '''
    res=getChampCounters(32)

    for i in res:
        print(i[0],i[1])

    #add_record(255, "Ahri", 1, 1, opponents)
    #res=collection.find( {"champ_id":255} )
    #getMatchList()
    
    #return HttpResponse(getMatchList())
    return HttpResponse(res)
    #return render(request, 'about.html')
#    return HttpResponse('about')


def homepage(request):
    return render(request, 'homepage.html')
 #   return HttpResponse('homepage')