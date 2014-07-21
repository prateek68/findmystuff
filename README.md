##10/10/2013##
##Name - findmystuff##
##version number - 1.0##
This project was undertaken by our team to develop a lost and found system for IIIT-Delhi students.

Key features

1) Report Lost and Found items
2) Automatic update on facebook page
3) Google Map Integration
4) Gmail Smtp Integration

##Installation instructions ##

For this u need to clone our directory , a clone link or a download link would be there at the top right corner in the overview section. To clone our project u need to first install mercurial on your system this can be done by

    sudo apt-get install mercurial 

Now to clone our project in your current working directory u need to type the following command in your terminal

    hg clone clone_link_of_our_project 

After doing this all our project files would be cloned in your current working directory.

Now u also need to install pip on your system this can be done by following commands 
    
    sudo apt-get install pip
    
We have used google openid for authentication , in order to use the authentication system on your system type these commands on your terminal 
 
    sudo pip install python-social-auth
    
    export PYTHONPATH=$PYTHONPATH:$/django-social-auth/


Now you have everything installed on your sysytem , to run our project u need to follow these commands in your project directory
 
  
       
       python manage.py syncdb

Go on and create an admin account and remember its login details and run our project on your local machine by typing 
    
       python manage.py runserver

The site get hosted on your local machine go on and open the link shown in your terminal on a browser window.
Default login is 127.0.0.1:8000

##Configuring the 404 Easter Egg##
Refer to [this wiki](https://github.com/IIIT-Delhi/lost-n-found/wiki/Adding-404-Easter-Egg-to-your-web-app)
