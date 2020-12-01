# API

## HTTP API Calls
### GET /get_keywords
Query list of keywords
- No parameters
- Example:
  - Query: GET /get_keywords
  - Response: ```{"keywords":["Australia", "Melbourne"]}```

### GET /get_news?text=\<text\>&keywords=\<keyword1>&limit=\<limit\>
Query news by text and/ or keywords
- Parameters:
  | Parameter | Description | Type | Required |
  |--|--|--|--|
  | text | Search for text occurrence in article. | string | no |
  | keywords | Search for articles with tags of all the keywords. | string, multiple | no |
  | limit | limit the number articles returned, a limit of 100 is applied if not specified. | int | no |

- Example:
  - Query: GET /get_news?keywords=iPhone&keywords=Android
  - Response: ```{"news":[{"article":"A ticket app which it is claimed will \"revolutionise\" the Tyne and Wear Metro has been released but is unavailable to iPhone users, the operator has said. ...","keywords":["iPhones","Apple","Newcastle upon Tyne","Android"],"publication_date":"Wed, 25 Nov 2020 18:29:25 GMT","score":0.0,"title":"New Metro ticket app cannot be used on iPhones","url":"https://www.bbc.com/news/uk-england-tyne-55072188"}]}```

## Server Response Codes
Standard HTTP response codes are used:
| Code | Description |
|--|--|
| 200 | The request was successfully processed. |
| 400 | The request could not be understood, or bad parameters were provided. |
| 500 | The server encountered an error when processing the request. |
