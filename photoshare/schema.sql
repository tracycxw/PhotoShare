CREATE DATABASE photoshare;
USE photoshare;
-- DROP TABLE Pictures CASCADE;
-- DROP TABLE Users CASCADE;
-- DROP TABLE Album CASCADE;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT PRIMARY KEY,
    email varchar(255) UNIQUE NOT NULL,
    password varchar(255) NOT NULL,
    firstName varchar(255) NOT NULL,
    lastName varchar(255) NOT NULL,
    birth DATE NOT NULL,
    profilePic longblob,
    bio varchar(255),
    hometown varchar(255),
    gender varchar(255),
    uploadContribution int NOT NULL,
    commentContribution int NOT NULL
  -- CONSTRAINT users_pk PRIMARY KEY (user_id)
);


CREATE TABLE Album
(
  album_id int4 AUTO_INCREMENT PRIMARY KEY,
  album_name varchar(255) NOT NULL,
  user_id int4 NOT NULL,
  album_date DATE NOT NULL, # should be not null
  -- CONSTRAINT album_pk PRIMARY KEY (album_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);


CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT PRIMARY KEY,
  album_id int4 NOT NULL,
  -- user_id int4,
  imgdata longblob NOT NULL,
  caption VARCHAR(255),
  -- INDEX upid_idx (user_id),
  -- CONSTRAINT pictures_pk PRIMARY KEY (picture_id),
  FOREIGN KEY (album_id) REFERENCES Album(album_id) ON DELETE CASCADE
);

CREATE TABLE Friends(
  friend_id1 int4 NOT NULL,
  friend_id2 int4 NOT NULL,
  PRIMARY KEY (friend_id1, friend_id2),
  FOREIGN KEY(friend_id1) REFERENCES Users(user_id),
  FOREIGN KEY(friend_id2) REFERENCES Users(user_id)
);

CREATE TABLE Comments(
  comment_id int4 AUTO_INCREMENT PRIMARY KEY,
  comment_date DATE NOT NULL,
  description text NOT NULL,
  picture_id int4,
  uid int4,
  FOREIGN KEY(picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE, 
  FOREIGN KEY(uid) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Tags(
  picture_id int4 NOT NULL,
  tag_word VARCHAR(255) NOT NULL,
  PRIMARY KEY (picture_id, tag_word),
  FOREIGN KEY(picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);

CREATE TABLE Likes(
  uid int4 NOT NULL,
  pid int4 NOT NULL,
  PRIMARY KEY (uid, pid),
  FOREIGN KEY(uid) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY(pid) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);



INSERT INTO Users (email, password, firstName, lastName, birth, profilePic,uploadContribution,commentContribution) 
VALUES ('tourist@bu.edu', 'test', '1', 'test', '2018-01-01','i',0,0);
INSERT INTO Album (album_name, user_id, album_date) VALUES ('defaultPictures',1,'2018-01-01');
INSERT INTO Pictures(album_id, imgdata) VALUES (1, 'i');
