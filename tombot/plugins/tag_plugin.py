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

    tagid = tag_to_id(bot, tagname)

    try:
        bot.cursor.execute('INSERT INTO tag_subscriptions (id, jid) VALUES (?,?)',
                           (tagid, senderjid))
    except sqlite3.IntegrityError:
        return 'You are already subscribed to that tag!'

    return 'Success!'

@Command('unsubscribe')
@reply_directly
def unsubscribe_cb(bot, message, *args, **kwargs):
    ''' Unsubscribe from a tag. '''
    senderjid = determine_sender(message)
    tagname = extract_query(message)

    tagid = tag_to_id(bot, tagname, False)
    if tagid:
        bot.cursor.execute('DELETE FROM tag_subscriptions WHERE id=? AND jid=?',
                           (tagid, senderjid))
        result = bot.cursor.rowcount
        if result == 0:
            return 'You weren\'t even subscribed!'
        else:
            return 'Success!'
    else:
        return 'Tag does not exist!'

# Helper functions
def tag_to_id(bot, tagname, create=True):
    '''
    Translates a tagname to a tag id.

    When create=True, the tag is created if it doesn't exist, on create=False, None is returned.
    '''
    bot.cursor.execute('SELECT id FROM tags WHERE name LIKE ?',
                       (tagname,))
    result = bot.cursor.fetchone()
    tagid = None
    if not result and create:
        bot.cursor.execute('INSERT INTO tags (name) VALUES (?)',
                           (tagname,))
        tagid = bot.cursor.lastrowid
        LOGGER.info('%s created.', tagname)
    elif result:
        tagid = result[0]

    return tagid
