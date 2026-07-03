# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/laviprog/knowledge-gateway/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                          |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|-------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| src/knowledge\_gateway/\_\_init\_\_.py                        |        0 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/api\_keys/\_\_init\_\_.py              |        0 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/api\_keys/dependencies.py              |        9 |        2 |        0 |        0 |     78% |     12-13 |
| src/knowledge\_gateway/api\_keys/models.py                    |       14 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/api\_keys/repositories.py              |        8 |        2 |        0 |        0 |     75% |     16-17 |
| src/knowledge\_gateway/api\_keys/routes.py                    |       12 |        2 |        0 |        0 |     83% |     35-38 |
| src/knowledge\_gateway/api\_keys/schema.py                    |       21 |        1 |        6 |        1 |     93% |        18 |
| src/knowledge\_gateway/api\_keys/services.py                  |       51 |       33 |       16 |        0 |     27% |25, 35-57, 68-74, 80-105, 115-124, 130-142 |
| src/knowledge\_gateway/auth/\_\_init\_\_.py                   |        0 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/auth/cookies.py                        |        7 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/auth/dependencies.py                   |       10 |        2 |        0 |        0 |     80% |     12-13 |
| src/knowledge\_gateway/auth/routes.py                         |       25 |        0 |        2 |        1 |     96% |   53-\>55 |
| src/knowledge\_gateway/auth/schema.py                         |        8 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/auth/services.py                       |       12 |        0 |        2 |        0 |    100% |           |
| src/knowledge\_gateway/auth/session\_store.py                 |       38 |        6 |        6 |        1 |     84% |53-55, 63, 68-69 |
| src/knowledge\_gateway/bootstrap.py                           |       25 |       16 |        6 |        0 |     29% |12-34, 47-51 |
| src/knowledge\_gateway/chats/\_\_init\_\_.py                  |        0 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/chats/dependencies.py                  |        9 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/chats/models.py                        |       40 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/chats/orchestrator.py                  |       67 |        8 |        4 |        1 |     87% |118, 139-146, 167-174, 185 |
| src/knowledge\_gateway/chats/prompts.py                       |       43 |        4 |       18 |        4 |     87% |87, 91, 96, 99 |
| src/knowledge\_gateway/chats/repositories.py                  |        4 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/chats/routes.py                        |       43 |       13 |        8 |        1 |     61% |69-97, 125-136, 182 |
| src/knowledge\_gateway/chats/schema.py                        |       42 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/chats/services.py                      |      258 |      106 |       74 |        9 |     55% |181-197, 231, 285, 297-304, 325, 334-341, 352-\>359, 479-\>481, 481-\>485, 485-\>489, 489-\>exit, 515-525, 536-537, 549-554, 568-578, 589-594, 612-635, 651-707, 754-769, 776-790, 799-804, 819-823, 830, 837 |
| src/knowledge\_gateway/chats/sse.py                           |       10 |        0 |        2 |        0 |    100% |           |
| src/knowledge\_gateway/config.py                              |       36 |        1 |        0 |        0 |     97% |        87 |
| src/knowledge\_gateway/database/\_\_init\_\_.py               |        0 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/database/base\_model.py                |        5 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/database/config.py                     |        4 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/database/metadata.py                   |        8 |        8 |        0 |        0 |      0% |       1-8 |
| src/knowledge\_gateway/database/mixins/\_\_init\_\_.py        |        2 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/database/mixins/soft\_delete\_mixin.py |       10 |        1 |        0 |        0 |     90% |        21 |
| src/knowledge\_gateway/documents/\_\_init\_\_.py              |        0 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/documents/dependencies.py              |        9 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/documents/extractors.py                |       31 |        3 |        8 |        1 |     90% | 56-57, 61 |
| src/knowledge\_gateway/documents/models.py                    |       36 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/documents/repositories.py              |        6 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/documents/routes.py                    |       40 |       15 |        0 |        0 |     62% |49-54, 79-80, 103-111, 132-138, 174-183, 204 |
| src/knowledge\_gateway/documents/schema.py                    |       18 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/documents/services.py                  |      156 |       39 |       24 |        4 |     73% |68-69, 81-90, 103-130, 167, 229-241, 325-346, 364, 375-\>377, 404, 412-417 |
| src/knowledge\_gateway/documents/tasks.py                     |       12 |        6 |        0 |        0 |     50% |     14-19 |
| src/knowledge\_gateway/documents/utils.py                     |       54 |        7 |       22 |        3 |     84% |25, 57-61, 70-\>73, 80 |
| src/knowledge\_gateway/embedding\_models/\_\_init\_\_.py      |        0 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/embedding\_models/dependencies.py      |        9 |        2 |        0 |        0 |     78% |     11-12 |
| src/knowledge\_gateway/embedding\_models/models.py            |       14 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/embedding\_models/repositories.py      |        4 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/embedding\_models/routes.py            |       28 |        9 |        0 |        0 |     68% |44-48, 73-74, 96-104, 127-135, 157 |
| src/knowledge\_gateway/embedding\_models/schema.py            |       18 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/embedding\_models/services.py          |       66 |       17 |       22 |        0 |     69% |33-34, 40-45, 98-116 |
| src/knowledge\_gateway/enums.py                               |        5 |        1 |        0 |        0 |     80% |        12 |
| src/knowledge\_gateway/exceptions/\_\_init\_\_.py             |        3 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/exceptions/domain.py                   |       27 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/exceptions/handlers.py                 |       24 |        4 |        0 |        0 |     83% |38-46, 76-83 |
| src/knowledge\_gateway/exceptions/responses.py                |       11 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/exceptions/schema.py                   |        4 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/knowledge\_bases/\_\_init\_\_.py       |        0 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/knowledge\_bases/dependencies.py       |        9 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/knowledge\_bases/models.py             |       16 |        1 |        0 |        0 |     94% |        41 |
| src/knowledge\_gateway/knowledge\_bases/repositories.py       |        4 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/knowledge\_bases/routes.py             |       33 |       13 |        0 |        0 |     61% |45-50, 77-79, 102-110, 133-141, 165-167 |
| src/knowledge\_gateway/knowledge\_bases/schema.py             |       36 |        5 |        2 |        0 |     82% |     66-75 |
| src/knowledge\_gateway/knowledge\_bases/services.py           |       79 |       23 |       22 |        3 |     68% |42-47, 57-80, 127-128, 134, 148-150, 159, 176-181 |
| src/knowledge\_gateway/lifecycle.py                           |       18 |        8 |        0 |        0 |     56% |     16-24 |
| src/knowledge\_gateway/llm/\_\_init\_\_.py                    |        0 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/llm/base.py                            |        7 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/llm/chat.py                            |       46 |        6 |       14 |        1 |     85% | 41, 91-95 |
| src/knowledge\_gateway/llm/client.py                          |       15 |        0 |        4 |        0 |    100% |           |
| src/knowledge\_gateway/llm/embeddings.py                      |       16 |        0 |        2 |        0 |    100% |           |
| src/knowledge\_gateway/llm\_models/\_\_init\_\_.py            |        0 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/llm\_models/dependencies.py            |        9 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/llm\_models/models.py                  |       13 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/llm\_models/repositories.py            |        4 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/llm\_models/routes.py                  |       33 |       11 |        0 |        0 |     67% |47-51, 76-77, 99-108, 131-141, 162, 180-181 |
| src/knowledge\_gateway/llm\_models/schema.py                  |       26 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/llm\_models/services.py                |       53 |       20 |       20 |        3 |     52% |20-21, 27-32, 79-99, 121, 133 |
| src/knowledge\_gateway/log\_config.py                         |       44 |        3 |        2 |        1 |     91% |42, 110, 135 |
| src/knowledge\_gateway/main.py                                |       16 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/metrics.py                             |        8 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/middlewares.py                         |       32 |        3 |        6 |        1 |     89% |47-53, 59-\>63 |
| src/knowledge\_gateway/pagination.py                          |        9 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/providers/\_\_init\_\_.py              |        0 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/providers/config.py                    |        6 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/providers/dependencies.py              |        9 |        2 |        0 |        0 |     78% |     11-12 |
| src/knowledge\_gateway/providers/models.py                    |       12 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/providers/repositories.py              |        4 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/providers/routes.py                    |       28 |        9 |        0 |        0 |     68% |42-46, 71-72, 94-102, 125-134, 155 |
| src/knowledge\_gateway/providers/schema.py                    |       24 |        1 |        0 |        0 |     96% |        46 |
| src/knowledge\_gateway/providers/services.py                  |       43 |       17 |       16 |        0 |     51% |20-25, 65-86 |
| src/knowledge\_gateway/qdrant/\_\_init\_\_.py                 |        0 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/qdrant/client.py                       |       12 |        1 |        4 |        2 |     81% |13-\>19, 28 |
| src/knowledge\_gateway/qdrant/schema.py                       |        3 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/qdrant/vector\_store.py                |       54 |       15 |       14 |        0 |     69% |93-130, 136-145 |
| src/knowledge\_gateway/redis/\_\_init\_\_.py                  |        0 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/redis/client.py                        |       13 |        7 |        4 |        0 |     35% |10-12, 16, 21-23 |
| src/knowledge\_gateway/redis/rate\_limiter.py                 |       20 |        0 |        2 |        0 |    100% |           |
| src/knowledge\_gateway/routes.py                              |       38 |        4 |        0 |        0 |     89% |33, 41, 52-53 |
| src/knowledge\_gateway/schema.py                              |       10 |        1 |        0 |        0 |     90% |        14 |
| src/knowledge\_gateway/security/\_\_init\_\_.py               |        0 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/security/api\_keys.py                  |       18 |        9 |        0 |        0 |     50% |18-21, 28, 39, 46-48 |
| src/knowledge\_gateway/security/dependencies.py               |       61 |        2 |       18 |        2 |     95% |    76, 95 |
| src/knowledge\_gateway/security/encryption.py                 |       31 |        6 |        8 |        0 |     74% |67-69, 72-74 |
| src/knowledge\_gateway/security/passwords.py                  |       10 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/users/\_\_init\_\_.py                  |        0 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/users/dependencies.py                  |        9 |        2 |        0 |        0 |     78% |     11-12 |
| src/knowledge\_gateway/users/models.py                        |       16 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/users/repositories.py                  |        4 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/users/routes.py                        |       37 |       11 |        0 |        0 |     70% |67-68, 89-94, 117-124, 146, 169-174, 198-203 |
| src/knowledge\_gateway/users/schema.py                        |       16 |        0 |        0 |        0 |    100% |           |
| src/knowledge\_gateway/users/services.py                      |       65 |       42 |       14 |        0 |     29% |20-21, 27-32, 43, 61-79, 92-106, 112-120, 131-141, 152-153, 159-164, 170, 179, 188-189 |
| src/knowledge\_gateway/utils.py                               |       11 |        0 |        0 |        0 |    100% |           |
| **TOTAL**                                                     | **2476** |  **530** |  **372** |   **39** | **75%** |           |


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