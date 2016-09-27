import re
import time


class SlackEvent(object):
    def __init__(self, data, client=None):
        self.__dict__ = data

    def __getattr__(self, value):
        return self.__dict__.get(value)

    def __repr__(self):
        return str(self.__dict__)


class SlackBot(object):

    regex_event_types = ['message']

    event_handlers = {}
    timed_handlers = {}
    class_handlers = []

    last_run = time.time()
    uptime = 0

    def __init__(self, client, config=None):
        self.client = client

        self.config = config or {}
        self.config.setdefault('ignore-bots', True)
        self.config.setdefault('bot-name', "Bot")

    def send_card(self, channel, title, title_url, text, fields=None,
                  bot_name=None, color="#36a64f", fallback="There was an error please try again"):
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

        return self.client.api_call(
            "chat.postMessage",
            as_user=False,
            username=bot_name or config.get('bot-name', 'Bot'),
            channel=channel,
            text="",
            attachments=json.dumps(attr))

    def handle_timers(self):
        self.uptime = int(time.time() - self.last_run)
        for interval, handlers in self.timed_handlers.items():
            if self.uptime % interval == 0:
                for handler in handlers:
                    if hasattr(handler, 'last_run') and handler.last_run == self.uptime:
                        continue
                    handler.last_run = self.uptime
                    handler()

                for cls in self.class_handlers:
                    cls.timer(interval)

    def before_handler(self, event):
        # Some custom handler stuff
        # we should add some configuration here to enable or disable some of these features.
        if event.user:

            # Ignore bots
            if self.config.get('ignore-bots', False):
                user = self.client.api_call('users.info', user=event.user).get('user', {})
                if user.get('is_bot'):
                    return

    def handle(self, event):
        self.before_handler(event)
        
        for event_type, handlers in self.event_handlers.items():
            for handler, msg_match in handlers:
                if event.type != event_type and event_type != '*':
                    continue
                if msg_match and event.type in self.regex_event_types \
                        and not re.findall(msg_match, event.text):
                    continue  # Failed to match the regex

                handler(event)

        for cls in self.class_handlers:
            cls.handle(event)

    def on(self, event_type, msg_match=None):
        if msg_match is not None:
            msg_match = re.compile(msg_match)

        def wrap(fn):
            self.event_handlers.setdefault(event_type, [])
            self.event_handlers[event_type].append((fn, msg_match))
            
            def wrapper(*args, **kwargs):
                return fn(*args, **kwargs)
            return wrapper
        return wrap

    def timed(self, interval_seconds):
        # Decorator args
        def wrap(fn):
            # Function object
            self.timed_handlers.setdefault(interval_seconds, [])
            self.timed_handlers[interval_seconds].append(fn)
            def wrapper(*args, **kwargs):
                # Called args
                return fn(*args, **kwargs)
            return wrapper
        return wrap

    def register_class(self, cls):
        self.class_handlers.append(cls)
        
