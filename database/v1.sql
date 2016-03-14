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
