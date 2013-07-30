## Background

First there are a few things you should know before we dive into it. You are probably familiar with editing a DNS zone, but if you are not, don't panic, this guide should be easy to follow.

A DNS zone is made up of several DNS records. Each zone is defined in most servers as a file or as a database entry. In a traditional Bind9 config, a zone is defined in named.conf and is pointed to a zone file. That zone file will contain all the DNS records for that zone.

EnableDNS uses MySQL as a backend for Bind. As a result, there are some aspects that you need to be aware when editing or creating a zone entry. I'm going to start with an example of a traditional Bind9 setup and explain the differences you need to take into account. Bellow is an example of an entry in a traditional zone file.

```shell
example.com. 3600 IN A 192.168.1.1
```

Lets take a closer look at the example above. Starting from left to right, we have:

* Host field (example.com). This field defines the host for which you are defining the DNS entry. Please note the DOT at the end, we're going to come back to it later.
* TTL field (3600). This is the Time To Live field. This instructs caching DNS servers how long they are suposed to cache the entry before asking again
* Record type field (IN A). This tells the DNS server that you want an A record.
* Data field (192.168.1.1). This is the actual value to which the record points to.

Now, I mentioned above that you should note the DOT at the end. The dot is very important because it tels BIND if the entry is a relative or an absolute one. The difference between relative entries and absolute entries is that relative entries have the zone names appended to them, while absolute entries do not. For example, if you were to define th above example as:

```shell
example.com 3600 IN A 192.168.1.1 # NOTE that the dot is missing
```

BIND would automatically append the zone name, thus becoming:

```shell
example.com.example.com. 3600 IN A 192.168.1.1
```

I know it may be a bit confusing, but fortunately, there is a way to avoid all the madness! DNS records can also be defined like this:

```shell
@ 3600 IN A 192.168.1.1
```

In this scenario the character @ is sinonimous to example.com. Because of the way BIND works with a database backend, this is the only format that we support. That means that each time you wish to define a record for the curent zone, you will need to use @.

"But how do i define subdomains" you ask? Simple. Just use relative names. Its much shorter and cleaner, and it works with all database servers. Bellow is an example of a DNS record for a subdomain name.

```shell
www 3600 IN A 192.168.1.1
```

This will define a new A record www.example.com pointing to 192.168.1.1. Note, that this is mandatory only for the Host field. The data field does not have this limitation. For example, you may define a record such as:

```shell
www 3600 IN CNAME example.com.
```

Now that that's out of the way, lets move on.

## DNS record types

### A records

key  | value
---  | ---
type | A
host | @
data | 192.168.1.1
ttl  | 3600

### AAAA (IPv6) records

key  | value
---  | ---
type | AAAA
host | @
data | ::1
ttl  | 3600

### MX records

key  | value
-------- | ---
type     | MX
host     | @
data     | ::1
priority | 0
ttl      | 3600

### PTR records

key  | value
---  | ---
type | PTR
host | 1
data | enabledns.com
ttl  | 3600

### TXT records

You should always enclose your TXT records in double quotes

key  | value
---  | ---
type | TXT
host | @
data | "v=spf1 ?all"
ttl  | 3600

### CNAME records

key  | value
---  | ---
type | CNAME
host | mail
data | @
ttl  | 3600

### NS records

key  | value
---  | ---
type | NS
host | @
data | ns.enabledns.com.
ttl  | 3600

### SRV records

For SRV records, the priority, weight, port and target all go in the "data" field.

key  | value
---  | ---
type | SRV
host | _service._proto.name
data | priority weight port target
ttl  | 3600