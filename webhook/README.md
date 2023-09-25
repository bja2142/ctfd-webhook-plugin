# ctfd plugin

A simple tool to let you notify a webhook of solve events.

## Configuration:

There is no web-ui-based configuration for this plugin at this time.

To configure this plugin, modify config.json prior to the app start. 

The following values are configurable in config.json:

* *webhook_url* [string]: the path to POST when events occur

* *webhook_secret* [string]: the secret to use for HMAC verification. 

* *report_all_solves* [boolean]: Submit all solves, or only submit those in reported solves.

* *reported_solves* [list<string>]: list of challenge names to submit
to the remote webhook. Only used if *report_all_solves* is false. 

* *point_levels*: A list of dictionaries that are detailed further in the next section. These items define point thresholds that can be 
used to either trigger a webhook or unlock other levels. If the
action is "unlock", it will mark all challenges with the tag given as visible. Because
vanilla CTFd does not support a hidden flag per user, this will
unlock for all users. Alternatiely, if the action is webhook,
it will trigger a post event to the remote webhook given. 

A sample of point_levels is below:

```
 "point_levels" : [
        {"threshold" : 15,
         "actions": [
            {"action" : "unlock", "tag": "level2"},
            {"action" : "webhook", "url" : "http://localhost:8000" }
         ]
        },
        {"threshold" : 80,
         "actions": [
            {"action" : "unlock", "tag": "level3"}
         ]
        }
    ],
```

Note that once a challenge is marked visible, there is no mechanism
to undo the action. If you delete the solve, it won't make the other challenges hidden.

## Webhook Data

A post to the webhook url will take the following format:

`{webhook_url}/?signature={data_hmac_sha256}`

Where the data is the raw json of the post request.

The data has the following fields:

```
{'user': 'user', 'challenge': 'test', 'score': 191, 'before_score': 181}
```


## References:

Special thanks to the ctfd-notifier plugin for providing a useful
reference for hooking challenge solves:

https://github.com/KaindorfCTF/ctfd-notifier/tree/master


## Format:

```
CTFd
└── plugins
   └── CTFd-plugin
       ├── README.md          # README file
       ├── __init__.py        # Main code file loaded by CTFd
       ├── requirements.txt   # Any requirements that need to be installed
       └── config.json        # Plugin configuration file
```

## Read the docs here:

https://docs.ctfd.io/docs/plugins/overview/
