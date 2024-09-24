from datetime import datetime
import datetime
import pandas as pd
import time
import mysql.connector
#import sensitive
import os

# Ask user to month date and year to search reddit
# date_month = int(input("Month to Search? "))
# if date_month in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
#     date_month = ("0" + str(date_month))
# date_day = int(input("Day to search? "))
# if date_day in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
#     date_day = ("0" + str(date_day))
# date_year = int(input("Year to search? "))

yestDate = datetime.datetime.today()
yestDate = yestDate - datetime.timedelta(days=1)
print(yestDate)

date = yestDate.strftime("%m/%d/%Y")
date_csv = yestDate.strftime("%m-%d-%Y")
print(date)
print(date_csv)


# One date format is to compare with datetime format, the other is so it can be used in csv file name
# cannot use slashes in file name so one format has dashes
# date = ("%s/%s/%d" % (date_month, date_day, date_year))
# date_csv = ("%s-%s-%d" % (date_month, date_day, date_year))



# Main method that grabs posts/comments and date
def post_and_timestamps(reddit):
    # cnx = mysql.connector.connect(user='dtujo', password='dtujo-mys', host='localhost', database='DataSAIL')
    # myCursor = cnx.cursor()
    # Creates a new and empty dataframe
    subreddit_list = ["Frugal"]
    fileList = []




    # for loop that loops for every subreddit in subreddit list entered by user.
    for subreddit in subreddit_list:
        df = pd.DataFrame(columns=['Timestamp', 'Subreddit', 'Post/Comment'])
        print("Grabbing from ", subreddit, flush=True)
        # Praw function that grabs posts from subreddit, saves it to a variable
        new_posts = reddit.subreddit(subreddit).new(limit=None)

        # Counter for testing and debugging purposes to be monitored in the run terminal
        post_number = 0
        # Loops through posts that were grabbed from praw function.
        for post in new_posts:
            # Several print statements for monitor, test, debug purposes
            post_number += 1
            # print("Post" + str(post_number))
            # changes post date from unix into utc timestamp and saves it to a variable.
            post_date = datetime.datetime.utcfromtimestamp(post.created).strftime('%m/%d/%Y')
            # print(post_date)
            # print(date)



            # if statement, compares date from user to date of post. If the same, appends row to df
            if post_date == date:
                # print("Grabbed post " + str(post_number))
                # print(post.title)
                # print('----------------')
                # Grabs post title, encodes and decodes to avoid errors with reddit flavor, images, etc
                title = post.title.encode(encoding='UTF-8', errors='ignore')
                titleTwo = title.decode('UTF-8')
                # Grabs post body, same as above
                body = post.selftext.encode(encoding='UTF-8', errors='ignore')
                bodyTwo = body.decode('UTF-8')
                # concatenates post body and title to be viewed as one entity
                body_title = titleTwo + " " + bodyTwo
                # creates variable for timestamp of post creation
                dateTest = datetime.datetime.utcfromtimestamp(post.created).strftime('%Y-%m-%d')
                date_time_obj = datetime.datetime.strptime(dateTest, "%Y-%m-%d")

                # sql_line = "INSERT INTO dailyRedditData (date, source, content) VALUES (%s, %s, %s)"
                # values = (date_time_obj, subreddit, body_title)
                #
                # try:
                #     myCursor.execute(sql_line, values)
                #     cnx.commit()
                # except:
                #     cnx.rollback()

                df = df.append({'Timestamp': date_time_obj, 'Subreddit': subreddit, 'Post/Comment': body_title},
                               ignore_index=True)


            else:
                post_number -= 1
                # print statement for monitoring/testing/debugging
                # print("skipped")
                # print('----------------')
                pass


            # while loop used for more comments option in reddit. Reddit uses a comment tree design where
            # each comment is like a directory, each comment can have their own tree and so on and on.
            # .replace_more is a method that interacts to load more comment in what ever tree it is in
            # this action is determined by reddit api's as an event and because we are limited by how many events we
            # can do in a minute, we need to limit the rate at which we are doing these events.
            # this while loop sets a limit on how many times you can use the replace more option. One replace more
            # option gives 19 comments. Thus we can grab 1000 comments from each post. We can grab as many as we want,
            # but will take a LONG time to run this program
            # If an exception occurs for exceeding events, program will wait 1 second before trying again.
            while True:
                try:
                    post.comments.replace_more(limit=50)
                    break
                except Exception:
                    time.sleep(1)
            # comments are saved to a list and iterated through
            for comment in post.comments.list():
                # converting comment unix time stamp to utc timestamp and saved as a variable

                # comment_date = datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d')
                comment_date_check = datetime.datetime.utcfromtimestamp(comment.created_utc).strftime('%m/%d/%Y')
                post_number += 1
                # if statement for comments matching above if statement for posts
                # print("Comment")
                # print(date)
                # print(comment_date_check)
                if post_number % 1000 == 0:
                    print(reddit, post_number)


                if comment_date_check == date:

                    # print("Grabbed comment : " + str(post_number))
                    # print(comment.body)
                    # print("---------------------------------------------")
                    date_comment = comment.created_utc
                    date_time_obj = datetime.datetime.fromtimestamp(date_comment)



                    # sql_line = "INSERT INTO dailyRedditData (DATE, SOURCE, CONTENT) VALUES (%s, %s, %s)"
                    # values = (date_time_obj, subreddit, comment.body)
                    #
                    # try:
                    #     myCursor.execute(sql_line, values)
                    #     cnx.commit()
                    # except:
                    #     cnx.rollback()

                    df = df.append({'Timestamp': date_time_obj, 'Subreddit': subreddit, 'Post/Comment': comment.body},
                                   ignore_index=True)

                else:
                    post_number -= 1
                    pass
                    # print("skipped")
                    # print("---------------------------------------------")
        fileList.append("%s_%s.csv" % (subreddit, date_csv))
        df.to_csv(r'/home/dtujo/myoptane/Trawler/Dataframes/%s_%s.csv' % (subreddit, date_csv), index=False)
        print("Post/Comments Grabbed: ", post_number, " from ", subreddit, flush=True)
        # df.to_csv(r'D:\Git\lewisuDataSAIL\Dataframes\%s_%s.csv' % (subreddit, date_csv), index=False)
    return fileList