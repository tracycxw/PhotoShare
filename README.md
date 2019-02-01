## README

Chunxi Wang



**OVERVIEW:**

This is a project of photoshare which is a database system for a web based photo social sharing application. The system is functional and is similar to Flickr. Technology stack includes python, MySQL, Flask, jinja, HTML.



**SCHEMA DESCRIPTION:**

The database schema is in the file **schema.sql**. Compared to the last submission, there are some changes in this final schema. (eg. create new table Like, modify attributes in table Users, Tags)



**PREREQUISITE**:

- Add all requirements in requirements.txt. 

- Change *MYSQL_DATABASE_PASSWORD* in the file *app.py*.  

- Log in your MySQL, then input `source schema.sql` in the command line.

- Open another terminal and run `python2.7 app.py` under the project directory, open the localhost link in a browser.

- First time, you should sign in with email: tourist@bu.edu and password: test. In the profile page, you should upload a profile photo (*profile.png* in the file) as other users' default profile photo. Then log out. Now, you can sign up any users and do other interesting things.


**USE CASE**:

- User management
  - For users has a account, they can sign in and view their profile. In their profile page, they can do basic actions like create albums and upload photos. Also, they are allowed to get **tag recommendation**, view the photos **they may also like** and **add/view friends** (exclude tourist, but include themselves).
  - For tourist, they will be given the tourist@bu.edu account, but are not allowed to get into the profile page. They are allowed to comment photos but are not allowed to like photos.

- Tag management

  - User can view their own photos by tag from profile page. And view all users photos by tag from welcome page.
  - For the most popular tags, users are allowed to view 5 of them.
  - Users can search photo by tags in welcome page. If search box is empty, it will show all the photos in the website.
  - You-may-also-like function. If the tag matches the total score for this picture will +1, otherwise -0.001. Order the total score, we can give our recommendation.
  - Tag recommendation. Return tags order by frequency of occurence (exclude the query tags).

- Comments and Like

  - Users (include tourists) are allowed to comment many times on each photo. Users (exclude tourists) are allowed to like each photo at most once. 

- Contribution

  - Total score of a user is upload picture number plus comment number. If a photo or a comment is deleted, the number will not change. The contributor excludes tourist account.


**Conclusion**:

All functions have been implemented. UI can be improved in the future.



