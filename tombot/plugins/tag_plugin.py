'''
Tags: shout at multiple people at once, if wanted.
'''
import sqlite3
import re

from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity

from tombot.helper_functions import reply_directly, determine_sender, extract_query
from tombot.registry import Command, get_easy_logger, Subscribe, BOT_MSG_RECEIVE
from tombot.plugins.users_plugin import jid_to_nick


LOGGER = get_easy_logger('tags')
TAG_PATTERN = r'(?:\s|^)#([^ .:,]+)'
TAG_REGEX = re.compile(TAG_PATTERN, re.MULTILINE)

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
        return 'Tag "{}" does not exist!'.format(tagname)

@Command('unsubscribe-all')
@reply_directly
def unsubscribe_all_cb(bot, message, *args, **kwargs):
    ''' Unsubscribe immediately from all tags. '''
    senderjid = determine_sender(message)

    bot.cursor.execute('DELETE FROM tag_subscriptions WHERE jid=?',
                       (senderjid,))

    return 'Successfully unsubscribed from {} tags.'.format(bot.cursor.rowcount)

# Message handler
@Subscribe(BOT_MSG_RECEIVE)
def tag_handler_cb(bot, message, *args, **kwargs):
    ''' Scan incoming messages for #tags and send copies to subscribers. '''
    recipients = set()
    results = TAG_REGEX.findall(message.getBody())
    for match in results:
        for subscriber in tag_subscribers(bot, match):
            recipients.add(subscriber)

    senderjid = determine_sender(message)
    try:
        sendername = jid_to_nick(bot, senderjid)
    except KeyError:
        LOGGER.warning('Unregistered jid %s tried to use a tag.')
        return # unregistered users may not use tags.

    try:
        recipients.remove(determine_sender(message))
    except KeyError:
        pass # Sender does not have to be subscribed to the tag.

    for recipient in recipients:
        entity = TextMessageProtocolEntity(
            '{}: {}'.format(sendername, message.getBody()),
            to=recipient)
        bot.toLower(entity)

def tag_subscribers(bot, tagname):
    '''
    Return a list of subscribers (jid) to a given tag.

    Empty list is returned if tag does not exist.
    '''
    tagid = tag_to_id(bot, tagname, create=False)
    if not tagid:
        return []

    bot.cursor.execute('SELECT jid FROM tag_subscriptions WHERE id=?', (tagid,))
    results = bot.cursor.fetchall()
    return results

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
