import numpy as np
import pandas as pd
import sys
from datetime import timedelta

import pandas as pd
try:
    import cpickle as pickle
except:
    import pickle







def initializeDataset(noDays,keepCurrent=False):
	data=pd.read_csv("data.csv")
	data['Date']=pd.to_datetime(data['Date'].apply(str), format='%Y%m%d')
	date_to_run=pd.to_datetime('today')-timedelta(days=noDays)
	if(not keepCurrent):
		data=data.loc[data['Date']<date_to_run]
	if date_to_run.day != pd.datetime.today().day:
		data=data.loc[data['active']==1]
	return data,date_to_run


def generateStatline(data):
	for index,row in data.iterrows():
		stats=str(row['Stats']).split()
		for stat in stats:
			if 'pt' in stat:
				data.at[index,'Points']=float(stat[:-2])
			if 'rb' in stat:
				data.at[index,'Rebounds']=float(stat[:-2])
			if 'as' in stat:
				data.at[index,'Assists']=float(stat[:-2])
			if 'st' in stat:
				data.at[index,'Steals']=float(stat[:-2])
			if 'bl' in stat:
				data.at[index,'Blocks']=float(stat[:-2])
			if 'to' in stat:
				data.at[index,'Turnovers']=float(stat[:-2])
	return data

def getAveragesInTimeFrame(data,date_to_run, days, stats_column, rename,var=False):
	if(var):
		return data[(data['Date']>(date_to_run-timedelta(days=days))) &(data['Date']<date_to_run)].groupby('First  Last')[stats_column].var().to_frame().rename(columns = {stats_column:rename}, inplace = False)
	else:
		
		return data[(data['Date']>(date_to_run-timedelta(days=days))) &(data['Date']<date_to_run)].groupby('First  Last')[stats_column].mean().to_frame().rename(columns = {stats_column:rename}, inplace = False)



def getTotalAverages(data,date_to_run, stats_column, rename,var=False):
	if(var):
		return data[data['Date']<date_to_run].groupby('First  Last')[stats_column].var().to_frame().rename(columns = {stats_column:rename}, inplace = False)
	else:
		return data[data['Date']<date_to_run].groupby('First  Last')[stats_column].mean().to_frame().rename(columns = {stats_column:rename}, inplace = False)


def getAveragesHomeAway(data, date_to_run,rename,homeaway,var=False):
	if(var):
		return data[(data['H/A']==homeaway)&(data['Date']<date_to_run)].groupby('First  Last')['FDP'].var().to_frame().rename(columns = {'FDP':rename}, inplace = False)
	else:
		return data[(data['H/A']==homeaway)&(data['Date']<date_to_run)].groupby('First  Last')['FDP'].mean().to_frame().rename(columns = {'FDP':rename}, inplace = False)



def addAveragesHomeAway(originalData, date_to_run,newData):
	avg_h=getAveragesHomeAway(originalData, date_to_run,'fdp mean home',"H",var=False)
	avg_a=getAveragesHomeAway(originalData, date_to_run,'fdp mean away',"A",var=False)
	
	var_h=getAveragesHomeAway(originalData, date_to_run,'fdp var home',"A",var=True)
	var_a=getAveragesHomeAway(originalData, date_to_run,'fdp var away',"A",var=True)

	avg_h_15=originalData[(originalData['H/A']=="H") & (originalData['Date']>(date_to_run-timedelta(days=15)))&(originalData['Date']<date_to_run)].groupby('First  Last')['FDP'].mean().to_frame().rename(columns = {'FDP':'fdp _mean_home_15'}, inplace = False)
	avg_a_15=originalData[(originalData['H/A']=="A") & (originalData['Date']>(date_to_run-timedelta(days=15)))&(originalData['Date']<date_to_run)].groupby('First  Last')['FDP'].mean().to_frame().rename(columns = {'FDP':'fdp_mean_away_15'}, inplace = False)


	for index, row in newData.iterrows():
		try:
			if(row['H/A']=='H'):
				newData.at[index, 'HA_mean']=avg_h.at[index,'fdp mean home']
				newData.at[index,'HA_var']=var_h.at[index,'fdp var home']
				newData.at[index,'HA_mean_15']=avg_h_15.at[index,'fdp _mean_home_15']
				newData.at[index,'HA_bool']="1"
			elif(row['H/A']=='A'):
				newData.at[index,'HA_mean']=avg_a.at[index, 'fdp mean away']
				newData.at[index,'HA_var']=var_a.at[index,'fdp var away']
				newData.at[index,'HA_mean_15']=avg_a_15.at[index,'fdp_mean_away_15']
				newData.at[index,'HA_bool']="0"
		except:
			"FAILED"
	return newData


