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
