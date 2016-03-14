CREATE TABLE nicks (
	id 		INTEGER PRIMARY KEY AUTOINCREMENT,
	name 	TEXT UNIQUE,
	jid		TEXT
);

CREATE TABLE users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	jid TEXT UNIQUE,
	primary_nick TEXT UNIQUE,
	lastactive INTEGER,
	timeout INTEGER,
	message TEXT,
	admin BOOL,
	bday date
);

CREATE TABLE tags (
	id INTEGER PRIMARY KEY,
	name TEXT UNIQUE
);

CREATE TABLE tag_subscriptions (
	id INTEGER,
	jid TEXT,
	FOREIGN KEY(id) REFERENCES tags(id),
	PRIMARY KEY(id, jid)
);
