from __future__ import division

#main.py
import webapp2  #gives access to Google's deployment code
import jinja2
import os
import time
from google.appengine.api import users
from models import Person
from models import Journal
from google.appengine.ext import ndb
import operator
import google.appengine.ext.db
#libraries for api_version
from google.appengine.api import urlfetch
import json
from time import strptime, strftime
import urllib
import string
import unicodedata
from datetime import datetime, date

LATENCY_TIME = 2
API_KEY = "AIzaSyDIvie5wqDm3ywU1Msdm_ZVhnLHM3t3c0o"

def text_to_list(full_text):
    oldwordlist = full_text.split(" ")
    wordlist = []
    for word in oldwordlist:
        newword = word.strip(string.punctuation)
        newword = newword.lower()
        wordlist.append(newword)
    return wordlist


def word_count(words):
    count = 0
    for word in words:
        count += 1
    return count

sad_words = ["sad", "confused", "upset", "cry", "crying", "disappointed", "worthless", "useless", "sadness", "insecure", "despair", "depressed",
                "defeated", "insecurity", "frustrated", "disappointment", "down", "low", "upsetting", "confusion"]
angry_words = ["angry", "mad", "ugh", "displeased", "upset", "frustrated", "frustration", "fuck", "shit", "shitty", "damn", "bitch", "dick", "shitbag",
                "asshole", "dickhead", "cunt", "annoying", "annoyed", "fucking", "fucked", "betrayed", "betray", "stupid"
                "arrogant", "awful", "brainless", "cheap", "childish", "corrupt", "controlling", "disgusting", "dishonest", "embarrassing",
                "evil", "fake", "furious", "greedy", "gross", "horrible", "immature", "insane", "insecure", "irrational", "irritating",
                "lame", "lousy", "lying", "manipulating", "mean", "nasty", "obnoxious", "offensive", "outraged", "painful", "pathetic",
                "pissed", "repulsive", "ridiculous", "rude", "selfish", "spoiled", "terrible", "thoughtless", "unacceptable", "underhanded",
                "unthoughtful", "useless", "violent", "worthless"]
happy_words = ["excited", "happy", "glad", "love", "content", "delighted", "awesome", "fantastic", "perfect", "success", "exciting", "alive",
                "pleased", "satisfied", "cheerful", "yay", "cool", "wonderful", "excitement", "good", "thank", "grateful", "brilliant", "hurray",
                "thankfully", "smile", "laugh", "nice", "amazing"]
worried_words = ["afraid", "stressed", "stressful", "unsure", "worried", "concerned", "stress", "anxious", "fear", "fearful", "panic", "nervous", "uneasy", "upset"]
confused_words = ["confused", "unsure", "confusion", "why", "who", "when", "can't", "ambiguous", "perplexed", "mixed", "muddled"]
embarrassed_words = ["embarrassing", "embarrassed", "shame", "shameful", "shaming", "insecure", "regret", "regretting", "regretted", "ashamed", "flustered", "fluster",
                    "guilty", "sorry", "stupid", "uncomfortable"]
tired_words = ["tired", "exhausted", "stressed", "sleep", "rest", "restful", "insomnia", "worked", "working", "tiring", "tire", "stress", "stressful", "exhaustion"]

sad = [204, 229, 255]
angry = [255, 204, 204]
happy = [255, 255, 204]
worried = [229, 204, 255]
confused = [204, 255, 204]
embarrassed = [255, 210, 255]
tired = [216, 216, 216]
none = [255, 255, 255]

colors = {"sad":sad, "angry":angry, "happy":happy, "worried":worried, "confused":confused, "embarrassed":embarrassed, "tired":tired, "none":none}

def find_emotions(words):
    emotions = {"sad": 0, "angry": 0, "happy": 0, "worried": 0, "confused": 0, "embarrassed": 0, "tired": 0, "none": 0}

    for word in words:
        if word in sad_words:
            emotions["sad"] += 1
        if word in angry_words:
            emotions["angry"] += 1
        if word in happy_words:
            emotions["happy"] += 1
        if word in worried_words:
            emotions["worried"] += 1
        if word in confused_words:
            emotions["confused"] += 1
        if word in embarrassed_words:
            emotions["embarrassed"] += 1
        if word in tired_words:
            emotions["tired"] += 1

    return emotions

