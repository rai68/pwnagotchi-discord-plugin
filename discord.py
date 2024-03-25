import logging
import requests
import json

import pwnagotchi
import pwnagotchi.ui.faces as faces
import pwnagotchi.plugins as plugins

# Installing:

# Move plugin file to your custom plugins directory `sudo cat /etc/pwnagotchi/config.toml | grep main.custom_plugins` 
# Add this to your pwnagotchi config (/etc/pwnagotchi/config.yml):

#main.plugins.discord.enabled = true
#main.plugins.discord.webhook_url = "webhook-url-here"


# Testing:
# You can trigger the webhook to rerun without a new session by deleting the session file:
# sudo rm /root/.pwnagotchi-last-session

# counter on screen how many blind epochs, internet conenctivity icon?

class Discord(plugins.Plugin):
    __author__ = 'charagarlnad, changes for opwngrid/jay base image by rai@discord '
    __version__ = '1.1.1'
    __license__ = 'GPL3'
    __description__ = 'Sends Pwnagotchi status webhooks to Discord.'

    def on_loaded(self):
        logging.info('Discord plugin loaded.')

    def on_internet_available(self, agent):
        display = agent.view()
        last_session = agent.last_session

        if last_session.is_new() and last_session.handshakes > 0:
            logging.info('Detected a new session and internet connectivity!')

            # NOT /root/pwnagotchi.png, as we want to send the screen as it is _before_ the sending status update is shown.

            # need to find where this is on jays image
            picture = '/dev/shm/pwnagotchi.png'

            display.on_manual_mode(last_session)
            display.update(force=True)
            display.image().save(picture, 'png')

            logging.info('Sending Discord webhook...')
            display.set('status', 'Sending Discord webhook...')
            display.update(force=True)

            try:
                data = {
                    'embeds': [
                        {
                            'title': 'Pwnagotchi Status',
                            'color': 3553599,
                            'description': 'New Pwnagotchi status update available! Here\'s some stats from the last session:',
                            'url': f'https://opwngrid.xyz/search/{agent.fingerprint()}',
                            'fields': [
                                {
                                    'name': 'Uptime',
                                    'value': last_session.duration,
                                    'inline': True
                                },
                                {
                                    'name': 'Epochs',
                                    'value': last_session.epochs,
                                    'inline': True
                                },
                                {
                                    'name': 'Average Reward',
                                    'value': str(last_session.avg_reward),
                                    'inline': True
                                },
                                {
                                    'name': 'Deauths',
                                    'value': last_session.deauthed,
                                    'inline': True
                                },
                                {
                                    'name': 'Associations',
                                    'value': last_session.associated,
                                    'inline': True
                                },
                                {
                                    'name': 'Handshakes',
                                    'value': last_session.handshakes,
                                    'inline': True
                                }
                            ],
                            'footer': {
                                'text': f'Pwnagotchi v{pwnagotchi.__version__} - Discord Plugin v{self.__version__}'
                            },
                            'image': {
                                'url': 'attachment://pwnagotchi.png'
                            }
                        }
                    ]
                }
                try:
                    with open(picture,'rb') as image:
                        requests.post(self.options['webhook_url'], files={'image': image, 'payload_json': (None, json.dumps(data))})
                except:
                    requests.post(self.options['webhook_url'], files={'payload_json': (None, json.dumps(data))})
                # This kinda sucks as the saved session ID is global for all plugins, and was added to core only for the twitter plugin
                # So the Discord plugin as of now is incompatable with the Twitter plugin
                # If the session saving could be modified to either be unique for every plugin or each plugin has to implement it itself it should be better
                # I might just implement it myself tbh if it doesn't get changed and someone wants to use twitter plugin at the same time
                last_session.save_session_id()

                logging.info('Webhook sent!')
                display.set('status', 'Webhook sent!')
                display.update(force=True)
            except Exception as e:
                logging.exception('An error occured in the Discord plugin.')
                display.set('face', faces.BROKEN)
                display.set('status', 'An error occured in the Discord plugin.')
                display.update(force=True)
