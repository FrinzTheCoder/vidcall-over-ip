# For Documentation Only

## Basic
{
    'type':'...'
    'content':'...'
}

## Connection
### Request
{
    'type':'CONNECTION_REQUEST'
    'content':'19122' // PIN
}
### Response (Positive)
{
    'type':'CONNECTION_RESPONSE'
    'content':'ACCEPTED'
}

### Response (Negative)
{
    'type':'CONNECTION_RESPONSE'
    'content':'REJECTED'
}

### Connection Source Request
{
    'type':'CONNECTION_SOURCE_REQUEST'
    'content':'Python' // 'Python' or 'Flutter'
}

### Connection Source Response (Positive)
{
    'type':'CONNECTION_SOURCE_RESPONSE'
    'content':'VALID'
}

### Connection Source Response (Negative)
{
    'type':'CONNECTION_SOURCE_RESPONSE'
    'content':'INVALID'
}

## General
### IP Address Info
{
    'type':'IP_ADDR_INFO_REQUEST'
    'content':''
}

### IP Address Response
{
    'type':'IP_ADDR_INFO_RESPONSE'
    'content':['192.168.0.2','192.168.0.3] // LIST OF IP ADDRESS TO SUBSCRIBE
}

## Publishing
### Publish Request
{
    'type':'PUBLISH_REQUEST'
    'content':''
}

### Publish Response
{
    'type':'PUBLISH_RESPONSE'
    'content':'ACCEPTED'
}

## Sending Data
### Send Data
{
    'type':'SEND_DATA'
    'content':'...' // IMAGE DATA TO SERVER
}

### Send Data Response
{
    'type':'SEND_DATA_RESPONSE'
    'content':'RECEIVED'
}

## Requesting Data
### Request Data
{
    'type':'REQUEST_DATA'
    'content':'192.168.0.2' // IP ADDRESS OF REQUESTED DATA
}

### Requesting Data Response
{
    'type':'REQUEST_DATA_RESPONSE'
    'content':'...' // IMAGE DATA TO SERVER
}
