ps -ef | grep "python3 discordbot.py" | awk '{print $2}' | xargs kill -9
rm nohup.out
nohup python3 discordbot.py &