def top_emotions(emotions):
    max = 0 #emotions must be 0 or greater
    first = ""
    max2 = 0
    second = ""
    for emotion in emotions:
        v=int(emotions[emotion])
        if v > max:
            print(emotion+" "+str(v)+" "+str(max))
            max2 = max #push max to second max
            second = first
            max = v #put new emotion at max
            first = emotion
        elif v > max2:
            max2 = v
            second = emotion

    if (max == 0):
        first = "none"
        second = "none"
    elif (max2 == 0):
        second = "none"
    print(first)
    print(second)
    top_two = {"first": colors[first], "second": colors[second]}
    return top_two

def emotion_to_color(emotion):
    if emotion == "sad":
        return sad
    elif emotion == "angry":
        return angry
    elif emotion == "happy":
        return happy
    elif emotion == "worried":
        return worried
    elif emotion == "confused":
        return confused
    elif emotion == "embaressed":
        return embaressed
    elif emotion == "tired":
        return tired
    elif emotion == "none":
        return [255, 255, 255]

def emotion_from_color(rgb):
    for color in colors:
        if colors[color] == rgb:
            return color


def filterFillers(str):
    words= text_to_list(str)   #an array of words separated by whitespace
    N = len(words)
    banned_words=["uh","um"] #fill in later
    res=[]
    for word in words:
        if word not in banned_words:
            res.append(word)
    return res

def filterFillersTest():
    str="Hi I like uh kinda don't like apple pie for some reason um yeah"
    filteredStr=filterFillers(str)
    print(filteredStr)

def fileToText(data):
    api_payload = {
        "config": {
            "encoding":"LINEAR16",
            "languageCode": "en-US"
        },
        "audio": {
            "content": data
        }
    }
    api_payload = json.dumps(api_payload)
    url = "https://speech.googleapis.com/v1/speech:recognize?key=" + API_KEY
    api_headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    api_response = urlfetch.fetch(url, method="post", payload = api_payload, headers = api_headers).content
    if 'results' in api_response:
        api_response_json = json.loads(api_response)
        api_text = api_response_json['results'][0]['alternatives'][0]['transcript']
        print(api_text)
        return api_text
    else:
        return None


jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
jinja_env.globals.update(zip=zip)

def checkLogIn(template):
    logout_url = users.create_logout_url('/')
    user = users.get_current_user()

    if user:
        email_address=user.nickname()
        existing_user=Person.query().filter(Person.email == email_address).get()
        template["logout_url"] = logout_url
        print(email_address)
        print(existing_user)
        if existing_user:
            template["hideLogIn"] = "hidden"
            template["first_name"] = existing_user.first_name
            template["last_name"] = existing_user.last_name
        else:
            template["hideLogOut"] = "hidden"
    else:
        template["hideLogOut"] = "hidden"

class HomePage(webapp2.RequestHandler):
    def get(self):
        home_dict={

        }
        checkLogIn(home_dict)
        home_template = jinja_env.get_template("/templates/homepage.html")
        self.response.write(home_template.render(home_dict))

class Ramble(webapp2.RequestHandler):
    def get(self):
        redirect= ""
        user = users.get_current_user() # will return a user if someone is signed in, if not, none
        if user:
            email_address = user.nickname()

            current_user = Person.query().filter(Person.email == email_address).get() #query if we already have that email #get pulls only one
            if not current_user:
                self.redirect('/register')
            # self.response.write("You are logged in " + email_address +"!")
        else:
            redirect = '<meta http-equiv="Refresh" content="0.0; url=/register">'

        meta_data ={
         "redirect": redirect,
        }

        ramble_template = jinja_env.get_template("/templates/ramble.html")
        checkLogIn(meta_data)
        self.response.write(ramble_template.render(meta_data))


