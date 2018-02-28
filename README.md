# BhagavadGita

Frontend and REST API for BhagavadGita.io

**Backend** - Flask

**Frontend** - MDBootstrap

**Database** - PostgreSQL

## REST API

The Bhagavad Gita Application Programming Interface (API) allows a web or mobile developer to use the Bhagavad Gita text in their web or mobile application(s). It is a RESTful API that follows some of the Best Practices for designing a REST API.

### Documentation

We have 2 types of documenatations available for this API, both based on the Open API specification.
1. [Swagger UI](https://bhagavadgita.io/apidocs/)
2. [ReDoc](https://bhagavadgita.io/docs/)

## Developing Locally

1. Fork this repository and clone the forked repository.
2. Create and activate a Python 3 virtualenv.
3. Use `pip install -r requirements.txt` to install the requirements.
4. `foreman start -f local` to start the server.
5. API can be accessed at `http://127.0.0.1:5000/api/v1` and frontend can be accessed at `http://127.0.0.1:5000`.

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/gita/BhagavadGita. This project is intended to be a safe, welcoming space for collaboration, and contributors are expected to adhere to the [Contributor Covenant](http://contributor-covenant.org) code of conduct.

To submit a pull request -

1. Fork/clone the repository.
2. Develop.
3. Create a new branch from the master branch.
4. Open a pull request on Github describing what was fixed or added.
