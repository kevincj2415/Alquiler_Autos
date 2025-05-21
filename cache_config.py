from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'simple',  # Para desarrollo. En producción usar 'redis'
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutos
})

def init_cache(app):
    cache.init_app(app)
    return cache
