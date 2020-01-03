# Setup of postgresql

### Local Installation

##### Requirements

* Postgres App

##### Installing postgres

Download postgres from `https://postgresapp.com/` and install it to your machine.
Click `start` in order to start the server which runs on port 5432.
You will access your user on the terminal.
Create the database using `create database jarvis`


### Setting up postgres configurations in .env

```
DATABASE_URL=postgresql://<postgres_username>:<postgres_password>@<host>:<port>/<db_name>
```
#### Remember to remove the greater than and less than symbols

`postgresql` represents the type of database you are using which is postgresql
`postgres_username` represents your postgresql User name
`postgres_password` represents your postgresql User password
`host` represents your postgresql host
`port` represents your postgresql server port
`db_name` represents your postgesql database name