def getTeamAndOpponentStats(data,date_to_run, newData):
	player_team=data.groupby('First  Last')['Team'].unique().to_frame()
	for index, row in player_team.iterrows():
	   row['Team']=row['Team'][0]

	g = data.drop_duplicates(subset=['Team', 'GameID', 'Date'])

	team_avg_pts=g[g['Date']<date_to_run].groupby('Team')['Team pts'].mean()
	team_var_pts=g[g['Date']<date_to_run].groupby('Team')['Team pts'].var()
	team_avg_pts_30=g[(g['Date']>(date_to_run-timedelta(days=30)))&(g['Date']<date_to_run)].groupby('Team')['Team pts'].mean()
	team_var_pts_30=g[(g['Date']>(date_to_run-timedelta(days=30)))&(g['Date']<date_to_run)].groupby('Team')['Team pts'].var()
	team_avg_pts_15=g[(g['Date']>(date_to_run-timedelta(days=15)))&(g['Date']<date_to_run)].groupby('Team')['Team pts'].mean()
	team_var_pts_15=g[(g['Date']>(date_to_run-timedelta(days=15)))&(g['Date']<date_to_run)].groupby('Team')['Team pts'].var()

	team_oppt_avg_pts=g[g['Date']<date_to_run].groupby('Team')['Opp pts'].mean()
	team_oppt_var_pts=g[g['Date']<date_to_run].groupby('Team')['Opp pts'].var()
	team_oppt_avg_pts_30=g[(g['Date']>(date_to_run-timedelta(days=30)))&(g['Date']<date_to_run)].groupby('Team')['Opp pts'].mean()
	team_oppt_var_pts_30=g[(g['Date']>(date_to_run-timedelta(days=30)))&(g['Date']<date_to_run)].groupby('Team')['Opp pts'].var()	
	team_oppt_avg_pts_15=g[(g['Date']>(date_to_run-timedelta(days=15)))&(g['Date']<date_to_run)].groupby('Team')['Opp pts'].mean()
	team_oppt_var_pts_15=g[(g['Date']>(date_to_run-timedelta(days=15)))&(g['Date']<date_to_run)].groupby('Team')['Opp pts'].var()


	for index, row in player_team.iterrows():
		player_team.at[index, 'team_avg_pts']=team_avg_pts[row['Team']]
		player_team.at[index, 'team_var_pts']=team_var_pts[row['Team']]
		player_team.at[index, 'team_avg_pts_30']=team_avg_pts_30[row['Team']]
		player_team.at[index, 'team_var_pts_30']=team_var_pts_30[row['Team']]
		player_team.at[index, 'team_avg_pts_15']=team_avg_pts_15[row['Team']]
		player_team.at[index, 'team_var_pts_15']=team_var_pts_15[row['Team']]


	player_team_opp=data[data['Date']==date_to_run.strftime('%Y%m%d')].groupby('First  Last')['Opp'].unique().to_frame()
	for index, row in player_team_opp.iterrows():
	   row['Opp']=row['Opp'][0]

	for index, row in player_team_opp.iterrows():
		player_team_opp.at[index, 'team_oppt_avg_pts']=team_oppt_avg_pts[row['Opp']]
		player_team_opp.at[index, 'team_oppt_var_pts']=team_oppt_var_pts[row['Opp']]
		player_team_opp.at[index, 'team_oppt_avg_pts_30']=team_oppt_avg_pts_30[row['Opp']]
		player_team_opp.at[index, 'team_oppt_var_pts_30']=team_oppt_var_pts_30[row['Opp']]
		player_team_opp.at[index, 'team_oppt_avg_pts_15']=team_oppt_avg_pts_15[row['Opp']]
		player_team_opp.at[index, 'team_oppt_var_pts_15']=team_oppt_var_pts_15[row['Opp']]

	newData=pd.merge(newData,player_team, left_index = True, right_index=True)
	newData=pd.merge(newData, player_team_opp, left_index = True, right_index=True)
	return newData