class JournalPage(webapp2.RequestHandler):
    def get(self):

        key = self.request.get_all("key") #this gives you a string
        # print(key)
        keyString = unicodedata.normalize('NFKD', key[0]).encode('ascii','ignore')
        keyList = keyString.split(" ")
        year = int(keyList[0])
        month = int(keyList[1])
        sumofSeconds = int(keyList[2]) #'2019', '10', '1119957']
        if len(keyList) > 2:
            r1 = int(keyList[3])
            g1 = int(keyList[4])
            b1 = int(keyList[5])
            r2 = int(keyList[6])
            g2 = int(keyList[7])
            b2 = int(keyList[8])
            rgb_1 = [r1, g1, b1]
            rgb_2 = [r2, g2, b2]

        user = users.get_current_user()
        email_address = user.nickname()
        #https://stackoverflow.com/questions/1345827/how-do-i-find-the-time-difference-between-two-datetime-objects-in-python

        profilePerson = Person.query().filter(Person.email == email_address).get() # gets the right obj now!!
        journal_page = Journal.query().filter(Journal.user == email_address).filter(Journal.year == year).filter(Journal.month == month).filter(Journal.sumSeconds >= sumofSeconds).get()

        if len(keyList) > 2:
            journal_page.rgb1 = rgb_1
            journal_page.rgb2 = rgb_2

        now = journal_page.created
        str_day = now.strftime('%m-%d-%Y')
        str_time = now.strftime('%H:%M')

        p1=emotion_from_color(journal_page.rgb1)
        p2='& '+emotion_from_color(journal_page.rgb2)

        if p1 == "none":
            p1 = "no tones detected"
            p2 = ""
        elif p2 == "& none":
            p2 = ""
        j_dict = {
            "first_name": profilePerson.first_name,
            "last_name": profilePerson.last_name,
            "diary_entry": journal_page.text,
            "r1": journal_page.rgb1[0],
            "g1": journal_page.rgb1[1],
            "b1": journal_page.rgb1[2],
            "r2": journal_page.rgb2[0],
            "g2": journal_page.rgb2[1],
            "b2": journal_page.rgb2[2],
            "p1": p1,
            "p2": p2,
            "date": str_day,
            "time": str_time,
            "word_count": word_count(text_to_list(journal_page.text)),
        }

        j_template = jinja_env.get_template("/templates/journal.html")
        checkLogIn(j_dict)
        self.response.write(j_template.render(j_dict))

    def post(self):

        angry = self.request.get("anger")
        sad = self.request.get("sadness")
        happy = self.request.get("happiness")
        confused = self.request.get("confusion")
        worried = self.request.get("anxiety")
        embarrassed = self.request.get("embarassment")
        tired = self.request.get("tired")

        emotions = {"angry":angry, "sad":sad, "happy":happy, "confused":confused, "worried":worried, "embarrassed":embarrassed, "tired":tired}

        key = self.request.get_all("key") #this gives you a string
        keyString = unicodedata.normalize('NFKD', key[0]).encode('ascii','ignore')
        keyList = keyString.split(" ")
        year = int(keyList[0])
        month = int(keyList[1])
        sumofSeconds = int(keyList[2]) #'2019', '10', '1119957']

        user = users.get_current_user()
        email_address = user.nickname()
        #https://stackoverflow.com/questions/1345827/how-do-i-find-the-time-difference-between-two-datetime-objects-in-python

        profilePerson = Person.query().filter(Person.email == email_address).get() # gets the right obj now!!
        journal_page = Journal.query().filter(Journal.user == email_address).filter(Journal.year == year).filter(Journal.month == month).filter(Journal.sumSeconds >= sumofSeconds).get()


        topEmotions = top_emotions(emotions)
        journal_page.rgb1 = colors[emotion_from_color(topEmotions["first"])]
        journal_page.rgb2 = colors[emotion_from_color(topEmotions["second"])]



        # time.sleep(3)

        print(topEmotions)
        print(emotions)
        print(journal_page.rgb1)
        print(journal_page.rgb2)

        # if (emotions[indicies[0]] != journal_page.p1)

        # def findtopemotions(emotions):
        #     max = -1 #emotions must be 0 or greater
        #     max2 = -1
        #     for index, emotion in enumerate(emotions):
        #         if emotion > max:
        #             max2 = max #push max to second max
        #             max = emotion #put new emotion at max
        #             firstIndex = index
        #         elif emotion > max2:
        #             max2 = emotion
        #             secondIndex = index
        #     return [firstIndex, secondIndex]
        # indicies = findtopemotions(emotions)

        # if (emotions[indicies[0]] != journal_page)

        #don't delete! old post code
        # text = fileToText(self.request.get("data"))
        # if text == None:
        #     time.sleep(5)
        #     self.redirect('/ramble')
        #     return
        # text = unicodedata.normalize('NFKD', text).encode('ascii','ignore')
        # # wordList = text_to_list(text)
        # wordList = filterFillers(text)
        # emotions = find_emotions(wordList)
        # topemotions = top_emotions(emotions) #returns a list of top emotions
        #
        # rgb_1 = topemotions["first"]
        # rgb_2 = topemotions["second"]
        # full_text = " "
        # full_text = full_text.join(wordList)
        #
        # user = users.get_current_user()
        # email_address = user.nickname()

        if user: #not tested yet
            # now = datetime.utcnow()
            # newJournal = Journal(user=email_address, text=full_text, rgb1=rgb_1, rgb2=rgb_2, year= int(now.year), month = int(now.month), sumSeconds=(int((now.day *60 * 24 * 60) + (now.hour * 60 * 60) + (now.minute * 60) + (now.second))))
            # newJournal.put()
            #
            # time.sleep(5)
            self.redirect("/journal?key=" + str(journal_page.year) +" "+ str(journal_page.month) + " " + str(journal_page.sumSeconds) + " " + str(journal_page.rgb1[0]) + " "+ str(journal_page.rgb1[1]) + " " + str(journal_page.rgb1[2]) + " " + str(journal_page.rgb2[0]) + " "+ str(journal_page.rgb2[1]) + " " + str(journal_page.rgb2[2]))


