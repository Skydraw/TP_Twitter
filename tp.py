# coding: utf-8 
import sqlite3
import sys
import os
import argparse
import hashlib
import re

parser = argparse.ArgumentParser()
parser.add_argument('-u', action='store', dest='username', help='Specify a domain to scan')
parser.add_argument('-p', action='store', dest='password', help='Specify a domain to scan')
parser.add_argument('-f', action='store', dest='function', help='Specify a domain to scan')
parser.add_argument('-i', action='store', dest='UserID', help='Specify a domain to scan')
parser.add_argument('-t', action='store', dest='tweet', help='Specify a domain to scan')
parser.add_argument('-c', action='store', dest='cookie', help='Specify a domain to scan')
args = parser.parse_args()





# Fonction BDD 
def initdb():
    db_path = "/tmp/test.db"
    conn = None

    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS `tweets` (
`TweetID` INTEGER,
`UserID` INTEGER,
`tweet` TEXT,
`date` TEXT,
PRIMARY KEY(`TweetID`)
);""")

        c.execute("""CREATE TABLE IF NOT EXISTS `users` (
     `UserID` INTEGER,
     `login` TEXT,
     `password` TEXT,
     PRIMARY KEY(`UserID`)
    );
    """)
        conn.commit()
        conn.close()

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    return (conn,c)

## Gestion de la sécurité 
serverKey = "0u64xoh9kv6h6cf"

def isText(text):
    regex = r"[\W]"
    if bool(re.search(regex,text)):
        result = 1
    else:
        result = 0
    return result
    




    

## Fonctions Login / Register
#tp register should return session token for this new user or session token for already registered user
def register(username,password):
    if isText(username) == 0 and isText(password) == 0:
        conn, c = initdb()
        #Si user existe
        c.execute("select * from `users` where login = '{}' and password = '{}';".format(username,password))
        if c.fetchone() is not None:
            mapCookie = open("MapCookie" , "r")
            for ligne in mapCookie:
                if username in ligne:
                    cookie = ligne.split(":")
                    return cookie[1]            
            mapCookie.close()
        else:
        #Si user n'existe pas
            cookie= hashlib.sha1()
            cookie.update(serverKey + username)
            c.execute("insert into `users`('login', 'password') VALUES('{}','{}');".format(username, password))
            conn.commit()
            mapCookie = open("MapCookie" , "a")
            mapCookie.write("\n"+username+":"+cookie.hexdigest())
            mapCookie.close()
            return login(username,password)
        conn.close()
    else:
        return None


#tp login should return session token for this existing user or nothing if there is no user with those credentials")
def login(username,password):
    # Test des caratères spéciaux dans username et password
    if isText(username) == 0 and isText(password) == 0:
        conn, c = initdb()
        c.execute("select * from `users` where login = '{}' and password = '{}';".format(username,password))
        if c.fetchone() is not None:
            mapCookie = open("MapCookie" , "r")
            for ligne in mapCookie:
                if username in ligne:
                    cookie = ligne.split(":")
                    return cookie[1]            
            mapCookie.close()
        else:
            return None
        conn.close()
    else:
        return None

#getting user name by calling : tp userIdFromSession"
def get_userId_from_session(cookie):
    mapCookie = open("MapCookie" , "r")
    for ligne in mapCookie:
        if cookie in ligne:
            username = ligne.split(":")
            return get_user_id(username[0])
    mapCookie.close()




## Fonctions Utilisateurs
def get_user_password(UserID):
    conn, c = initdb()
    c2 = c.execute("select password,UserID from `users` WHERE UserID ='{}';".format(UserID))
    res = c2.fetchall()
    return "{}".format(res[0][0])
    conn.close()

def get_user_name(UserID):
    conn, c = initdb()
    c2 = c.execute("select login,UserID from `users` WHERE UserID ='{}';".format(UserID))
    res = c2.fetchall()
    if(len(res) > 0):
        return "{}".format(res[0][0])
    conn.close()
    
def get_user_id(username):
    conn, c = initdb()
    c2 = c.execute("select UserID, login from `users` WHERE login ='{}';".format(username))
    res = c2.fetchall()
    if(len(res) > 0):
        return "{}".format(res[0][0])
    conn.close()

def get_list_userId():
    conn, c = initdb()
    c2 = c.execute("select UserID from `users`")
    res = c2.fetchall()
    tab = []
    for i in range(len(res)):
        tab.append(str(i+1))
    return ",".join(tab)    
    

## Fonctions Tweets
def register_tweet(UserID,tweet):
    conn, c = initdb()
    c.execute("insert into `tweets`('UserID', 'tweet', 'date') VALUES('{}','{}', datetime('now'));".format(UserID, tweet ))
    conn.commit()
    conn.close()

def get_tweet_content(TweetID):
    conn, c = initdb()
    c2 = c.execute("select tweet,TweetId from `tweets` WHERE TweetId ='{}';".format(TweetID))
    res = c2.fetchall()
    if(len(res) > 0):
        return "{}".format(res[0][0])
    conn.close()
    
def get_tweet_date(TweetID):
    conn, c = initdb()
    c2 = c.execute("select date,TweetId from `tweets` WHERE TweetId ='{}';".format(TweetID))
    res = c2.fetchall()
    if(len(res) > 0):
        return "{}".format(res[0][0])
    conn.close()
    
    
def get_tweet_userid(TweetID):
    conn, c = initdb()
    c2 = c.execute("select UserID,TweetId from `tweets` WHERE TweetId ='{}';".format(TweetID))
    res = c2.fetchall()
    if(len(res) > 0):
        return "{}".format(res[0][0])
    conn.close()


def list_tweet_for_user_ids(UserID):
    conn, c = initdb()
    c2 = c.execute("select tweet from `tweets` WHERE UserID='{}';".format(UserID))
    res = c2.fetchall()
    if(len(res) > 0):
        return "\n".join(map(lambda v:"{}".format(v[0]),res))
    conn.close()
    

def printIfNotNone(content):
    if (content):
        print content

if args.function == 'login':
    printIfNotNone(login(args.username,args.password))
elif args.function == 'register':
    printIfNotNone(register(args.username,args.password))
elif args.function == 'get_user_password':
    printIfNotNone(get_user_password(args.UserID))
elif args.function == 'get_user_name':
    printIfNotNone(get_user_name(args.UserID))
elif args.function == 'get_user_id':
    printIfNotNone(get_user_id(args.username))
elif args.function == 'register_tweet':
    register_tweet(args.UserID,args.tweet)
elif args.function == 'get_tweet_content':
    printIfNotNone(get_tweet_content(args.TweetID))
elif args.function == 'get_tweet_date':
    printIfNotNone(get_tweet_date(args.TweetID))
elif args.function == 'get_tweet_userid':
    printIfNotNone(get_tweet_userid(args.TweetID))
elif args.function == 'get_list_userId':
    printIfNotNone(get_list_userId())
elif args.function == 'list_tweet_for_user_ids':
    printIfNotNone(list_tweet_for_user_ids(args.UserID))
elif args.function == 'get_userId_from_session':
    printIfNotNone(get_userId_from_session(args.cookie))

    





    
    
