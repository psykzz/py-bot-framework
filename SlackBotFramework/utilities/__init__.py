def send_card(client, channel, title, title_url, text, fields=None,
              bot_name="Bot", color="#36a64f",
              fallback="There was an error please try again"):
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
