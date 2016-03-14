'''
Tags: shout at multiple people at once, if wanted.
'''
import sqlite3

from tombot.helper_functions import reply_directly, determine_sender, extract_query
from tombot.registry import Command, get_easy_logger


LOGGER = get_easy_logger('tags')

@Command('subscribe')
@reply_directly
def subscribe_cb(bot, message, *args, **kwargs):
    ''' Subscribe to a tag. '''
    senderjid = determine_sender(message)
    tagname = extract_query(message).strip()
    if ' ' in tagname:
        return 'Tags must not contain spaces!'

    bot.cursor.execute('SELECT id FROM tags WHERE name LIKE ?',
                       (tagname,))
    result = bot.cursor.fetchone()
    tagid = None
    if not result:
        bot.cursor.execute('INSERT INTO tags (name) VALUES (?)',
                           (tagname,))
        tagid = bot.cursor.lastrowid
        LOGGER.info('%s created.', tagname)
    else:
        tagid = result[0]

    try:
        bot.cursor.execute('INSERT INTO tag_subscriptions (id, jid) VALUES (?,?)',
                           (tagid, senderjid))
    except sqlite3.IntegrityError:
        return 'You are already subscribed to that tag!'

    return 'Success!'
