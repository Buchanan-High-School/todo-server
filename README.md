# todo-server

A simple Flask JSON server which writes to a SQL database from a frontend. 

The purpose of this project is to allow first-year web development students to practice building frontend systems for pre-existing services which expose JSON APIs.

This is meant to be hosted locally without global access. As such, authentication is minimal and data should not be considered secure. Do not deploy without modifications if you are collecting sensitive or personally identifying information from users.

## Installation

You will need:

- postgres
- nginx
- Python

Install Flask + dependencies

`pip install -r requirements.txt`

You can also install with `rye` or `uv`

`rye sync`
`uv sync`

Modify `.env` and `.config.py.sample` with your environment variables for database interactions.

## API

### Authentication

This is a teaching backend, so authentication is done with a simple `Basic` header.

```javascript
let options = {
	headers: {
		"Authorization": "Basic username:password"
	}
}
```

### Request headers

`todo-server` expects JSON and will return JSON. Set a header to ensure the proper format is returned.

```javascript
let options = {
	headers: {
		// authorization header
		"Content-Type": "application/json"
	}
}
```

Other data types can be added to handle different headers.

### Responses

All respones are in JSON and have a `status` key you can use to check for errors.

Successful responses include the `data` key with the results of the operation. An error will have the `message` key with more information about the error.

```javascript
// Successful response
{
	"status": "success",
	"data": ...
}

// Error response
{
	"status": "error",
	"message": ...
}
```

## Endpoints

### Get all todos

`GET http://todo-server.local/todo` List all todos for a user.

This will return an array of all todo items for the requested user.

```javascript
{
	data: [
		{
			"id": 1,
			"completed": false,
			"created_at": "2025-02-05",
			"description": "Looooong walk.",
			"due": "2025-02-07",
			"title": "Walk the dog"
		},
		{
			"id": 2,
			"completed": false,
			"created_at": "2025-02-05",
			"description": "He only eats wet food.",
			"due": "2025-02-10",
			"title": "Feed the cat"
		},
	],
	status: "success"
}
```

### Create a todo

`POST http://todo-server.local/todo` create a todo item for a given user.

#### Required parameters

- `<string> title`: heading for the item

#### Optional parameters

- `<string> description`: details about the todo item
- `<Date> due`: ISO formatted due date for the given item. If omitted, the due date will automatically be set to one day in the future from the time of creation.
- `<Boolean> completed`: whether or not the item is completed.

Request

```javascript
let options = {
	headers: {
		"Authorization": "Basic username:password",
		"Content-Type": "application/json"
	},
	method: "POST",
	body: {
		title: "My todo",
		description: "This is a thing to do",
		due: new Date().toISOString(),
		completed: false
	}
}

fetch("http://todo-server.local/todo", options)
```

Response

```javascript
{
	"created": {
		"id": 3,
		"title": "My todo",
		"description": "This is a thing to do",
		"due": "2025-02-06",
		"completed": false
	},
	"data": [
		{
			// array of all todo objects
		}
	],
	"status": "success" 
}
```

### Get a single todo

`GET http://todo-server.local/todo/1` Get single todo for a user.

```javascript
{
	data: {
		"id": 1,
		"completed": false,
		"created_at": "2025-02-05",
		"description": "Looooong walk.",
		"due": "2025-02-07",
		"title": "Walk the dog"
	},
	status: "success"
}
```

### Update a todo

`PUT http://todo-server.local/todo/1` update a single todo item

Valid fields sent in the request will be updated on the todo object. Empty requests will return a 400 Bad Request error.

#### Optional parameters

- `<string> title`: heading for the item
- `<string> description`: details about the todo item
- `<Date> due`: due date for the given item. If omitted, the due date will automatically be set to one day in the future from the time of creation.
- `<Boolean> completed`: whether or not the item is completed.

```javascript
let options = {
	headers: { // request headers },
	method: "PUT",
	body: {
		"title": "My new title"
	}
}

fetch("http://todo-server.local/todo/1", options)
```

Returns
```javascript
{
	created: {
		"id": 1,
		"title": "My new title",
		"description": "This is a thing to do",
		"due": "2025-02-06",
		"completed": false
	},
	data: [
		{
			// all todo items
		}
	],
	status: "success"
}
```

### Delete a todo

`DELETE http://todo-server.local/todo/1` delete a todo for a user

```javascript
let options = {
	headers: { // request headers },
	method: "DELETE"
}
```

Returns

```javascript
fetch("http://todo-server.local/todo/1", options)

{
	data: [
		{
			// remaining todo items
		}
	],
	status: "success"
}
```
