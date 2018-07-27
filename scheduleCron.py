from crontab import CronTab


bhagavadgita = CronTab(user='radhakrishna')


# New Job
job = bhagavadgita.new(
    command='python /Users/radhakrishna/Desktop/bhagavadgita/radhakrishna.py', comment='radhakrishna')
job.minute.on(35)
job.hour.on(5)
job.minute.every(1)
bhagavadgita.write()


# Remove a cron job
# bhagavadgita.remove_all()
# bhagavadgita.write()
