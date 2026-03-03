# CSD-325
Visit the website for presentation while its not on AWS:
[[src\pages\index.html]]

# API Gateways
The frontend gathers user input and uses scripts.js to pass it to the authenticate API gateway through various routes.
API Gateway then triggers the appropriate function in lambda and returns the response it gives with CORS headers appended.

# Lambda Function
The flaskAuthentication lambda function connects to the database to perform read-write operations.
/login sees if a username/password combination exists, performs email verification, and logs the user into the site if successful.
/register allows a person to add a new username/password combination to the database so they can then log into the website.