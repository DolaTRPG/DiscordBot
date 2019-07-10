import configurations
import requests


async def log(bot, content):
    """send log to log channel
    """
    log_channel = configurations.key['log_channel']
    await bot.get_channel(int(log_channel)).send(content)


def create_gist(filename, description, content):
    """create gist with content
    Args:
        - (str) filename: filename of content, will also be gist name
        - (str) description: description for this gist
        - (str) content: file content
    Return:
        - (str) html url for this gist
    """
    request_payload = {
        'description': description,
        'public': False,
        'files': {
            filename: {
                'content': content
            }
        }
    }
    request_header = {"Authorization": "Basic " + configurations.key['gist_auth']}
    response = requests.post(url='https://api.github.com/gists', json=request_payload, headers=request_header)
    return response.json()['html_url']
