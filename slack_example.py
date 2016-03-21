import time
import requests

from SlackBotFramework import SlackBot, SlackEvent

# Some custom handler for your chat client, slack - irc - whatever
if __name__ == '__main__':
    from slackclient import SlackClient
    import json
    import re

    client = SlackClient("")
    bot = SlackBot(client)

    def send_card(channel, title, title_url, text, fields=None,
                  bot_name="Bot", color="#36a64f", fallback="There was an error please try again"):
        attr = [{
            "fallback": fallback,
            "color": color,
            "title": title,
            "title_link": title_url,

            "text": text
        }]

        if fields:
            if not isinstance(fields, list):
                fields = [fields]
            attr[0]['fields'] = fields

        return client.api_call(
            "chat.postMessage",
            as_user=True,
            username=bot_name,
            channel=channel,
            text="",
            attachments=json.dumps(attr))

    def get_user_games(name, key=""):

        url = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=%s&vanityurl=%s" % (key, name)
        req = requests.get(url)
        steam_id = req.json().get('response', {}).get('steamid')
        if not steam_id:
            return False

        url =   "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=%s&steamid=%s&format=json" % (key, steam_id)
        return requests.get(url).json()

    @bot.on('message', '!steam games (.+)')    
    def hi_reply(event):

        user = re.findall(r'!steam games (.+)', event.text)
        if not user:
            return client.rtm_send_message(event.channel, "Invalid usage.")

        user = user[0]
        user_games = get_user_games(user)
        if not user_games:
            return client.rtm_send_message(event.channel, "User %(user)s not found" % {'user': user})

        games = user_games.get('response', {})

        client.rtm_send_message(event.channel, "<http://steamcommunity.com/id/%(user)s/games|%(user)s> has %(no_games)s game(s)." % {'user': user, 'no_games':games.get('game_count')})
        # print(send_card(
        #             event.channel,
        #             title='URLS',
        #             title_url='http://google.com',
        #             text="<http://imgur.com|imgur> \n <http://facebook.com|facebook>"))

    # @bot.timed(5)   
    # def on_timer():
    #     print("Timer, 5", time.time())

    while not client.rtm_connect():
        time.sleep(0.1)
    else:
        print("Connected")

    while True:
        for data in client.rtm_read():

            event = SlackEvent(data)
            bot.handle(event)

        bot.handle_timers()
        time.sleep(0.01)


