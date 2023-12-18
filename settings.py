from environs import Env

env = Env()
env.read_env()

debug = env.bool('DEBUG', False)

bot_token = env.str('BOT_TOKEN')

redis_db = {
    'user': env.str(f'{"TEST_" if debug else ""}REDIS_USER'),
    'password': env.str(f'{"TEST_" if debug else ""}REDIS_PASSWORD'),
    'host': env.str(f'{"TEST_" if debug else ""}REDIS_HOST'),
    'port': env.int(f'{"TEST_" if debug else ""}REDIS_PORT'),
}
redis_connection_string = "redis://%(user)s:%(password)s@%(host)s:%(port)d" % redis_db

opensearch_verify = env.bool(f'{"TEST_" if debug else ""}OPENSEARCH_VERIFY_SSL', True)
opensearch_creds = (
    env.str(f'{"TEST_" if debug else ""}OPENSEARCH_USER'),
    env.str(f'{"TEST_" if debug else ""}OPENSEARCH_PASSWORD')
)
opensearch_host = env.str(f'{"TEST_" if debug else ""}OPENSEARCH_HOST')
opensearch_port = env.int(f'{"TEST_" if debug else ""}OPENSEARCH_PORT')
opensearch_url = f'https://{opensearch_host}:{opensearch_port}'

key_path = env.str('KEY_PATH')
encrypt_key = open(key_path, 'rb').read()

logging_path = env.str('LOG_PATH')
