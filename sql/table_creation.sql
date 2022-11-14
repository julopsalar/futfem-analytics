--DELETE FROM Squad
DROP TABLE Squad, Player, Match, Event

CREATE TABLE Squad(
	Squad VARCHAR(20) PRIMARY KEY NOT NULL,
	URL VARCHAR(100) NOT NULL
)

CREATE TABLE Player(
	Player VARCHAR(50) PRIMARY KEY NOT NULL,
	Position VARCHAR(4) NOT NULL,
	OtherPositions VARCHAR(6),
	Squad VARCHAR(50),
	Age VARCHAR(7),
	Born VARCHAR(4)
)

-- 'Wk', 'Day', 'Date', 'Time', 'Home', 'xG_Home', 'Score', 'xG_Away', 'Away', 'Attendance', 'Venue', 'Referee', 'MatchReport', 'Notes', 'MatchID'
CREATE TABLE Match(
	MatchID VARCHAR(30) PRIMARY KEY NOT NULL,
	Wk INTEGER NOT NULL,
	Day VARCHAR(4) NOT NULL,
	Date DATE NOT NULL,
	Time TIME NOT NULL,
	Home VARCHAR(20) NOT NULL,
	xG_Home FLOAT(10) NOT NULL,
	Score VARCHAR(5) NOT NULL,
	xG_Away FLOAT(10) NOT NULL,
	Away VARCHAR(20) NOT NULL,
	Attendance VARCHAR(10),
	Venue VARCHAR(50),
	Referee VARCHAR(40),
	MatchReport VARCHAR(80),
	Notes VARCHAR(10)
	
)

CREATE TABLE Event(
	MatchReport VARCHAR(30) NOT NULL,
	MatchMin VARCHAR(5) NOT NULL,
	Event VARCHAR(25) NOT NULL,
	Player1 VARCHAR(50) NOT NULL,
	Player2 VARCHAR(50)
)

--INSERT INTO Squad(Squad, Url) VALUES ('Barcelona', 'cosasdeprueba.com')

SELECT * FROM Squad
SELECT * FROM Player
SELECT * FROM Event
SELECT * FROM Match