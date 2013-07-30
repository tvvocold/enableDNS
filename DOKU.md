## Intro

The API is self documenting, but for the sake of clenliness, we will be using this document for a more in depth explanation of features and usage.


## Authentication

For the time being, users authenticate to the API using BasicAuthentication. Session authentication also works, but chances are you won't be using it in your API calls. It is however enabled to allow you to browse the API inside your browser more easely.


## API usage

The following examples will demonstrate how to access the API using the cURL command line tool. Most Linux and Mac users will have this binary installed already. If you are on Windows, you may download and install cURL from [HERE](http://curl.haxx.se/download.html).

These examples intended as a generic guide. You may use any library that can make use of the following HTTP verbs: POST,GET,PUT, DELETE.

Some examples include:

* cURL (most languages)
* httplib (python)

The following terms will be used throughout the examples:

* testuser (EnableDNS username)
* secret (testuser password)
* example.com (example domain name)


Please note. The API supports JSON and YAML, but has not yet been tested with YAML. We strongly recommend you go with JSON.

## Read operations

### Fetching domain list

The following API call will fetch a list of testuser added domain names:


```shell
curl -X GET -u 'testuser:secret' -k http://127.0.0.1:8080/api/v1.0/domains.json
```

The API will respond with something similar to:

```json
{

    "results": [
        {
            "url": "http://127.0.0.1:8080/api/v1.0/domains/2.json",
            "shared": false,
            "add_date": "2013-07-26T16:09:01",
            "zone_name": "example.com",
            "id": 2,
            "shared_with": [ ],
            "owned": true,
            "last_update": "2013-07-26T16:47:36"
        }
    ]

}
```

Breakdown of the fields above:

* url: The resource URL. You may use this to directly access this domain
* shared: Indicates if the domain is shared with anyone or not.
* add_date: pretty self explanatory
* zone_name: The name of the zone
* id: resource id
* shared_with: an array of users this zone is shared with
* owned: indicates if this zone belongs to you or not
* last_update: last modification date


### Fetch details about a particular domain

The following API call will display all the records in example.com:

```shell
curl -X GET -u 'testuser:secret' -k "http://127.0.0.1:8080/api/v1.0/domains/2.json"
```

For the sake of keeping this example as simple and clean as possible, i have only included 2 records. The API will respond with something similar to:

```json
[
    {
        "url": "http://127.0.0.1:8080/api/v1.0/domains/2/389.json",
        "retry": 7200, 
        "data": "ns.127.0.0.1:8080.", 
        "refresh": 14400, 
        "id": 389, 
        "host": "@", 
        "minimum": 3600, 
        "expire": 1209600, 
        "ttl": 3600, 
        "serial": 2011090500, 
        "type": "SOA", 
        "resp_person": "office.rohost.com."
    }, 
    {
        "url": "http://127.0.0.1:8080/api/v1.0/domains/2/390.json",
        "type": "A", 
        "host": "@", 
        "data": "192.168.1.1", 
        "id": 390, 
        "ttl": 3600
    }
]
```

Now, a quick note about the results returned by the API. All created records will have a field called 'id' and one called 'url' inside the record block. The 'url' and the 'id' can be used when updating or deleting a record. The rest of the fields are actual record fields and they are all required. For a list of record types and required fields, please refer to section [DNS Record Types](https://github.com/ROHOST/enableDNS/blob/master/RecordTypes.md)


## Create operations

### Adding a new domain

Here's how you can add a domain:

```shell
curl -X POST -u 'testuser:secret' -H "Content-Type:application/json" -d '{ "example.com": [ { "type": "A", "host":"@", "data":"192.168.1.1", "ttl":"3600" } ] }' -k "http://127.0.0.1:8080/api/v1.0/domains.json"
```

Lets break it down a bit and explain what happens:

* -X POST . This is the method used to interact with the API. In a REST API, POST means CREATE.
* -u 'testuser:secret' . These are the credentials used to authenticate to the API
* -H "Content-Type:application/json". Sets a content-type when sending the request to the API
* -d . This option sends the POST data to the API. Post data will contain all the information needed to create the domain and should be a json similar to:

```json
{
  "example.com":
    [ 
      { 
        "type": "A",
        "host":"@",
        "data":"192.168.1.1",
        "ttl":"3600"
      } 
    ]
}
```
You will note that there is no SOA (Start Of Authority) in the JSON. Because EnableDNS will be responsible for your zone, the SOA will be automatically set by the app to a predefined value. You may view the record using GET, but you will not be able to modify or delete it. Sending a SOA record via POST or PUT will not generate an error, however, it will be ignored.

To change the default values of resp_person and data, please set the following variables inside you local_settings.py:

```python
DNS_RESP_PERSON = "support.example.com"
DNS_SOA_DATA = "ns.example.com"
```

Adding multiple domains is also supported:

```json
{
  "example.com":
    [ 
      { 
        "type": "A",
        "host":"@",
        "data":"192.168.1.1",
        "ttl":"3600"
      } 
    ],
    "example2.com":
    [ 
      { 
        "type": "A",
        "host":"@",
        "data":"192.168.1.1",
        "ttl":"3600"
      } 
    ]
}
```

### Adding new records

Adding new records can be done in the same manner in which you add a new domain. You may add multiple records to the same zone. In out last examples when we fetched information about a domain, we mentioned the id and url field. We are going to use this now when updating a zone.

```shell
curl -X POST -u 'testuser:secret' -H "Content-Type:application/json" -d '[ { "type": "A", "host":"mail", "data":"192.168.1.1", "ttl":"3600" }, { "type": "MX", "host":"@", "data":"mail", "priority": 0, "ttl":"3600" } ]' -k "http://127.0.0.1:8080/api/v1.0/domains/2.json"
```

Here is the post data in the above example:

```json
[
  {
    "type": "A",
    "host":"mail",
    "data":"192.168.1.1",
    "ttl":"3600" 
  },
  {
    "type": "MX",
    "host":"@",
    "data":"mail",
    "priority": 0,
    "ttl":"3600"
  }
]
```

The above example will add 2 records:

* An A record (mail.example.com) pointed to 192.168.1.1
* An MX record that points example.com to mail.example.com (the previous A record)

## Update operations

There are very few differences between create (POST) and update (PUT). They work almost the same way, with the only difference that when updating a record you have to specify the record ID inside the record block.

```shell
curl -X PUT -u 'testuser:secret' -H "Content-Type:application/json" -d '[ { "id": 390 , "type": "A", "host":"mail", "data":"192.168.1.1", "ttl":"3600" } ]' -k "http://127.0.0.1:8080/api/v1.0/domains/2.json"
```

* Note the extra 'id' field inside the json
* This will update the record with id 390 in zone example.com

Here is the JSON in the above example:

```json
[
  {
    "id": 390,
    "type": "A",
    "host": "mail",
    "data":"192.168.1.1",
    "ttl":"3600"
  }
]
```

In the case of updates, you may also specify only the information you wish to change. For example, if you only need to update the IP address for hostname mail.example.com, the following is enought:

```json
[
  {
    "id": 390,
    "data": "192.168.1.2"
  }
]
```

## Mixing it up

Now, because there are so few differences between the two methods (POST and PUT) we allow updating and creating of new records using any of those verbs. This is not verry REST-ful but at least this way you can update and create records using one API call. As a result, you can POST or PUT a json with an existing record and a new record. Here is an example of mixing updates with creating new records:

```shell
curl -X PUT -u 'testuser:secret' -H "Content-Type:application/json" -d '[ { "id": 390 , "type": "A", "host":"mail", "data":"192.168.1.1", "ttl":"3600" }, { "type": "A", "host":"ftp", "data":"192.168.1.1", "ttl":"3600" } ]' -k "http://127.0.0.1:8080/api/v1.0/domains/2.json"
```

Here is the JSON in the above example:

```json
[
  {
    "id": 390 ,
    "type": "A",
    "host":"mail",
    "data":"192.168.1.1",
    "ttl":"3600"
  },
  {
    "type": "A",
    "host":"ftp",
    "data":"192.168.1.1",
    "ttl":"3600"
  }
]
```

Two things are happening here:

* The record with id 390 is being updated
* A new A record (ftp.example.com) is being created

## Delete operations

Deleting zones or records is easy. Simply send a DELETE to a record or zone URL and you are done with it. For now at least deleting multiple records/zones is not supported, but stay tuned. We will add this feature shortly.

### Delete one record

The following action will delete record 390 from zone example.com (id 2):

```shell
curl -X DELETE -u 'testuser:secret' "http://127.0.0.1:8080/api/v1.0/domains/2/390.json"
```

## Domain Sharing

Domain sharing is a great way to allow diifferent people acces to one of your domains. For example, lets say that you are the co-owner of a domain and you want to allow your associate acces to the domain. One easy way is to share your domain with him/her.

The users with whom you share your domain with will have read and write access to them, so be careful who you trust. Shared domains however can only be deleted by the owner of the domain.


### Add share for a domain

To share a domain with one or more users you just need to POST an array of usernames to the API:

```shell
curl -X POST -u 'testuser:secret' -d '["example", "example2"]' -H 'Content-type: application/json' -k http://127.0.0.1:8080/api/v1.0/shares/2.json -D - && echo
```

You may add as many users as you like in the array you post.

Here is the JSON in the above example

```json
[
    "example",
    "example2"
]
```

### Read shared domains

To list all domains that have been shared with other users you may use the following api call

```shell
curl -X GET -u 'testuser:secret' -k http://127.0.0.1:8080/api/v1.0/shares.json -D - && echo

```

### Remove share from domain

When removing users you can use the ID of the share itself, or the username of the user you wish to remove.

Removing a single user:

```shell
curl -X DELETE -u 'testuser:secret' -k http://127.0.0.1:8080/api/v1.0/shares/2/81.json -D - && echo
```
Removing multiple users by ID. Note that this is not the user id, its the share ID.

```shell
curl -X DELETE -u 'testuser:secret' -k http://127.0.0.1:8080/api/v1.0/shares/2.json?ids=81,82,93 -D - && echo
```

Removing multiple users by username

```shell
curl -X DELETE -u 'testuser:secret' -k http://127.0.0.1:8080/api/v1.0/shares/2.json?users=example,example2 -D - && echo
```