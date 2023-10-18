ps -ef | grep "python3 telegrambot.py" | awk '{print $2}' | xargs kill -9
rm nohup.out
nohup python3 telegrambot.py &
# bash start.sh