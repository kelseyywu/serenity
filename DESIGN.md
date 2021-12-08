Design
Below is an overview of the design of my Flask app.

General Structure
Significant portions of the structure for the Flask app were adapted from our solution for the Finance problem set. Serenity and the Finance website share several structural similarities, like the usage of user accounts and a similar navigational structure. As such, the register, login, layout, and logout pages are similar to those for Finance. We also took inspiration with parts of helpers.py such as with login_required. Some of the tables in visualizations and entries were loosely inspired by parts of Finance.

HTML templates
To preserve a uniformly styled appearance on all pages of the website, I first created a layout.html template from which most of the other templates extend. layout.html contains meta tags and includes Bootstrap and Javascript functionalities so that they are accessible to all other templates. layout.html also contains the navigation bar, whose links change depending on whether or not the current user is logged in. This was accomplished with a simple Jinja if statement that checks for session["user_id"]. As a result, almost all pages have common visual styling. 

SQL Databases
In serenity.db, there are three tables named users, emotions, and diaryentries. The table “users” stores the username and password hashes of each user along with a primary key. The table “emotions” stores the user id, results of all mental health quiz results (emotions logged, happiness level, and stress level), and respective timestamps. The table “diaryentries” stores the user id, timestamps, diary entry, and diary title. The “users” table is linked to “emotions” and “diaryentries” through the foreign key “user_id” variable that references users.id.

Index
The bulk of the code is found within the index or landing page. To create the clock, we created two javascript functions, startTime() and checkTime(). We then called upon the function in the HTML <body> using onload=startTime(). This allowed us to display an accurate clock on our homepage.

To create the inspirational quote button, we created an array of a few inspirational quotes and used a random number generator to extract a random element from the array every time the button is pressed.

A cool feature on our index page is the ability to create the randomly generated backgrounds, which was also generated via a random number generator and Unsplash’s API. Unsplash is an online repository of freely-usable images by photographers around the world.

Quiz
The mental health quiz feature allows users to answers three different questions via a form:
(1) A series of checkboxes that encapsulate users’ different emotions
(2) A happiness slider that allows users to rate their level of happiness from 0 to 10
(3) A stress slider that allows users to rate their level of stress from 0 to 10

The user’s responses and respective timestamps of those responses are then entered into a SQL table called “emotions”. Then, in the visualizations tab, these responses are displayed in a table coded with CSS.

Diary
The tables were coded with CSS. A form was created on the diary.html tab, which collected valuable information regarding diary entry and title. This information was uploaded into the SQL table, and called upon on the entries.html tab, where the HTML table tabulates through every entry. The app functions are created through Python, where we ensure the correct information is being entered.

Login/Register
Creating an account and logging in is accomplished the same way as in Finance (finding a matching entry in users table and using a hash function to match passwords).