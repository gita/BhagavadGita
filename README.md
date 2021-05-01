<p align="center">
  <a href="https://bhagavadgita.io">
    <img src="app/static/images/app/gita.png" alt="Bhagavad Gita" width="500">
  </a>
</p>

<p align="center">
  A not-for-profit initiative to help spread the transcendental wisdom from the Bhagavad Gita to people around the world. Built for Gita readers by Gita readers.
</p>

## ⚠️ We are in the process of redesigning the app from scratch for v2 and are actively looking for contributors who would be interested in helping out. Please read the Contributing section below if you are interested.

## ℹ️ Repositories for v2
For v2 of BhagavadGita.io, we plan to separate the backend and frontend layers. Hence, the code for [backend will be hosted here](https://github.com/gita/bhagavad-gita-backend) and that for the [frontend will be hosted here](https://github.com/gita/bhagavad-gita-frontend).

This repository will host general resources like roadmap, v2 plan, documentation etc for BhagavadGita.io.

## Contributing

There are many ways in which you can participate in the project, for example:

* [Submit bugs](https://github.com/gita/BhagavadGita/issues/new?template=bug_report.md) and [feature requests](https://github.com/gita/BhagavadGita/issues/new?template=feature_request.md), and help us verify as they are checked in
* Review [source code changes](https://github.com/gita/BhagavadGita/pulls)

If you are interested in, please see the following documents - 

* [Roadmap](https://github.com/gita/BhagavadGita/wiki/Roadmap)
* [BhagavadGita.io v2 Plan](https://github.com/gita/BhagavadGita/wiki/BhagavadGita.io-v2-Plan) (**START HERE**)
* [Contributing guide](https://github.com/gita/BhagavadGita/blob/master/CONTRIBUTING.md)
* [How to Contribute](https://github.com/gita/BhagavadGita/wiki/How-to-Contribute)
* [Coding guidelines](https://github.com/gita/BhagavadGita/wiki/Coding-Guidelines)
* [Submitting pull requests](https://github.com/gita/BhagavadGita/wiki/How-to-Contribute#pull-requests)
* [Finding an issue to work on](https://github.com/gita/BhagavadGita/wiki/How-to-Contribute#where-to-contribute)

## Contributors needed -
Please [fill out this form](https://docs.google.com/forms/d/1vs1C1Cyf8wie_SjxWfWCSZO9agjVo0-m_Xxd9n6VD5E) if you interested in any of the roles listed below or have suggestions for any other roles.

### Developer
Backend, frontend, full-stack devs to build the web application. Android and iOS devs to build android and iOS apps.

### Designer
UI and UX designers needed to design the web and mobile apps in order to provide the best possible experience to the user, helping them in reading.

### Product manager
to manage the cross-functional team.

### SEO expert
to optimize the apps for search engine and app store discovery.

### Everyone else interested in contributing.
Suggestions are more than welcome.

## Feedback

* Ask a question on [Slack](https://join.slack.com/t/thegitainitiative/shared_invite/zt-dclsan2f-gL2s3oj1P3UQsc5v2fKpDQ)
* [Request a new feature](CONTRIBUTING.md)
* Up vote [popular feature requests](https://github.com/gita/BhagavadGita/issues?q=is%3Aopen+is%3Aissue+label%3Afeature-request+sort%3Areactions-%2B1-desc)
* [File an issue](https://github.com/gita/BhagavadGita/issues)
* Follow [@shrikrishna](https://twitter.com/shrikrishna) and let us know what you think!

---
## OLD VERSION (v1)

Frontend and REST API for BhagavadGita.io

**Backend** - Flask

**Frontend** - Material Design

**Database** - PostgreSQL, ElasticSearch

## REST API

The Bhagavad Gita Application Programming Interface (API) allows a web or mobile developer to use the Bhagavad Gita text in their web or mobile application(s). It follows some of the Best Practices for designing a REST API.

### Current version
The current version of the API is v1. We encourage you to explicitly use this version in the url.

### Schema
All API access is over HTTPS, and accessed from https://bhagavadgita.io/api/v1. All data is sent and received as JSON.

### Authentication
HTTP requests to the BHAGAVAD GITA API are protected with OAUTH2 authentication.
To be able to use the API, you need to be a registered [BhagavadGita.io](https://bhagavadgita.io) user. After signing in, you can register your applications from your Account Dashboard after which you will be issued a Client ID and Client Secret specific to an application that can be used to programatically get the access_token(valid for 300sec).

**How to get an access token?**
Make a POST request to `/auth/oauth/token` with these parameters sent in Headers - 
1. Client ID - Obtained from Account Dashboard after registering an app.
2. Client Secret - Obtained from Account Dashboard after registering an app.
3. Grant Type - Use `client credentials`.
4. Scope - Use `verse` if you just want to access the verses, `chapter` if you just want to access the chapters and `verse chapter` if you want access to both.

Example - 

`curl -X POST "https://bhagavadgita.io/auth/oauth/token" -H "accept: application/json" -H "content-type: application/x-www-form-urlencoded" -d "client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&grant_type=client_credentials&scope=verse%20chapter"`

Then, you can use the received access_token to access any of the endpoints. You can send the access_token as a header or as a query parameter.

Examples -

1. Query Parameter

`curl -X GET "https://bhagavadgita.io/v1/chapters?access_token=YOUR_ACCESS_TOKEN" -H "accept: application/json"`

2. Header

`curl -X GET \
  https://bhagavadgita.io/v1/chapters \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'`

### Documentation

We have 2 types of documenatations available for this API, both based on the Open API specification.
1. [Swagger UI](https://bhagavadgita.io/apidocs/)
2. [ReDoc](https://bhagavadgita.io/docs/)

## Developing Locally

1. Fork this repository and clone the forked repository.
2. Create and activate a Python 3 virtualenv.
3. Use `pip install -r requirements.txt` to install the requirements.
4. `python manage.py runserver` to start the server.
5. Create an environment file `config.env`. Please open an issue or email contact@bhagavadgita.io for the credentials of the file.
6. Frontend can be accessed at `http://127.0.0.1:5000` and API docs can be accessed at `http://127.0.0.1:5000/apidocs/`.

---
