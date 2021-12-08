Serenity
Serenity is a Flask app located within CS50 IDE. The goal of this application is to be able to track an user’s mental health status, while also giving additional features like a minimalistic productivity homepage and a diary entry feature. Below are instructions for running and using the website.

Getting Started
First, access the directory containing the source code for Serenity and execute flask run in the terminal. This will start the server. Click on the link shown to open the website. This should bring you to the login page. At the top is a navigation bar with links to register an account and log in. For new users, click register to register a new account. Otherwise type in your username and password to log in.

Creating an Account
In order to access the features of serenity, one needs to create an account. To create an account, click on the "Register" link on the navigation bar. You will see a form with username, password, and password confirmation fields. Our program will hash your password to increase security. The password confirmation must match the above password. Once all the fields have been filled out, click on the Register button to create an account. You will be redirected to the login page.

Log In
Input your username and password, then click on the button below to log in. If the username and password combination is not found, the login page will reload with a message that the username or password is incorrect. Upon successful login, you will be redirected to the home page. The navigation bar has more links now, including the home page (accessible by clicking serenity), quiz, visualizations, diary, entries, and suggestions. The links to register and log in are replaced with a link to log out. 

The Homepage
When logged in, users can access their own homepage. This page pulls stock photos from unplash as the background. Refreshing the page will generate a new image as your background. The homepage also displays a clock, as well as the weather for Cambridge, MA, our current location. Finally, it gives users a daily inspirational quote. By clicking on the button a quote will appear, randomly generated from a preset list. You can click the button to display other quotes.

Taking the Quiz
From the homepage, click on the “quiz” link to be redirected to the mental health quiz.

Viewing the Visualizations
For easy access to previous quiz results, click on the visualizations link. This link allows you to access all previous quiz answers in an easy-to-read table, which displays date of entry, and your results. Each user can only access their entries, to ensure privacy.

Submitting a Diary Entry
From the homepage, click on the “diary” link to be brought to the diary entry page. The page will have two fields for entry: a title and a box for our entry. Entries are capped at 500 characters to ensure succinctness. Click submit entry to submit your entry.

View Entries
You can view your entries by clicking on “entries”. This page will display the date of the entry, the title, and the text for your entry. All entries from one user should be displayed in this page, so users can track their moods and thoughts from one day to the next.

Suggestions
Based on the quiz results, our page will give feedback to users to promote a healthier lifestyle. These include increasing your sleep, increasing exercise, relieving stress, and being positive. We hope this feedback will help guide users into making better decisions.

Log Out
When logged in, click on the "Log Out" link in the navigation bar to log out. You will be redirected to the login page.

Video:
https://youtu.be/uaa_oZQq8Dc