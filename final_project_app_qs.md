# SI 364 - Final Project questions

## Overall

* **What's a one-two sentence description of what your app will do?**

I am going to create an application that allows you to store movies you have seen and movies you have not seen, but want to ("wish list"). For movies you add to your "Wish List", you will be able to get a description of the movie.


## The Data

* **What data will your app use? From where will you get it? (e.g. scraping a site? what site? -- careful not to run it too much. An API? Which API?)**
Movie descriptions will be taken from itunes API and movie ratings will be taken from IMDB API.

* **What data will a user need to enter into a form?**
There will be a login page and the user will need to enter the movies they want to add to the "Have Seen List" and "Wish List".

* **How many fields will your form have? What's an example of some data user might enter into it?**
This application is going to have multiple forms. You will be able to search for a movie produced by a specific director or actor. You will also be able to search by title.

* **After a user enters data into the form, what happens? Does that data help a user search for more data? Does that data get saved in a database? Does that determine what already-saved data the user should see?**
When a user searches for a movie it will then be added to a database. This database is storing all the movies they have seen.
* **What models will you have in your application?**
Models will be for each movie, user, Have Seen List and Wish List.

* **What fields will each model have?**
The model for movie will have the title, rating and actors.
The model for each user will have their username, the number of movies on their Wish List and the number of movies on their Have Seen list.
The model for Wish List will have the movie.
The model for Have Seen List will have the movie.
* **What uniqueness constraints will there be on each table? (e.g. can't add a song with the same title as an existing song)**
A constraint will be that if a movie is on your "Have Seen List" it can't also be on your "Wish List". 

* **What relationships will exist between the tables? What's a 1:many relationship between? What about a many:many relationship?**
Many: many relationship will be movie to director or movie to actor.
One: many relationship will be user to movies.
* **How many get_or_create functions will you need? In what order will you invoke them? Which one will need to invoke at least one of the others?**
For each movie and for each user I would need to invoke a get_or_create function.
First there will be one invoked for each user, then for each movie the user searches.

## The Pages

* **How many pages (routes) will your application have?**
There will be 3 pages. A page that searches for movies, a page that adds movies to either Wish List or Have Seen List.

* **How many different views will a user be able to see, NOT counting errors?**
There will be 4 views. A login page, a Wish List page, a page that takes you to movie descriptions and a Have Seen List page.

* **Basically, what will a user see on each page / at each route? Will it change depending on something else -- e.g. they see a form if they haven't submitted anything, but they see a list of things if they have?**
The user is first going to see a page that allows them to login. They will then have an option to view their Wish List or Have Seen page or they can search for a movie. If they choose to search for a movie, they will be taken to a page where you can search by title, director or actor. They then can choose to add this movie to either list. 
## Extras

* **Why might your application send email?**
So that you can send your Wish List to other indiviudals. 

* **If you plan to have user accounts, what information will be specific to a user account? What can you only see if you're logged in? What will you see if you're not logged in -- anything?**
When you're logged in you will be able to see your specific movie lists.

* **What are your biggest concerns about the process of building this application?**
I am most concerned about the aspect of logging in and having different user accounts. 