class Register(webapp2.RequestHandler):

    def post(self): #only called when user is in google but not registered with us, they just filled out a form
        # print("hello is this reached?")

        first_name=self.request.get("firstname").lower()
        last_name=self.request.get("lastname").lower()
        # print(first_name)
        # print(last_name)
        email_address=users.get_current_user().nickname()
        current_user = Person(
            first_name=first_name,
            last_name=last_name,
            email = email_address

        )
        # print(current_user)
        current_user.put()
        time.sleep(5)
        self.redirect('/')



    def get(self):
        # print("hello get?")
        user = None
        existing_user = None
        login_url = None
        logout_url = None
        user = users.get_current_user() # will return a user if someone is signed in, if not, none
        existing_user = None
        if user:
            email_address = user.nickname()
            existing_user = Person.query().filter(Person.email == email_address).get() #query if we already have that email #get pulls only one
            logout_url = users.create_logout_url('/')
            if existing_user:
                self.redirect('/')
        else:
            login_url = users.create_login_url('/register')
            self.redirect(login_url)

        reg_dict ={
        "user": user,
        "existing_user": existing_user,
        "logout_url": logout_url,
        "login_url": login_url
        }
        register_template = jinja_env.get_template("/templates/register.html")
        checkLogIn(reg_dict)
        self.response.write(register_template.render(reg_dict))


class Account(webapp2.RequestHandler):
    def get(self):
        # key = self.request.get_all("key")
        # name= key[0].split(' ')
        user = users.get_current_user()
        email_address = user.nickname()

        profilePerson = Person.query().filter(Person.email == email_address).get() # gets the right obj now!!
        journal_query = Journal.query().filter(Journal.user == email_address).order(-Journal.created).fetch() # try w data
        journal_dates = []
        journal_times = []
        journal_keys = []

        for journal in journal_query:
            now = journal.created
            str_day = now.strftime('%m-%d-%Y')
            str_time = now.strftime('%H:%M')
            str_key = str(now.year) + " " + str(now.month) + " " + str(journal.sumSeconds)
            journal_dates.append(str_day)
            journal_times.append(str_time)
            journal_keys.append(str_key)

        #goal - when you click profile, it populates it with the profile of the person you clicked on/ yourself
        acct_dict={
            "firstName": profilePerson.first_name,
            "lastName": profilePerson.last_name, #finish this!!
            "journal_query": journal_query,
            "journal_dates": journal_dates,
            "journal_times": journal_times,
            "journal_keys": journal_keys,
        }
        acct_template = jinja_env.get_template("/templates/account.html")
        checkLogIn(acct_dict)
        self.response.write(acct_template.render(acct_dict))

    def post(self):
        time_key = self.request.get('key_value')
        timeKeyString = unicodedata.normalize('NFKD', time_key).encode('ascii','ignore')
        timeKeyList = timeKeyString.split(" ")
        year = int(timeKeyList[0])
        month = int(timeKeyList[1])
        sumofSeconds = int(timeKeyList[2])

        user = users.get_current_user()
        email_address = user.nickname()

        profilePerson = Person.query().filter(Person.email == email_address).get()
        journal_page = Journal.query().filter(Journal.user == email_address).filter(Journal.year == year).filter(Journal.month == month).filter(Journal.sumSeconds >= sumofSeconds).get()
        journal_page.key.delete()
        time.sleep(LATENCY_TIME)
        self.redirect('/account')


