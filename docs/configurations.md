## Настройки БД

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=knowledge
DB_USERNAME=
DB_PASSWORD=
```

# Настройки Yandex Search API

```env
YANDEX_API_KEY=
YANDEX_FOLDER_ID=
YANDEX_API_URL=https://searchapi.api.cloud.yandex.net/v2/gen/search
```

# Настройки graphana

```env
GF_ADMIN_USER=admin
GF_ADMIN_PASSWORD=
```

# Настройки LLM

* LLM_MODEL - основная модель, которая используется для работы.
* EMBEDDING_MODEL - модель для векторизации текста.

```env
LLM_APIKEY=
LLM_MODEL=
EMBEDDING_MODEL=text-embedding-3-small
LLM_URL=https://api.aitunnel.ru/v1/
```

# Настройки семантического поиска

```env
MAX_COSINE_DISTANCE=0.25
```

# Настройки журналирования

```env
LOG_PATH=app.log
```