from crontab import CronTab

cron = CronTab(user='radhakrishna')  


job = cron.new(
    command='python /Users/radhakrishna/Desktop/bhagavadgita/example.py')
job.minute.every(1) 


# for item in cron:
#     print(item)

# cron.remove_all()

cron.write()
