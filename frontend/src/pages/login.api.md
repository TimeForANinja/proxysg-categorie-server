# Routes
`GET` at `/`:
a basic home route with some info about the API

`POST` at `/auth`:
an endpoint that will create and log in users and issue JSON web tokens

`POST` at `/verify`:
an endpoint that will help verify JSON web tokens to see if they are valid

`POST` at `/check-account`:
an endpoint that will check if a given email address has an associated entry in the auth database