class Speech(webapp2.RequestHandler):
    def get(self):
        speech_template = jinja_env.get_template("/templates/speech.html")
        self.response.write(speech_template.render())

    def post(self):
        data = self.request.get('data')
        text = fileToText(data)
        self.response.write(text)

class Stats(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        email_address = user.nickname()
        profilePerson = Person.query().filter(Person.email == email_address).get() # gets the right obj now!!

        # journal query
        journal_query = Journal.query().fetch()
        wordjournals =[]
        journal_colors = []
        emotion_dict =  {"sad": 0, "angry": 0, "happy": 0, "worried": 0, "confused": 0, "embarrassed": 0, "tired": 0, "none": 0}
        num_entries = len(journal_query)

        for journal in journal_query:
            for i in journal.text.split():
                wordjournals.append(i)
            # this counts the total amount of each emotion that appears first in a entry (* 2) and second (* 1)
            emotion_dict[emotion_from_color(journal.rgb1)] += 1

        # color 'time-line'
        WINDOW_SIZE = 5
        for i in range(len(wordjournals) - WINDOW_SIZE):
            journal_window = wordjournals[i:i+WINDOW_SIZE]
            journal_window_emotions = find_emotions(journal_window)
            journal_window_top_emotion = top_emotions(journal_window_emotions)['first']
            journal_colors.append(journal_window_top_emotion)
        #average dictionary
        reds = []
        greens = []
        blues = []

        for journal in journal_query:
            for index, item in enumerate(journal.rgb1):
                if ((index+3)%3==0):
                    reds.append(item)
                elif((index-1)%3==0):
                    greens.append(item)
                elif((index+1)%3==0):
                    blues.append(item)
        sumreds = 0
        sumgreens =0
        sumblues =0
        for i in range(len(reds)):
            sumreds += reds[i]
            sumblues += blues[i]
            sumgreens += greens[i]

        # average top emotions
        averageRGB = [int((sumreds/len(reds))), int((sumgreens/len(greens))), int((sumblues/len(blues)))]

        stats_data = {
            "first_name": profilePerson.first_name,
            "last_name": profilePerson.last_name,
            "numTotalWords": len(wordjournals),
            "nsad": emotion_dict["sad"],
            "nhappy": emotion_dict["happy"],
            "nangry": emotion_dict["angry"],
            "nworried": emotion_dict["worried"],
            "nconfused": emotion_dict["confused"],
            "nembarrassed": emotion_dict["embarrassed"],
            "ntired": emotion_dict["tired"],
            "r": averageRGB[0],
            "g": averageRGB[1],
            "b": averageRGB[2],
            "numEntries": num_entries,
            "journal_colors": journal_colors
        }


        stats_template = jinja_env.get_template("/templates/stats.html")
        checkLogIn(stats_data)
        self.response.write(stats_template.render(stats_data))

class Slider(webapp2.RequestHandler):
    def get(self):
        key = self.request.get_all("key") #this gives you a string
        print(key)
        keyString = unicodedata.normalize('NFKD', key[0]).encode('ascii','ignore')
        keyList = keyString.split(" ")
        year = int(keyList[0])
        month = int(keyList[1])
        sumofSeconds = int(keyList[2]) #'2019', '10', '1119957']

        user = users.get_current_user()
        email_address = user.nickname()
        print(email_address)

        profilePerson = Person.query().filter(Person.email == email_address).get()
        time.sleep(3)
        journal_page = Journal.query().filter(Journal.user == email_address).filter(Journal.year == year).filter(Journal.month == month).filter(Journal.sumSeconds >= sumofSeconds).get()

        now = journal_page.created


        str_day = now.strftime('%m-%d-%Y')
        str_time = now.strftime('%H:%M')

        emotions = find_emotions(text_to_list(journal_page.text))
        totalEmotions=0
        for emotion in emotions:
            totalEmotions += emotions[emotion]
        percent_emotions = {}
        if totalEmotions != 0:
            percent_emotions["angry"] = round(100*(emotions["angry"]/totalEmotions))
            percent_emotions["sad"] = round(100*(emotions["sad"]/totalEmotions))
            percent_emotions["happy"] = round(100*(emotions["happy"]/totalEmotions))
            percent_emotions["worried"] = round(100*(emotions["worried"]/totalEmotions))
            percent_emotions["confused"] = round(100*(emotions["confused"]/totalEmotions))
            percent_emotions["embarrassed"] = round(100*(emotions["embarrassed"]/totalEmotions))
            percent_emotions["tired"] = round(100*(emotions["tired"]/totalEmotions))
        else:
            percent_emotions["angry"] = 0
            percent_emotions["sad"] = 0
            percent_emotions["happy"] = 0
            percent_emotions["worried"] = 0
            percent_emotions["confused"] = 0
            percent_emotions["embarrassed"] = 0
            percent_emotions["tired"] = 0


        linkpart = str(year) + " " + str(month) + " " + str(sumofSeconds)
        link = ("/journal?key=" + linkpart)
        print(link)
        s_dict = {
            "first_name": profilePerson.first_name,
            "last_name": profilePerson.last_name,
            "diary_entry": journal_page.text,
            "r1": journal_page.rgb1[0],
            "g1": journal_page.rgb1[1],
            "b1": journal_page.rgb1[2],
            "r2": journal_page.rgb2[0],
            "g2": journal_page.rgb2[1],
            "b2": journal_page.rgb2[2],
            "date": str_day,
            "time": str_time,
            "link": link,
            "angry": percent_emotions["angry"],
            "sad": percent_emotions["sad"],
            "happy": percent_emotions["happy"],
            "worried": percent_emotions["worried"],
            "confused": percent_emotions["confused"],
            "embarrassed": percent_emotions["embarrassed"],
            "tired": percent_emotions["tired"],

        }

        s_template = jinja_env.get_template("/templates/slider.html")
        self.response.write(s_template.render(s_dict))

    def post(self):
        text = fileToText(self.request.get("data"))
        if text == None:
            self.redirect('/ramble')
            return
        text = unicodedata.normalize('NFKD', text).encode('ascii','ignore')
        wordList = filterFillers(text)
        emotions = find_emotions(wordList)
        topemotions = top_emotions(emotions) #returns a list of top emotions
        rgb_1 = topemotions["first"]
        rgb_2 = topemotions["second"]
        full_text = " "
        full_text = full_text.join(wordList)

        user = users.get_current_user()
        email_address = user.nickname()

        if user: #not tested yet
            now = datetime.utcnow()
            newJournal = Journal(user=email_address, text=full_text, rgb1=rgb_1, rgb2=rgb_2, year= int(now.year), month = int(now.month), sumSeconds=(int((now.day *60 * 24 * 60) + (now.hour * 60 * 60) + (now.minute * 60) + (now.second))))

            newJournal.put()
            time.sleep(2)
            self.redirect("/slider?key=" + str(newJournal.year) +" "+ str(newJournal.month) + " " + str(newJournal.sumSeconds))

        
        # slider_template = jinja_env.get_template("/templates/slider.html")
        # self.response.write(ramble_template.render(slider_dict))
        


app = webapp2.WSGIApplication([
    ('/', HomePage), #this maps the root url to the Main Page Handler
    ('/register', Register),
    ('/ramble', Ramble),
    ('/speech', Speech),
    ('/journal', JournalPage),
    ('/account', Account),
    ('/stats', Stats),
    ('/slider', Slider),
], debug=True)
