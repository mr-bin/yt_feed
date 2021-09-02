import os
import asyncio
import datetime
import traceback
import logging.config

from telegram import Bot, ParseMode
from pyyoutube import Api

from yt_feed.config import config
from yt_feed.lock import get_lock_value, set_lock_value

logging.config.dictConfig(config['logging'])

youtube_logger = logging.getLogger('youtube')
telegram_logger = logging.getLogger('telegram')
bot_logger = logging.getLogger('bot')


def post_messages(bot, channel_name, latest_videos):
    for one in latest_videos:
        status = bot.send_message(chat_id=channel_name,
                                  text=f'<b>{one["channel_title"]}</b> - <i>{one["published"]}</i> \n\n{one["video_title"]} \n{one["url"]}',
                                  parse_mode=ParseMode.HTML)
        status = status.to_dict()
        telegram_logger.debug('send_message', extra={'chat': status['chat'],
                                                     'text': status['text']})


def get_latest_videos(api, channel):
    channel_res = api.get_channel_info(channel_id=channel['id'])

    playlist_id = channel_res.items[0].contentDetails.relatedPlaylists.uploads
    channel_title = channel_res.items[0].snippet.title
    playlist_item_res = api.get_playlist_items(playlist_id=playlist_id, count=channel['count_to_list'])

    last_ts = get_lock_value(f'{channel["id"]}.lock')

    latest_videos = []

    for one in playlist_item_res.items:
        snippet = one.to_dict()['snippet']
        content_details = one.to_dict()['contentDetails']
        published_at = snippet['publishedAt']
        published_at_parsed = datetime.datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ').replace(
            tzinfo=datetime.timezone.utc)
        published_at_ts = int(published_at_parsed.timestamp())
        if published_at_ts > last_ts:
            latest_videos.append({'published_at': snippet['publishedAt'],
                                  'published_at_ts': published_at_ts,
                                  'published': published_at_parsed.strftime('%d %B %Y %H:%M'),
                                  'channel_title': channel_title,
                                  'video_title': snippet['title'],
                                  'url': f'http://www.youtube.com/watch?v={content_details["videoId"]}'
                                  })

    latest_videos = sorted(latest_videos, key=lambda x: x['published_at_ts'])
    youtube_logger.debug('get_playlist_items', extra={
        'channel_title': channel_title,
        'channel_id': channel['id'],
        'latest_videos': latest_videos})

    if latest_videos:
        set_lock_value(f'{channel["id"]}.lock', latest_videos[-1]['published_at_ts'])

    return latest_videos


async def periodic(tg_bot, yt_api, tg_channel, yt_channel):
    while True:
        try:
            latest_videos = get_latest_videos(yt_api, yt_channel)
            post_messages(tg_bot, tg_channel, latest_videos)
        except Exception:
            bot_logger.debug("Some exception happened", extra={'exception': traceback.print_exc()})
        await asyncio.sleep(yt_channel['delay'])


def main():
    TG_HTTP_API_TOKEN = config['TG_HTTP_API_TOKEN'] if config.get('TG_HTTP_API_TOKEN') else os.environ.get('TG_HTTP_API_TOKEN')
    YT_API_KEY = config['YT_API_KEY'] if config.get('YT_API_KEY') else os.environ.get('YT_API_KEY')

    tg_bot = Bot(token=TG_HTTP_API_TOKEN)
    yt_api = Api(api_key=YT_API_KEY)

    loop = asyncio.get_event_loop()

    tasks = []
    for feed in config['feeds']:
        for yt_channel in feed['yt_channels']:
            tasks.append(loop.create_task(periodic(tg_bot, yt_api, feed['tg_channel'], yt_channel)))

    try:
        for task in tasks:
            loop.run_until_complete(task)
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    main()
