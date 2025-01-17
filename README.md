# Housing scrapper

In my pursue of a new place to live, I was tired of having to remember which properties I've already checked, and also having to remember to go to the listings sites.

When I started bookmarking the queries I did in every listing site I realized what I was doing could be easily automated, and voilà!

Meet housing scrapper, an app that queries the listings sites for you and notifies you over Telegram when a new property shows up. It remembers the one it notified you about so you won't receive the same property again.

This initial version is aimed at the Argentinean market, therefore there are only providers that list housing in Argentina.

I'd love to receive comments, bugs, ideas, suggestion (I don't use Python daily, please help me be more pythonic if you'd like to), etc. Hit me at rodrigouroz@gmail.com or file an issue in the repo.

## Virtual environment

- Activate: `source venv/bin/activate`
- Deactivate: `deactivate`

## Installation

This was tested with Python 3.8. To install dependencies:

`pip3 install -r requirements.txt`

## Configuration

There's a `configuration.sample.yml` that you can use as a template for your configuration. Copy that file to a new one in the root folder and name it `configuration.yml`

You need to configure two aspects of the script: the listing providers and the notifier.

For the notifier you need to create a Telegram bot first: [Create a Telegram bot](https://core.telegram.org/bots)

Creating the bot will give you an authorization token. Save it for later, you'll need it.

A bot can't talk with you directly, you have two options: you talk to it first, thus allowing it to reply to you, or you can add it to a group. Whatever option you choose, you need to get the `chat_id` of either your account or the group.

After you've done either of the above, run this little script to find the `chat_id` (replace with your authorization token):

```python
import telegram
bot = telegram.Bot(token=MY_TOKEN)
print([u.message.chat.id for u in bot.get_updates()])
```
You'll see a list with an element, that's the `chat_id` you need to save for later. Write it down :-)

With the authorization token and the chat id you can now configure the notifier. Here's an example:

```yaml
notifier:
    messages:
      - 'Hey, I have found new properties. Check them out:'
      - 'I hope it is lucky day today:'
    enabled: true
    chat_id: <CHAT_ID>
    token: <TOKEN>
```

One down, one more to go. Now we need to configure the providers. For the sake of simplicity I'll include a sample, which I hope will be good enough:

```yaml
providers:
  zonaprop:
    base_url: 'https://www.zonaprop.com.ar'
    sources:
      - '/departamentos-alquiler-2-habitaciones.html'
      - '/ph-alquiler-2-habitaciones.html'
  argenprop:
    base_url: 'https://www.argenprop.com'
    sources:
      - '/departamento-alquiler-pais-argentina-2-dormitorios'
      - '/ph-alquiler-pais-argentina-2-dormitorios'
  mercadolibre:
    base_url: 'https://inmuebles.mercadolibre.com.ar'
    sources:
      - '/departamentos/alquiler/2-dormitorios/'
      - '/casas/alquiler/2-dormitorios/'
  properati:
    base_url: 'https://www.properati.com.ar'
    sources:
      - '/departamento/alquiler/ambientes:2'
  inmobusqueda:
    base_url: 'https://www.inmobusqueda.com.ar'
    sources:
      - '/departamento-alquiler-la-plata-casco-urbano.html?cambientes=2.'
```

If you have issues with SSL certificates you can disable SSL validation with the attribute `disable_ssl`, by default it is enabled.

One final step, you need to initialize the database. Just run `python3 setup.py` and that's it. It will create a sqlite3 db file in the root folder.

You're all set. Now run `python3 main.py` and sit tight!

## Testing

Well, perhaps `testing` is a big word for this. You can run a module that tests that the providers configured can properly scrap information. If they work, you should see the listings in your console.

To test: `python3 -m tests`

## Running

That's up to you. What I've found more useful is to run it once an hour. For that I put it in the crontab:

`0 * * * * cd /<PATH_TO_PROJECT>/housing_tracker && python3 main.py >> run.log 2>&1`

You can also set the configuration `infinite_frequency: true` to make the script execute forever -script executes, sleeps 30 seconds, script executes, sleeps 30 seconds, ...-.
