import praw
from pyquery import PyQuery
from praw.errors import HTTPException
from tornado import web
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
import sys
import ScheduleGrabber
import SubGrabber
from urlparse import urlparse
import time
from selenium import webdriver
import re

while 1:
    team1=sys.argv[1]
    phantomJSInstallLocation=sys.argv[2]
    sub = ''
    url=''
    homeTeam = ''
    awayTeam = ''
    scheduleURLs=''
    currGame=''
    gameDate=''
    gameTime=''
    print("Team 1: "+team1)
    team1 = ScheduleGrabber.getTeamAbb(team1)
    print("Team 1: "+team1)
    sub = SubGrabber.getSubreddit(team1)
    #sub="/r/steelersdesign"
    r = praw.Reddit(user_agent="Steelers Mod GameThread Creator")
    returnString = ""
    awayLogoString=""
    homeLogoString=""

    class Page(web.RequestHandler):
        def get(self):
            code = self.get_argument("code", default=None, strip=False)
            self.write("Success! Your code: %s" % code)
            IOLoop.current().stop()
            self.login(code)

        def login(self, code):
            deets = r.get_access_information(code)
            print("oauth_refresh_token (put in praw.ini): %s" % deets['refresh_token'])
            r.set_access_credentials(**deets)
            # TODO: Automatically update praw.ini with refresh_token

    application = web.Application([
        (r"/authorize_callback", Page),
    ])

    try:
        r.refresh_access_information()
    except HTTPException:
        url = r.get_authorize_url('uniqueKey', ['identity', 'read', 'vote', 'edit'], True)
        print("Please open: ", url)
        server = HTTPServer(application)
        server.listen(65010)
        IOLoop.current().start()

    url="http://espn.go.com/nfl/team/_/name/"+team1+"/"
    doc = PyQuery(url)
    for e in doc(".club-schedule > ul > ul> li > a").items():
        parsedURL=urlparse(e.attr("href"))
        gameID=parsedURL.query
        gameIDArray = gameID.split("=")
        scheduleURLs+=gameIDArray[1]+" "
    gameIDArray=scheduleURLs.split(" ")
    currWeek=""
    index=0
    for e in gameIDArray:
        index+=1
        print("e: "+e)
        url="http://espn.go.com/nfl/boxscore?gameId="+e
        browser = webdriver.PhantomJS(phantomJSInstallLocation+"phantomjs")
        browser.get(url)
        content = browser.page_source
        browser.quit()
        doc=PyQuery(content)
        currQuarter = doc(".game-time").text()
        print("currQuarter: "+currQuarter)
        network=""
        if currQuarter != 'Final':
            currGame = e
            currWeek = index
            gameDate=doc(".game-date").text()
            gameTime=doc(".game-time.time").text()
            network=doc(".competitors .game-status .network").text()
            break
    url="espn.go.com/nfl/boxscore?gameId="+currGame
    print("Game Date: "+gameDate)
    print("Game Time: "+gameTime)


    #gameDate="09/24"
    #gameTime="8:00 PM"


    gameTimeArray=gameTime.split(" ")
    gameAMOrPM = gameTimeArray[1]
    gameTime=gameTimeArray[0]
    gameTimeArray = gameTime.split(":")
    hour=gameTimeArray[0]
    gameDateArray=gameDate.split("/")
    month=gameDateArray[0]
    day=gameDateArray[1]
    if gameDateArray[0] < 10:
        monthArray=gameDateArray[0].split("")
        month=monthArray[1]
    if gameDateArray[1] < 10:
        dayArray=gameDateArray[1].split("")
        day=dayArray[1]
    gameDate=month+"/"+day
    #print("URLs: "+scheduleURLs)

    #main("pit", "ne", "https://espn.go.com/nfl/boxscore?gameId=400791485", "/r/steelers")

    if r.user == None:
        print("Failed to log in. Something went wrong!")
    else:
        print("Logged in as %s." % r.user)
    print(sub)
    r.get_subreddit(sub)
    #doc = PyQuery(url)
    currQuarter = "N/A"
    currentMonth = time.strftime("%m")
    currentDay = time.strftime("%d")
    currentHour = time.strftime("%I")
    #currentMonth="09"
    #currentDay="10"
    #currentHour="08"
    if int(currentHour) < 10:
        print(currentHour)
        currentHourArray = list(currentHour)
        currentHour=currentHourArray[1]
    if int(currentMonth) < 10:
        currentMonthArray = list(currentMonth)
        currentMonth=currentMonthArray[1]
    if int(currentDay) < 10:
        currentDayArray = list(currentDay)
        currentDay=int(currentDayArray[1])
    currentMinute = time.strftime("%M")
    currentAmOrPM = time.strftime("%p")
    print("Month: "+month+" day: "+day+" currentMonth: "+currentMonth+" currentDay: "+currentDay+" currentAM/PM: "+currentAmOrPM+"gameAM/PM"+gameAMOrPM)
    currQuarter = doc(".game-time").text()
    if int(currentMonth) - int(month) == 0 and int(currentDay) - int(day) == 0:
        print("HOUR: "+hour+" currentHour: "+currentHour)
        if ((gameAMOrPM == currentAmOrPM and int(hour) != 1 and int(hour)-int(currentHour) <= 1) or (int(currentHour)==12 and int(hour) == 1)):
            while currQuarter != "Final":
                redditPost = ""
                currQuarter = doc(".game-time").text()
                scoringSummaryQuarter = doc(".scoring-summary > table > tbody > .highlight")
                scoringSummaryPlay = doc(".scoring-summary > table > tbody > tr > .game-details > .table-row")
                quartersString = ""
                for e in doc("#linescore > thead > tr > th").items():
                    print("e: "+e.text())
                    if(e.text() == ""):
                        quartersString += "- "
                    else:
                        quartersString += e.text()+" "
                quartersString = re.sub(" $", "", quartersString)
                print("Quarterts String: "+quartersString)
                quarters=quartersString.split(" ")
                topPerformerStats=doc(".game-notes > p")
                scoringSummaryQuarter=doc(".mod-data > thead > tr > th")
                scoringSummaryPlay=doc("mod-data > tbody")
                scoringSummary = ""
                scoreboardQuarterHeader="|Team"
                homeTeamScores=""
                awayTeamScores=""
                homeTeamAbb=doc(".home > .content > .team-container > .team-info > .team-name > .abbrev").text()
                awayTeamAbb=doc(".away > .content > .team-container > .team-info > .team-name > .abbrev").text()
                homeTeamMascot=doc(".home > .content > .team-container > .team-info > .team-name > .short-name").text()
                homeTeamCity=doc(".home > .content > .team-container > .team-info > .team-name > .long-name").text()
                awayTeamMascot=doc(".away > .content > .team-container > .team-info > .team-name > .short-name").text()
                awayTeamCity=doc(".away > .content > .team-container > .team-info > .team-name > .long-name").text()
                #homeTeamAbb="ne"
                #awayTeamAbb="pit"
                print("Home: "+homeTeamAbb)
                print("Away: "+awayTeamAbb)
                homeTeamSub=SubGrabber.getSubreddit(homeTeamAbb)
                awayTeamSub=SubGrabber.getSubreddit(awayTeamAbb)
                awayLogoString="[]("+awayTeamSub+")"
                homeLogoString="[]("+homeTeamSub+")"

                awayCmpPercString=""
                for e in doc("#gamepackage-passing .gamepackage-away-wrap  .mod-data > tbody > tr > .c-att").items():
                    awayCmpPercString += e.text()+" "
                awayPassingYardsString=""
                for e in doc("#gamepackage-passing .gamepackage-away-wrap  .mod-data > tbody > tr > .yds").items():
                    awayPassingYardsString+=e.text()+" "
                awayYPAString=""
                for e in doc("#gamepackage-passing .gamepackage-away-wrap  .mod-data > tbody > tr > .avg").items():
                    awayYPAString+=e.text()+" "
                awayPassingTDString=""
                for e in doc("#gamepackage-passing .gamepackage-away-wrap  .mod-data > tbody > tr > .td").items():
                    awayPassingTDString+=e.text()+" "
                awayINTString=""
                for e in doc("#gamepackage-passing .gamepackage-away-wrap  .mod-data > tbody > tr > .int").items():
                    awayINTString+=e.text()+" "
                awaySacksString=""
                for e in doc("#gamepackage-passing .gamepackage-away-wrap .mod-data > tbody > tr > .sacks").items():
                    awaySacksString+=e.text()+" "
                awayRatingString=""
                for e in doc("#gamepackage-passing .gamepackage-away-wrap  .mod-data > tbody > tr > .rtg").items():
                    awayRatingString+=e.text()+" "
                awayQBNameString=""
                for e in doc("#gamepackage-passing .gamepackage-away-wrap  .mod-data > tbody > tr > .name > a").items():
                    awayQBNameString+=e.text()+"!!!!"


                homeCmpPercString=""
                for e in doc("#gamepackage-passing .gamepackage-home-wrap  .mod-data > tbody > tr > .c-att").items():
                    homeCmpPercString += e.text()+" "
                homePassingYardsString=""
                for e in doc("#gamepackage-passing .gamepackage-home-wrap  .mod-data > tbody > tr > .yds").items():
                    homePassingYardsString+=e.text()+" "
                homeYPAString=""
                for e in doc("#gamepackage-passing .gamepackage-home-wrap  .mod-data > tbody > tr > .avg").items():
                    homeYPAString+=e.text()+" "
                homePassingTDString=""
                for e in doc("#gamepackage-passing .gamepackage-home-wrap  .mod-data > tbody > tr > .td").items():
                    homePassingTDString+=e.text()+" "
                homeINTString=""
                for e in doc("#gamepackage-passing .gamepackage-home-wrap  .mod-data > tbody > tr > .int").items():
                    homeINTString+=e.text()+" "
                homeSacksString=""
                for e in doc("#gamepackage-passing .gamepackage-home-wrap .mod-data > tbody > tr > .sacks").items():
                    homeSacksString+=e.text()+" "
                homeRatingString=""
                for e in doc("#gamepackage-passing .gamepackage-home-wrap  .mod-data > tbody > tr > .rtg").items():
                    homeRatingString+=e.text()+" "
                homeQBNameString=""
                for e in doc("#gamepackage-passing .gamepackage-home-wrap  .mod-data > tbody > tr > .name > a").items():
                    homeQBNameString+=e.text()+"!!!!"

                awayRBNameString=""
                for e in doc("#gamepackage-rushing .gamepackage-away-wrap  .mod-data > tbody > tr > .name > a").items():
                    awayRBNameString+=e.text()+"!!!!"
                awayRushingAttString=""
                for e in doc("#gamepackage-rushing .gamepackage-away-wrap  .mod-data > tbody > tr > .car").items():
                    awayRushingAttString+=e.text()+" "
                awayRushingYardsString=""
                for e in doc("#gamepackage-rushing .gamepackage-away-wrap  .mod-data > tbody > tr > .yds").items():
                    awayRushingYardsString+=e.text()+" "
                awayYardsPerCarryString=""
                for e in doc("#gamepackage-rushing .gamepackage-away-wrap  .mod-data > tbody > tr > .avg").items():
                    awayYardsPerCarryString+=e.text()+" "
                awayRushingTDString=""
                for e in doc("#gamepackage-rushing .gamepackage-away-wrap  .mod-data > tbody > tr > .td").items():
                    awayRushingTDString+=e.text()+" "
                awayRushingLongString=""
                for e in doc("#gamepackage-rushing .gamepackage-away-wrap  .mod-data > tbody > tr > .long").items():
                    awayRushingLongString+=e.text()+" "


                homeRBNameString=""
                for e in doc("#gamepackage-rushing .gamepackage-home-wrap  .mod-data > tbody > tr > .name > a").items():
                    homeRBNameString+=e.text()+"!!!!"
                homeRushingAttString=""
                for e in doc("#gamepackage-rushing .gamepackage-home-wrap  .mod-data > tbody > tr > .car").items():
                    homeRushingAttString+=e.text()+" "
                homeRushingYardsString=""
                for e in doc("#gamepackage-rushing .gamepackage-home-wrap  .mod-data > tbody > tr > .yds").items():
                    homeRushingYardsString+=e.text()+" "
                homeYardsPerCarryString=""
                for e in doc("#gamepackage-rushing .gamepackage-home-wrap  .mod-data > tbody > tr > .avg").items():
                    homeYardsPerCarryString+=e.text()+" "
                homeRushingTDString=""
                for e in doc("#gamepackage-rushing .gamepackage-home-wrap  .mod-data > tbody > tr > .td").items():
                    homeRushingTDString+=e.text()+" "
                homeRushingLongString=""
                for e in doc("#gamepackage-rushing .gamepackage-home-wrap  .mod-data > tbody > tr > .long").items():
                    homeRushingLongString+=e.text()+" "

                homeWRNameString=""
                for e in doc("#gamepackage-receiving .gamepackage-home-wrap  .mod-data > tbody > tr > .name > a").items():
                    homeWRNameString+=e.text()+"!!!!"
                homeReceptionsString=""
                for e in doc("#gamepackage-receiving .gamepackage-home-wrap  .mod-data > tbody > tr > .rec").items():
                    homeReceptionsString+=e.text()+" "
                homeReceivingYardsString=""
                for e in doc("#gamepackage-receiving .gamepackage-home-wrap  .mod-data > tbody > tr > .yds").items():
                    homeReceivingYardsString+=e.text()+" "
                homeYardsPerCatchString=""
                for e in doc("#gamepackage-receiving .gamepackage-home-wrap  .mod-data > tbody > tr > .avg").items():
                    homeYardsPerCatchString+=e.text()+" "
                homeReceivingTDString=""
                for e in doc("#gamepackage-receiving .gamepackage-home-wrap  .mod-data > tbody > tr > .td").items():
                    homeReceivingTDString+=e.text()+" "
                homeReceivingLongString=""
                for e in doc("#gamepackage-receiving .gamepackage-home-wrap  .mod-data > tbody > tr > .long").items():
                    homeReceivingLongString+=e.text()+" "
                homeReceivingTargetsString=""
                for e in doc("#gamepackage-receiving .gamepackage-home-wrap  .mod-data > tbody > tr > .tgts").items():
                    homeReceivingTargetsString+=e.text()+" "

                awayWRNameString=""
                for e in doc("#gamepackage-receiving .gamepackage-away-wrap  .mod-data > tbody > tr > .name > a").items():
                    awayWRNameString+=e.text()+"!!!!"
                awayReceptionsString=""
                for e in doc("#gamepackage-receiving .gamepackage-away-wrap  .mod-data > tbody > tr > .rec").items():
                    awayReceptionsString+=e.text()+" "
                awayReceivingYardsString=""
                for e in doc("#gamepackage-receiving .gamepackage-away-wrap  .mod-data > tbody > tr > .yds").items():
                    awayReceivingYardsString+=e.text()+" "
                awayYardsPerCatchString=""
                for e in doc("#gamepackage-receiving .gamepackage-away-wrap  .mod-data > tbody > tr > .avg").items():
                    awayYardsPerCatchString+=e.text()+" "
                awayReceivingTDString=""
                for e in doc("#gamepackage-receiving .gamepackage-away-wrap  .mod-data > tbody > tr > .td").items():
                    awayReceivingTDString+=e.text()+" "
                awayReceivingLongString=""
                for e in doc("#gamepackage-receiving .gamepackage-away-wrap  .mod-data > tbody > tr > .long").items():
                    awayReceivingLongString+=e.text()+" "
                awayReceivingTargetsString=""
                for e in doc("#gamepackage-receiving .gamepackage-away-wrap  .mod-data > tbody > tr > .tgts").items():
                    awayReceivingTargetsString+=e.text()+" "

                scoreAway = ""
                scoreHome = ""
                for e in doc("#linescore > tbody > tr").eq(0)("td").items():
                    if(e.text()) == "":
                        scoreAway+="- "
                    else:
                        scoreAway+=e.text()+" "
                for e in doc("#linescore > tbody > tr").eq(1)("td").items():
                    print("e: "+e.text())
                    if(e.text()) == "":
                        scoreHome+="- "
                    else:
                        scoreHome+=e.text()+" "
                print("Score Away: "+scoreAway)
                print("Score Home: "+scoreHome)
                scoreAwayArray = scoreAway.split(" ")
                scoreHomeArray = scoreHome.split(" ")
                scoreboardTableDivider="|-|"
                homeTeamScores+="|"+homeLogoString
                awayTeamScores+="|"+awayLogoString
                print(len(quarters))
                for i in range(len(quarters)):
                    scoreboardQuarterHeader+="|"+quarters[i]
                    scoreboardTableDivider+="-|"
                if len(scoreAwayArray) > 1:
                    for i in range(0, len(quarters)+1):
                        if i > len(scoreHomeArray):
                            print("homeScore len "+len(scoreHomeArray) +"is less than i "+i)
                            homeTeamScores+="|-"
                        else:
                            print("Home Score: "+scoreHomeArray[i])
                            homeTeamScores += "|"+scoreHomeArray[i]
                    for i in range(0, len(quarters)+1):
                        if i > len(scoreAwayArray):
                            print("awayScore len "+len(scoreAwayArray) +"is less than i "+i)
                            awayTeamScores+="|+"
                        else:
                            print("Away Score: "+scoreAwayArray[i])
                            awayTeamScores += "|"+scoreAwayArray[i]


                homeCmpPercentArray = homeCmpPercString.split(" ")
                homeQBNameArray = homeQBNameString.split("!!!!")
                homePassingTDArray = homePassingTDString.split(" ")
                homePassingYardsArray = homePassingYardsString.split(" ")
                homeYPAArray = homeYPAString.split(" ")
                homeINTArray = homeINTString.split(" ")
                homeRatingArray = homeRatingString.split(" ")
                homeSacksArray = homeSacksString.split(" ")


                awayCmpPercentArray = awayCmpPercString.split(" ")
                awayQBNameArray = awayQBNameString.split("!!!!")

                awayPassingTDArray = awayPassingTDString.split(" ")
                awayPassingYardsArray = awayPassingYardsString.split(" ")
                awayYPAArray = awayYPAString.split(" ")
                awayINTArray = awayINTString.split(" ")
                awayRatingArray = awayRatingString.split(" ")
                awaySacksArray = awaySacksString.split(" ")

                homeRushingAttArray = homeRushingAttString.split(" ")
                homeRushingLongArray = homeRushingLongString.split(" ")
                homeRushingYardsArray = homeRushingYardsString.split(" ")
                homeRushingTDArray = homeRushingTDString.split(" ")
                homeYardsPerCarryArray = homeYardsPerCarryString.split(" ")
                homeRBNameArray = homeRBNameString.split("!!!!")

                awayRushingAttArray = awayRushingAttString.split(" ")
                awayRushingLongArray = awayRushingLongString.split(" ")
                awayRushingYardsArray = awayRushingYardsString.split(" ")
                awayRushingTDArray = awayRushingTDString.split(" ")
                awayYardsPerCarryArray = awayYardsPerCarryString.split(" ")
                awayRBNameArray = awayRBNameString.split("!!!!")

                homeReceptionsArray = homeReceptionsString.split(" ")
                homeReceivingYardsArray = homeReceivingYardsString.split(" ")
                homeReceivingTargetsArray = homeReceivingTargetsString.split(" ")
                homeReceivingTDArray = homeReceivingTDString.split(" ")
                homeReceivingLongArray = homeReceivingLongString.split(" ")
                homeWRNameArray = homeWRNameString.split("!!!!")
                homeYardsPerCatchArray = homeYardsPerCatchString.split(" ")

                awayReceptionsArray = awayReceptionsString.split(" ")
                awayReceivingYardsArray = awayReceivingYardsString.split(" ")
                awayReceivingTargetsArray = awayReceivingTargetsString.split(" ")
                awayReceivingTDArray = awayReceivingTDString.split(" ")
                awayReceivingLongArray = awayReceivingLongString.split(" ")
                awayWRNameArray = awayWRNameString.split("!!!!")
                awayYardsPerCatchArray = awayYardsPerCatchString.split(" ")

                #print("|"+homeLogoString+"|Cmp %|")
                homeQBStats=""
                awayQBStats=""
                homeRBStats=""
                awayRBStats=""
                homeWRStats=""
                awayWRStats=""
                qbHeaders="|Team|Name|Cmp/Att|Yards|TDs|Ints|YPA|Sacks-Yards|Rating|\n"
                qbDivider="|-|-|-|-|-|-|-|-|-|\n"
                for i in range(0, len(homeQBNameArray)):
                    homeQBStats+="|"+homeLogoString+"|"+homeQBNameArray[i]+"|"+homeCmpPercentArray[i]+"|"+homePassingYardsArray[i]+"|"+homePassingTDArray[i]+"|"+homeINTArray[i]+"|"+homeYPAArray[i]+"|"+homeSacksArray[i]+"|"+homeRatingArray[i]+"|\n"
                for i in range(0, len(awayQBNameArray)):
                    awayQBStats+="|"+awayLogoString+"|"+awayQBNameArray[i]+"|"+awayCmpPercentArray[i]+"|"+awayPassingYardsArray[i]+"|"+awayPassingTDArray[i]+"|"+awayINTArray[i]+"|"+awayYPAArray[i]+"|"+awaySacksArray[i]+"|"+awayRatingArray[i]+"|\n"

                rbHeaders="|Team|Name|Att|Yards|TDs|Y/C|Long\n"
                rbDivider="|-|-|-|-|-|-|-|\n"
                for i in range(0, len(homeRBNameArray)):
                    homeRBStats+="|"+homeLogoString+"|"+homeRBNameArray[i]+"|"+homeRushingAttArray[i]+"|"+homeRushingYardsArray[i]+"|"+homeRushingTDArray[i]+"|"+homeYardsPerCarryArray[i]+"|"+homeRushingLongArray[i]+"|\n"
                for i in range(0, len(awayRBNameArray)):
                    awayRBStats+="|"+awayLogoString+"|"+awayRBNameArray[i]+"|"+awayRushingAttArray[i]+"|"+awayRushingYardsArray[i]+"|"+awayRushingTDArray[i]+"|"+awayYardsPerCarryArray[i]+"|"+awayRushingLongArray[i]+"|\n"

                wrHeaders="|Team|Name|Rec.|Yards|Y/C|TDs|Targets|Long|\n"
                wrDivider="|-|-|-|-|-|-|-|-|\n"
                for i in range(0, len(homeWRNameArray)):
                    homeWRStats+="|"+homeLogoString+"|"+homeWRNameArray[i]+"|"+homeReceptionsArray[i]+"|"+homeReceivingYardsArray[i]+"|"+homeYardsPerCatchArray[i]+"|"+homeReceivingTDArray[i]+"|"+homeReceivingTargetsArray[i]+"|"+homeReceivingLongArray[i]+"|\n"
                for i in range(0, len(awayWRNameArray)):
                    awayWRStats+="|"+awayLogoString+"|"+awayWRNameArray[i]+"|"+awayReceptionsArray[i]+"|"+awayReceivingYardsArray[i]+"|"+awayYardsPerCatchArray[i]+"|"+awayReceivingTDArray[i]+"|"+awayReceivingTargetsArray[i]+"|"+awayReceivingLongArray[i]+"|\n"

                redditPost+="#Current time left: "+currQuarter+"\n\n#Scoreboard: \n\n"+scoreboardQuarterHeader+"|\n"+scoreboardTableDivider+"\n"+homeTeamScores+"|\n"+awayTeamScores+"|\n\n"

                redditPost+= "#Home Passing Stats:\n\n"
                redditPost+=qbHeaders+qbDivider+homeQBStats+"\n\n"
                redditPost+= "#Away Passing Stats:\n\n"
                redditPost+=qbHeaders+qbDivider+awayQBStats+"\n\n"
                redditPost+= "#Home Rushing Stats\n\n"
                redditPost+=rbHeaders+rbDivider+homeRBStats+"\n\n"
                redditPost+= "#Away Rushing Stats\n\n"
                redditPost+=rbHeaders+rbDivider+awayRBStats+"\n\n"
                redditPost+= "#Home Receiving Stats\n\n"
                redditPost+=wrHeaders+wrDivider+homeWRStats+"\n\n"
                redditPost+= "#Away Receiving Stats\n\n"
                redditPost+=wrHeaders+wrDivider+awayWRStats+"\n\n"
                redditPost+="#Chat Frog\n\nChat frog will have a live chat running during the game, and you can use your reddit account to login there.  It can be found [here](https://chatfrog.com"+sub+").\n\nGame is on "+network+".\n\nGo to /r/nflstreams and find the link for this game for a stream.\n\n"

                url="http://espn.go.com/nfl/game?gameId="+gameID
                browser = webdriver.PhantomJS(phantomJSInstallLocation+"phantomjs")
                browser.get(url)
                content = browser.page_source
                browser.quit()
                scoringDoc=PyQuery(content)

                r.refresh_access_information()



                #returnString = r.get_submission("https://www.reddit.com/r/steelersdesign/comments/3m9g16/week_3_game_thread_washington_redskins_new_york/")




                threadTitle = 'Week '+str(currWeek)+' Game Thread: '+awayTeamCity+' '+awayTeamMascot+' @ '+homeTeamCity+' '+homeTeamMascot
                if returnString == "":
                    returnString = r.submit(sub, 'Week '+str(currWeek)+' Game Thread: '+awayTeamCity+' '+awayTeamMascot+' @ '+homeTeamCity+' '+homeTeamMascot, text=redditPost, save=True)
                else:
                    returnString.edit(redditPost)
                #print(returnString)

                url="http://espn.go.com/nfl/boxscore?gameId="+currGame
                browser = webdriver.PhantomJS(phantomJSInstallLocation+"phantomjs")
                browser.get(url)
                content = browser.page_source
                browser.quit()
                doc=PyQuery(content)
                time.sleep(60)
            if(currQuarter == 'Final' and int(currentMonth) - int(month) == 0 and int(currentDay) - int(day) == 0):
                returnString.edit(redditPost)
                r.submit(sub, 'Week '+str(currWeek)+' Post Game Thread: '+awayTeamCity+' '+awayTeamMascot+' @ '+homeTeamCity+' '+homeTeamMascot, text=redditPost, save=True)
                url="http://espn.go.com/nfl/team/_/name/"+team1+"/"
                doc = PyQuery(url)
                for e in doc(".club-schedule > ul > ul> li > a").items():
                    parsedURL=urlparse(e.attr("href"))
                    gameID=parsedURL.query
                    gameIDArray = gameID.split("=")
                    scheduleURLs+=gameIDArray[1]+" "
                gameIDArray=scheduleURLs.split(" ")
                currWeek=""
                index=0
                for e in gameIDArray:
                    index+=1
                    print("e: "+e)
                    url="http://espn.go.com/nfl/boxscore?gameId="+e
                    browser = webdriver.PhantomJS(phantomJSInstallLocation+"phantomjs")
                    browser.get(url)
                    content = browser.page_source
                    browser.quit()
                    doc=PyQuery(content)
                    currQuarter = doc(".game-time").text()
                    print("currQuarter: "+currQuarter)
                    network=""
                    if currQuarter != 'Final':
                        currGame = e
                        currWeek = index
                        gameDate=doc(".game-date").text()
                        gameTime=doc(".game-time.time").text()
                        network=doc(".competitors .game-status .network").text()
                        break
                url="espn.go.com/nfl/boxscore?gameId="+currGame
                gameTimeArray=gameTime.split(" ")
                gameAMOrPM = gameTimeArray[1]
                gameTime=gameTimeArray[0]
                gameTimeArray = gameTime.split(":")
                hour=gameTimeArray[0]
                gameDateArray=gameDate.split("/")
                month=gameDateArray[0]
                day=gameDateArray[1]
                if gameDateArray[0] < 10:
                    monthArray=gameDateArray[0].split("")
                    month=monthArray[1]
                if gameDateArray[1] < 10:
                    dayArray=gameDateArray[1].split("")
                    day=dayArray[1]
                gameDate=month+"/"+day
        else:
            time.sleep(600)
    else:
        time.sleep(600)