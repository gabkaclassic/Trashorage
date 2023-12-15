from environs import Env

env = Env()
env.read_env()

bot_token = env.str('BOT_TOKEN')

redis_db = {
    'user': env.str('REDIS_USER'),
    'password': env.str('REDIS_PASSWORD'),
    'host': env.str('REDIS_HOST'),
    'port': env.int('REDIS_PORT'),
}
redis_connection_string = "redis://%(user)s:%(password)s@%(host)s:%(port)d" % redis_db

opensearch_verify = env.bool('OPENSEARCH_VERIFY_SSL', True)
opensearch_creds = (
    env.str('OPENSEARCH_USER'),
    env.str('OPENSEARCH_PASSWORD')
)
opensearch_url = f'https://{env.str("OPENSEARCH_HOST")}:{env.int("OPENSEARCH_PORT")}'

key_path = env.str('KEY_PATH')
encrypt_key = open(key_path, 'rb').read()

logging_path = env.str('LOG_PATH')