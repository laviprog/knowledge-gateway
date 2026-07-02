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
| src/rag\_service/auth/\_\_init\_\_.py                   |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/auth/cookies.py                        |        7 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/auth/dependencies.py                   |       10 |        2 |        0 |        0 |     80% |     12-13 |
| src/rag\_service/auth/routes.py                         |       25 |        0 |        2 |        1 |     96% |   53-\>55 |
| src/rag\_service/auth/schema.py                         |        8 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/auth/services.py                       |       12 |        0 |        2 |        0 |    100% |           |
| src/rag\_service/auth/session\_store.py                 |       38 |        6 |        6 |        1 |     84% |53-55, 63, 68-69 |
| src/rag\_service/bootstrap.py                           |       25 |       16 |        6 |        0 |     29% |12-34, 47-51 |
| src/rag\_service/chats/\_\_init\_\_.py                  |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/chats/dependencies.py                  |        9 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/chats/models.py                        |       34 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/chats/orchestrator.py                  |       67 |        8 |        4 |        1 |     87% |118, 139-146, 167-174, 185 |
| src/rag\_service/chats/prompts.py                       |       38 |        5 |       16 |        5 |     81% |67, 75, 79, 84, 87 |
| src/rag\_service/chats/repositories.py                  |        4 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/chats/routes.py                        |       43 |       13 |        8 |        1 |     61% |69-97, 124-134, 178 |
| src/rag\_service/chats/schema.py                        |       40 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/chats/services.py                      |      242 |       90 |       64 |        9 |     60% |178-181, 215, 269, 281-288, 309, 318-325, 336-\>343, 463-\>465, 465-\>469, 469-\>473, 473-\>exit, 499-509, 520-521, 533-538, 552-562, 573-578, 595-617, 632-673, 710-723, 730-738, 745-750, 765-769, 776, 783 |
| src/rag\_service/chats/sse.py                           |       10 |        0 |        2 |        0 |    100% |           |
| src/rag\_service/config.py                              |       34 |        1 |        0 |        0 |     97% |        76 |
| src/rag\_service/database/\_\_init\_\_.py               |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/database/base\_model.py                |        5 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/database/config.py                     |        4 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/database/metadata.py                   |        8 |        8 |        0 |        0 |      0% |       1-8 |
| src/rag\_service/database/mixins/\_\_init\_\_.py        |        2 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/database/mixins/soft\_delete\_mixin.py |       10 |        1 |        0 |        0 |     90% |        21 |
| src/rag\_service/documents/\_\_init\_\_.py              |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/documents/dependencies.py              |        9 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/documents/extractors.py                |       31 |        3 |        8 |        1 |     90% | 56-57, 61 |
| src/rag\_service/documents/models.py                    |       36 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/documents/repositories.py              |        6 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/documents/routes.py                    |       40 |       15 |        0 |        0 |     62% |48-52, 77-78, 101-109, 130-136, 172-181, 202 |
| src/rag\_service/documents/schema.py                    |       18 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/documents/services.py                  |      152 |       36 |       22 |        4 |     75% |64-65, 71-76, 89-116, 153, 215-227, 302-323, 341, 352-\>354, 381, 389-394 |
| src/rag\_service/documents/tasks.py                     |       12 |        6 |        0 |        0 |     50% |     14-19 |
| src/rag\_service/documents/utils.py                     |       54 |        7 |       22 |        3 |     84% |25, 57-61, 70-\>73, 80 |
| src/rag\_service/embedding\_models/\_\_init\_\_.py      |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/embedding\_models/dependencies.py      |        9 |        2 |        0 |        0 |     78% |     11-12 |
| src/rag\_service/embedding\_models/models.py            |       14 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/embedding\_models/repositories.py      |        4 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/embedding\_models/routes.py            |       28 |        9 |        0 |        0 |     68% |44-48, 73-74, 96-104, 127-135, 156 |
| src/rag\_service/embedding\_models/schema.py            |       18 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/embedding\_models/services.py          |       56 |       15 |       20 |        0 |     67% |34-39, 92-110 |
| src/rag\_service/enums.py                               |        5 |        1 |        0 |        0 |     80% |        12 |
| src/rag\_service/exceptions/\_\_init\_\_.py             |        3 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/exceptions/domain.py                   |       27 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/exceptions/handlers.py                 |       24 |        4 |        0 |        0 |     83% |38-46, 76-83 |
| src/rag\_service/exceptions/responses.py                |       11 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/exceptions/schema.py                   |        4 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/knowledge\_bases/\_\_init\_\_.py       |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/knowledge\_bases/dependencies.py       |        9 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/knowledge\_bases/models.py             |       11 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/knowledge\_bases/repositories.py       |        4 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/knowledge\_bases/routes.py             |       31 |       11 |        0 |        0 |     65% |45-49, 74-75, 98-104, 127-133, 157-159 |
| src/rag\_service/knowledge\_bases/schema.py             |       14 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/knowledge\_bases/services.py           |       56 |       23 |       14 |        0 |     53% |28-33, 71-83, 89-91, 97-102, 108, 117-122 |
| src/rag\_service/lifecycle.py                           |       18 |        8 |        0 |        0 |     56% |     16-24 |
| src/rag\_service/llm/\_\_init\_\_.py                    |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/llm/base.py                            |        7 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/llm/chat.py                            |       46 |        6 |       14 |        1 |     85% | 41, 91-95 |
| src/rag\_service/llm/client.py                          |       15 |        0 |        4 |        0 |    100% |           |
| src/rag\_service/llm/embeddings.py                      |       16 |        0 |        2 |        0 |    100% |           |
| src/rag\_service/llm\_models/\_\_init\_\_.py            |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/llm\_models/dependencies.py            |        9 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/llm\_models/models.py                  |       13 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/llm\_models/repositories.py            |        4 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/llm\_models/routes.py                  |       33 |       11 |        0 |        0 |     67% |47-51, 76-77, 99-108, 131-141, 162, 180-181 |
| src/rag\_service/llm\_models/schema.py                  |       26 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/llm\_models/services.py                |       53 |       20 |       20 |        3 |     52% |20-21, 27-32, 79-99, 121, 133 |
| src/rag\_service/log\_config.py                         |       44 |        3 |        2 |        1 |     91% |42, 110, 135 |
| src/rag\_service/main.py                                |       16 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/metrics.py                             |        8 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/middlewares.py                         |       32 |        3 |        6 |        1 |     89% |47-53, 59-\>63 |
| src/rag\_service/pagination.py                          |        9 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/providers/\_\_init\_\_.py              |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/providers/config.py                    |        6 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/providers/dependencies.py              |        9 |        2 |        0 |        0 |     78% |     11-12 |
| src/rag\_service/providers/models.py                    |       12 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/providers/repositories.py              |        4 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/providers/routes.py                    |       28 |        9 |        0 |        0 |     68% |42-46, 71-72, 94-102, 125-134, 155 |
| src/rag\_service/providers/schema.py                    |       24 |        1 |        0 |        0 |     96% |        46 |
| src/rag\_service/providers/services.py                  |       43 |       17 |       16 |        0 |     51% |20-25, 65-86 |
| src/rag\_service/qdrant/\_\_init\_\_.py                 |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/qdrant/client.py                       |       12 |        1 |        4 |        2 |     81% |13-\>19, 28 |
| src/rag\_service/qdrant/schema.py                       |        3 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/qdrant/vector\_store.py                |       54 |       22 |       14 |        1 |     54% |93-130, 136-145, 169-205 |
| src/rag\_service/redis/\_\_init\_\_.py                  |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/redis/client.py                        |       13 |        7 |        4 |        0 |     35% |10-12, 16, 21-23 |
| src/rag\_service/redis/rate\_limiter.py                 |       20 |        0 |        2 |        0 |    100% |           |
| src/rag\_service/routes.py                              |       38 |        4 |        0 |        0 |     89% |33, 41, 52-53 |
| src/rag\_service/schema.py                              |       10 |        1 |        0 |        0 |     90% |        14 |
| src/rag\_service/security/\_\_init\_\_.py               |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/security/api\_keys.py                  |       18 |        9 |        0 |        0 |     50% |18-21, 28, 39, 46-48 |
| src/rag\_service/security/dependencies.py               |       61 |        2 |       18 |        2 |     95% |    76, 95 |
| src/rag\_service/security/encryption.py                 |       31 |        6 |        8 |        0 |     74% |67-69, 72-74 |
| src/rag\_service/security/passwords.py                  |       10 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/users/\_\_init\_\_.py                  |        0 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/users/dependencies.py                  |        9 |        2 |        0 |        0 |     78% |     11-12 |
| src/rag\_service/users/models.py                        |       16 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/users/repositories.py                  |        4 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/users/routes.py                        |       37 |       11 |        0 |        0 |     70% |67-68, 89-94, 117-124, 146, 169-174, 198-203 |
| src/rag\_service/users/schema.py                        |       16 |        0 |        0 |        0 |    100% |           |
| src/rag\_service/users/services.py                      |       65 |       42 |       14 |        0 |     29% |20-21, 27-32, 43, 61-79, 92-106, 112-120, 131-141, 152-153, 159-164, 170, 179, 188-189 |
| src/rag\_service/utils.py                               |       11 |        0 |        0 |        0 |    100% |           |
| **TOTAL**                                               | **2379** |  **509** |  **346** |   **38** | **75%** |           |


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