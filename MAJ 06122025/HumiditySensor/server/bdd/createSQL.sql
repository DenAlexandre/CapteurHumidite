
CREATE TABLE "datasensor" (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	datetime DATETIME
, temperature REAL, humidity REAL, "output" TEXT);


-- config definition

CREATE TABLE "config" (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	field TEXT, value TEXT);


INSERT INTO config
(id, field, value)
VALUES(1, 'cons_hum', '50');


SELECT id, field, value
FROM config where field = 'cons_hum';