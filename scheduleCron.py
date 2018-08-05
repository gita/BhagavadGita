from crontab import CronTab


bhagavadgita = CronTab(user='radhakrishna')


# New Job
job = bhagavadgita.new(
    command='cd /home/radhakrishna/radhakrishna && source venv/bin/activate && python /home/radhakrishna/radhakrishna/radhakrishna.py', comment='radhakrishna')
job.minute.on(21)
job.hour.on(20)
job.enable()
bhagavadgita.write()
if bhagavadgita.render():
    print(bhagavadgita.render())


# Remove a cron job

# for item in bhagavadgita:
#     print(item)

# bhagavadgita.remove_all()


# bhagavadgita.write()
