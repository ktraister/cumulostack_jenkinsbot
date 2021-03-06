import requests
import json
import time
import jenkins
import datetime

#bot token is used to write, access_token is used to read
access_token = ""
bot_token = ""
history_url = "https://slack.com/api/channels.history"
message_url = "https://slack.com/api/chat.postMessage"
channel_id ="CG8L5GUEQ"

print("STARING PYBOT...")
#start_time = time.timestamp()

server = jenkins.Jenkins('http://localhost:49001', username='admin', password='')

def list_jobs():
    jobs = server.get_jobs()
    final_jobs = ""
    for job in jobs:
        print(job['name'])
        name = job['name']
        url = job['url']
        currjob = "%s --> %s\n" % (name, url)
        final_jobs = "%s %s" % (final_jobs, currjob)
    print("returning " + final_jobs)
    return final_jobs

def run_job(JOB):
    JOB = "".join(e for e in JOB)
    print("CALLING JOB")
    #if server.build_job returns 2, it's good
    try:
        print(server.build_job(JOB))
        return "Started build job %s" % JOB
    except Exception as e:
        print(str(e))
        if "Requested item could not be found" in str(e):
            return "I'm sorry, this job doesn't exist"
        elif "409 Client Error: Conflict for url:" in str(e):
            return "I'm sorry, this job seems to be disabled"

def job_status(JOB):
    JOB = "".join(e for e in JOB)
    print("CHECKING JOB STATUS ", JOB)
    try:
        last_build_number = server.get_job_info(JOB)['lastBuild']['number']
        build_info = server.get_build_info(JOB, last_build_number)
        description = build_info['actions'][0]['causes'][0]['shortDescription']
        artifacts = build_info['artifacts']
        building = build_info['building']
        duration = build_info['duration']
        result = build_info['result']
        composite_build = "JOB NAME: " + str(JOB) + "\n" +                        \
                          "LAST BUILD DESCRIPTION: " + str(description) + "\n" +  \
                          "BUILDING: " + str(building) + "\n" +                   \
                          "DURATION: " + str(duration) + "MS" + "\n" +            \
                          "BUILD NUMBER: " + str(last_build_number) + "\n" +      \
                          "RESULT: " + str(result) + "\n" +                       \
                          "ARTIFACTS: " + str(artifacts) + "\n"
        print(composite_build)
        return composite_build
    except Exception as e:
        print(str(e))
        if "does not exist" in str(e):
            return "I'm sorry, this job doesn't exist"

def handler(FUNC):
    return FUNC()

switcher = {
        " are you ok?": "Yes Dr. Falken!",
        " list all jobs": handler(list_jobs),
        " list commands": "list all jobs, run job, status of job, are you ok?"
        }


while True:
    #req_string = "%s%s%s%s%s%s" % (history_url, "?token=", access_token, "&channel=", channel_id, "&oldest=", str(start_time))
    req_string = "%s%s%s%s%s" % (history_url, "?token=", access_token, "&channel=", channel_id)

    output = requests.get(req_string)
    myjson = json.loads(output.text)

    time.sleep(1)
    for message in myjson['messages']:
        try:
            with open(".histfile", "r") as f:
                old_messages = f.readlines()
            if "%s%s" % (str(message), "\n") in old_messages:
                continue
        except:
            pass
        msg_text = message['text']
        #print("MY MESSAGE: ", msg_text)
        if "Hey JenkinsPybot" in msg_text:
            mytext = msg_text.split(',', 2)
            print("I got: ", mytext)
            if "run job" in mytext[1]:
                myjob = mytext[1].split(' ')[3:]
                print("RUN JOB TEXT ", mytext)
                replytext = run_job(myjob)
            elif "status of job" in mytext[1]:
                myjob = mytext[1].split(' ')[4:]
                print("RUN JOB TEXT ", mytext)
                replytext = job_status(myjob)
            else:
                replytext = switcher.get(mytext[1], "Sorry, I didn't find a response for that")
            print("I'll respond: ", replytext)
            req_string = "%s%s%s%s%s%s%s" % (message_url, "?token=", access_token, "&channel=", channel_id, "&text=", replytext)
            print(req_string)
            myinput = requests.get(req_string)
            if myinput.status_code != 200:
                print("FAILED TO POST MESSAGE")
            else:
                print("WRITING TO FILE...")
                with open(".histfile", "a") as f:
                    f.write("%s\n" % str(message))
