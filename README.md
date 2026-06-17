# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/laviprog/knowledge-gateway/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                    |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|-------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| src/rag\_service/\_\_init\_\_.py                        |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/api\_keys/\_\_init\_\_.py              |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/api\_keys/dependencies.py              |        9 |        2 |        0 |        0 |     78% |     12-13 |
| src/rag\_service/api\_keys/models.py                    |       14 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/api\_keys/repositories.py              |        8 |        2 |        0 |        0 |     75% |     16-17 |
| src/rag\_service/api\_keys/routes.py                    |       12 |        2 |        0 |        0 |     83% |     35-38 |
| src/rag\_service/api\_keys/schema.py                    |       21 |        1 |        6 |        1 |     93% |        18 |
| src/rag\_service/api\_keys/services.py                  |       51 |       33 |       16 |        0 |     27% |25, 35-57, 68-74, 80-105, 115-124, 130-142 |
| src/rag\_service/bootstrap.py                           |       16 |       10 |        4 |        0 |     30% |     10-30 |
| src/rag\_service/chats/\_\_init\_\_.py                  |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/chats/dependencies.py                  |        9 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/chats/models.py                        |       34 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/chats/prompts.py                       |       38 |        5 |       16 |        5 |     81% |67, 75, 79, 84, 87 |
| src/rag\_service/chats/repositories.py                  |        4 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/chats/routes.py                        |       65 |       39 |        6 |        1 |     38% |67-179, 206-216 |
| src/rag\_service/chats/schema.py                        |       37 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/chats/services.py                      |      191 |       72 |       52 |        4 |     60% |178, 232, 244-251, 272, 281-288, 299-\>306, 428-438, 449-450, 462-467, 481-491, 502-507, 524-551, 558-566, 573-578, 585-589 |
| src/rag\_service/chats/sse.py                           |       10 |        0 |        2 |        0 |    100% |           |
| src/rag\_service/config.py                              |       33 |        1 |        0 |        0 |     97% |        70 |
| src/rag\_service/database/\_\_init\_\_.py               |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/database/base\_model.py                |        5 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/database/config.py                     |        4 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/database/metadata.py                   |        5 |        5 |        0 |        0 |      0% |       1-5 |
| src/rag\_service/database/mixins/\_\_init\_\_.py        |        2 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/database/mixins/soft\_delete\_mixin.py |       10 |        1 |        0 |        0 |     90% |        21 |
| src/rag\_service/documents/\_\_init\_\_.py              |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/documents/dependencies.py              |        9 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/documents/extractors.py                |       31 |        3 |        8 |        1 |     90% | 56-57, 61 |
| src/rag\_service/documents/models.py                    |       34 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/documents/repositories.py              |        6 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/documents/routes.py                    |       38 |       14 |        0 |        0 |     63% |47-51, 76-77, 99-106, 126-130, 164-172, 193 |
| src/rag\_service/documents/schema.py                    |       18 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/documents/services.py                  |       98 |       25 |       10 |        2 |     73% |56-61, 73-88, 121, 151-156, 199-217, 229 |
| src/rag\_service/documents/tasks.py                     |       11 |        5 |        0 |        0 |     55% |     14-18 |
| src/rag\_service/documents/utils.py                     |       54 |        7 |       22 |        3 |     84% |25, 57-61, 70-\>73, 80 |
| src/rag\_service/enums.py                               |        5 |        1 |        0 |        0 |     80% |        12 |
| src/rag\_service/exceptions/\_\_init\_\_.py             |        3 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/exceptions/domain.py                   |       27 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/exceptions/handlers.py                 |       24 |        4 |        0 |        0 |     83% |38-46, 76-83 |
| src/rag\_service/exceptions/responses.py                |       11 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/exceptions/schema.py                   |        4 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/lifecycle.py                           |       18 |        8 |        0 |        0 |     56% |     16-24 |
| src/rag\_service/llm\_models/\_\_init\_\_.py            |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/llm\_models/dependencies.py            |        9 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/llm\_models/models.py                  |       11 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/llm\_models/repositories.py            |        4 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/llm\_models/routes.py                  |       33 |       11 |        0 |        0 |     67% |47-51, 76-77, 99-107, 130-139, 160, 178-179 |
| src/rag\_service/llm\_models/schema.py                  |       25 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/llm\_models/services.py                |       51 |       18 |       18 |        3 |     55% |20-21, 27-32, 76-93, 115, 127 |
| src/rag\_service/log\_config.py                         |       44 |        3 |        2 |        1 |     91% |42, 110, 135 |
| src/rag\_service/main.py                                |       14 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/middlewares.py                         |       29 |        3 |        4 |        1 |     88% |41-47, 53-\>57 |
| src/rag\_service/ollama/\_\_init\_\_.py                 |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/ollama/chat.py                         |       26 |       14 |        8 |        0 |     35% | 36, 50-79 |
| src/rag\_service/ollama/client.py                       |       16 |        1 |        6 |        3 |     82% |14-\>24, 16-\>19, 33 |
| src/rag\_service/ollama/embeddings.py                   |       11 |        4 |        2 |        0 |     54% |     18-26 |
| src/rag\_service/pagination.py                          |        9 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/qdrant/\_\_init\_\_.py                 |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/qdrant/client.py                       |       12 |        1 |        4 |        2 |     81% |13-\>19, 28 |
| src/rag\_service/qdrant/schema.py                       |        3 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/qdrant/vector\_store.py                |       40 |       23 |       12 |        1 |     35% |27-31, 47-77, 83-87, 105-126 |
| src/rag\_service/redis/\_\_init\_\_.py                  |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/redis/client.py                        |       13 |        7 |        4 |        0 |     35% |10-12, 16, 21-23 |
| src/rag\_service/redis/rate\_limiter.py                 |       20 |        0 |        2 |        0 |    100% |           |
| src/rag\_service/routes.py                              |       30 |        4 |        0 |        0 |     87% |29, 37, 48-49 |
| src/rag\_service/schema.py                              |       10 |        1 |        0 |        0 |     90% |        14 |
| src/rag\_service/security/\_\_init\_\_.py               |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/security/api\_keys.py                  |       18 |        9 |        0 |        0 |     50% |18-21, 28, 39, 46-48 |
| src/rag\_service/security/dependencies.py               |       30 |        0 |        6 |        0 |    100% |           |
| src/rag\_service/users/\_\_init\_\_.py                  |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/users/dependencies.py                  |        9 |        2 |        0 |        0 |     78% |     11-12 |
| src/rag\_service/users/models.py                        |       15 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/users/repositories.py                  |        4 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/users/routes.py                        |       37 |       11 |        0 |        0 |     70% |67-68, 89-94, 117-124, 146, 169-174, 198-203 |
| src/rag\_service/users/schema.py                        |       16 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/users/services.py                      |       58 |       38 |       14 |        0 |     28% |20-21, 27-32, 43, 61-79, 92-106, 112-120, 131-141, 152-153, 159-167 |
| src/rag\_service/utils.py                               |       11 |        0 |        0 |        0 |    100% |           |
| **TOTAL**                                               | **1577** |  **390** |  **224** |   **28** | **71%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/laviprog/knowledge-gateway/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/laviprog/knowledge-gateway/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/laviprog/knowledge-gateway/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/laviprog/knowledge-gateway/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Flaviprog%2Fknowledge-gateway%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/laviprog/knowledge-gateway/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.