def generateData(noDays, train=False):

	originalData,date_to_run=initializeDataset(noDays)

	originalData=generateStatline(originalData)

	newData=pd.merge(getTotalAverages(originalData,date_to_run,'FDP','fdp mean'), getTotalAverages(originalData,date_to_run,'FDP','fdp var', True), left_index = True, right_index=True)
	newData=pd.merge(newData,getTotalAverages(originalData,date_to_run,'Points','Total_Pts') , left_index = True, right_index=True)
	newData=pd.merge(newData, getTotalAverages(originalData,date_to_run,'Rebounds','Total_Rb'), left_index = True, right_index=True)
	newData=pd.merge(newData, getTotalAverages(originalData,date_to_run,'Assists','Total_As'), left_index = True, right_index=True)
	newData=pd.merge(newData, getTotalAverages(originalData,date_to_run,'Steals','Total_St'), left_index = True, right_index=True)
	newData=pd.merge(newData, getTotalAverages(originalData,date_to_run,'Blocks','Total_Bl'), left_index = True, right_index=True)
	newData=pd.merge(newData, getTotalAverages(originalData,date_to_run,'Turnovers','Total_TO'), left_index = True, right_index=True)

	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,20,'FDP','fdp mean_20'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,20,'FDP','fdp var_20',True), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,20,'Points','20_Pts'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,20,'Assists','20_As'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,20,'Rebounds','20_Rb'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,20,'Steals','20_St'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,20,'Blocks','20_Bl'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,20,'Turnovers','20_To'), left_index = True, right_index=True)

	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,10,'FDP','fdp mean_10'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,10,'FDP','fdp var_10',True), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,10,'Points','10_Pts'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,10,'Assists','10_As'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,10,'Rebounds','10_Rb'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,10,'Steals','10_St'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,10,'Blocks','10_Bl'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,10,'Turnovers','10_To'), left_index = True, right_index=True)

	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,5,'FDP','fdp mean_5'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,5,'FDP','fdp mean_5',True), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,5,'Points','5_Pts'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,5,'Assists','5_As'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,5,'Rebounds','5_Rb'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,5,'Steals','5_St'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,5,'Blocks','5_Bl'), left_index = True, right_index=True)
	newData=pd.merge(newData, getAveragesInTimeFrame(originalData,date_to_run,5,'Turnovers','5_To'), left_index = True, right_index=True)

	


	originalData,date_to_run=initializeDataset(noDays,True)

	#add home/away
	homeaway=originalData[originalData['Date']==date_to_run.strftime('%Y%m%d')][['First  Last', 'H/A']]
	homeaway.set_index('First  Last', inplace=True)
	newData=pd.merge(newData,homeaway, left_index=True, right_index=True)



	#add position
	pos=originalData[originalData['Date']==date_to_run.strftime('%Y%m%d')][['First  Last','FD pos']]
	pos.set_index('First  Last', inplace=True)
	newData=pd.merge(newData, pos, left_index = True, right_index=True)


	#add home/away stats
	newData=addAveragesHomeAway(originalData, date_to_run,newData)

	#add team and team opponent pt averages
	newData=getTeamAndOpponentStats(originalData,date_to_run,newData)

	minutes=originalData[(originalData['Date']>(date_to_run-timedelta(days=7))) &(originalData['Date']<date_to_run)].groupby('First  Last')["Minutes"].mean().to_frame().rename(columns = {"Minutes":"mins 7 days"}, inplace = False)
	newData=pd.merge(newData,minutes, left_index = True, right_index=True)
	
	if(date_to_run<pd.datetime.now()):
		Fdp=originalData[originalData['Date']==date_to_run.strftime('%Y%m%d')][['First  Last', 'FDP']]
		Fdp.set_index('First  Last', inplace=True)
		newData=pd.merge(newData,Fdp, left_index=True, right_index=True)	


	#clean data-fill 0's, drop columns
	newData=newData.fillna(0)
	newData=newData.iloc[:,np.r_[0:32,33:38,39:45,46:54]]
	''''newData=newData.drop('H/A',1)
	newData=newData.drop('Team',1)
	newData=newData.drop('Opp',1)'''


	if(train):	
		newData=newData.reset_index()
		newData=newData.iloc[:,1:]
		
	else:
		salary=originalData[originalData['Date']==date_to_run.strftime('%Y%m%d')][['First  Last', 'FD Sal']]
		salary.set_index('First  Last', inplace=True)
		
		newData=pd.merge(newData,salary, left_index=True, right_index=True)	

	return newData





def createTrainTestSets(day_to_run):
	train=pd.DataFrame([])
	test=generateData(day_to_run)

	for i in range(day_to_run+1,day_to_run+55):
		try:
			train=train.append(generateData(i, True))
		except:
			"Failed on date "+str(pd.datetime.now()-timedelta(days=i))
	return train,test

