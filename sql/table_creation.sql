CREATE TABLE Squad(
	Squad VARCHAR(20) PRIMARY KEY NOT NULL,
	URL VARCHAR(100) NOT NULL
)

CREATE TABLE Player(
	Player VARCHAR(50) PRIMARY KEY NOT NULL,
	Nation VARCHAR(10),
	Pos VARCHAR(10),
	Squad VARCHAR(20),
	Age VARCHAR(7),
	Born VARCHAR(5),

	CONSTRAINT FK_Player_Squad FOREIGN KEY (Squad) REFERENCES Squad(Squad)
)


-- 'Rk', 'Squad', 'H/A', 'D', 'GA', 'GD', 'GF', 'L', 'MP', 'Pts', 'Pts/MP', 'W', 'xG', 'xGA', 'xGD', 'xGD/90'
CREATE TABLE SquadRecord(
	Squad VARCHAR(20) NOT NULL,
	Rk INTEGER NOT NULL,
	H_A CHAR(4) NOT NULL,
	W INTEGER NOT NULL,
	D INTEGER NOT NULL,
	L INTEGER NOT NULL,
	GF INTEGER NOT NULL,
	GA INTEGER NOT NULL,
	GD INTEGER NOT NULL,
	MP INTEGER NOT NULL,
	Pts INTEGER NOT NULL,
	Pts_MP FLOAT NOT NULL,
	xG FLOAT NOT NULL,
	xGA FLOAT NOT NULL,
	xGD FLOAT NOT NULL,
	xGD_90 FLOAT NOT NULL,

	CONSTRAINT PK_Squad_Record PRIMARY KEY (Squad,H_A),
	CONSTRAINT FK_Record_Squad FOREIGN KEY (Squad) REFERENCES Squad(Squad)
)



-- 'Wk', 'Day', 'Date', 'Time', 'Home', 'xG_Home', 'Score', 'xG_Away', 'Away', 'Attendance', 'Venue', 'Referee', 'MatchReport', 'Notes', 'MatchID'
CREATE TABLE Match(
	MatchID VARCHAR(30) PRIMARY KEY NOT NULL,
	Wk INTEGER NOT NULL,
	Day VARCHAR(4) NOT NULL,
	Date DATE NOT NULL,
	Time TIME NOT NULL,
	Home VARCHAR(20) NOT NULL,
	xG_Home FLOAT(4) NOT NULL,
	Score VARCHAR(5) NOT NULL,
	xG_Away FLOAT(4) NOT NULL,
	Away VARCHAR(20) NOT NULL,
	Attendance VARCHAR(10),
	Venue VARCHAR(50),
	Referee VARCHAR(40),
	MatchReport VARCHAR(80),
	Notes VARCHAR(10),

	CONSTRAINT FK_Match_Home FOREIGN KEY (Home) REFERENCES Squad(Squad),
	CONSTRAINT FK_Match_Away FOREIGN KEY (Away) REFERENCES Squad(Squad)
)



CREATE TABLE Event(
	MatchID VARCHAR(30) NOT NULL,
	Team VARCHAR(20) NOT NULL,
	Minute VARCHAR(5) NOT NULL,
	Score VARCHAR(5) NOT NULL,
	Player1 VARCHAR(50) NOT NULL,
	Player2 VARCHAR(50),
	Event VARCHAR(25) NOT NULL,
	Notes VARCHAR(20),

	CONSTRAINT FK_Event_Match FOREIGN KEY (MatchID) REFERENCES Match(MatchID),
	CONSTRAINT FK_Event_Squad FOREIGN KEY (Team) REFERENCES Squad(Squad)
)

CREATE TABLE Shot(
	Minute VARCHAR(5) NOT NULL, 
	Player VARCHAR(50) NOT NULL,
	Squad VARCHAR(20) NOT NULL, 
	xG FLOAT(4) NOT NULL, 
	PSxG FLOAT(4), 
	Outcome VARCHAR(20) NOT NULL, 
	Distance INTEGER NOT NULL, 
	Body_Part VARCHAR(20) NOT NULL, 
	Notes VARCHAR(20), 
	SCA1_Player VARCHAR(50), 
	SCA1_Event VARCHAR(20), 
	SCA2_Player VARCHAR(50), 
	SCA2_Event VARCHAR(20), 
	MatchID VARCHAR(30) NOT NULL,

	CONSTRAINT PK_Shot PRIMARY KEY (MatchID,Squad,Player,Minute,xG),
	CONSTRAINT FK_Shot_Player FOREIGN KEY (Player) REFERENCES Player(Player),
	CONSTRAINT FK_Shot_Player1 FOREIGN KEY (SCA1_Player) REFERENCES Player(Player),
	CONSTRAINT FK_Shot_Player2 FOREIGN KEY (SCA2_Player) REFERENCES Player(Player),
	CONSTRAINT FK_Shot_Match FOREIGN KEY (MatchID) REFERENCES Match(MatchID),
	CONSTRAINT FK_Shot_Squad FOREIGN KEY (Squad) REFERENCES Squad(Squad)	
)



CREATE TABLE PlayerMatchStats ( 
	Player VARCHAR(50) NOT NULL,
	# FLOAT(4) ,
	Nation VARCHAR(20) ,
	Pos VARCHAR(10) ,
	Age VARCHAR(6) ,
	Minu INTEGER ,
	Gls INTEGER ,
	Ast INTEGER ,
	PK INTEGER ,
	PKatt INTEGER ,
	Sh INTEGER ,
	SoT INTEGER ,
	CrdY INTEGER ,
	CrdR INTEGER ,
	Touches INTEGER ,
	Tkl INTEGER ,
	Intr INTEGER ,
	Blocks INTEGER ,
	xG FLOAT(4) ,
	npxG FLOAT(4) ,
	xAG FLOAT(4) ,
	SCA INTEGER ,
	GCA INTEGER ,
	Total_Cmp INTEGER ,
	Total_Att INTEGER ,
	Total_TotDist INTEGER ,
	Total_PrgDist INTEGER ,
	Short_Cmp INTEGER ,
	Short_Att INTEGER ,
	Medium_Cmp INTEGER ,
	Medium_Att INTEGER ,
	Long_Cmp INTEGER ,
	Long_Att INTEGER ,
	xA FLOAT(4) ,
	KP INTEGER ,
	Third INTEGER ,
	PPA INTEGER ,
	CrsPA INTEGER ,
	Prog INTEGER ,
	Att INTEGER ,
	PassTypes_Live INTEGER ,
	PassTypes_Dead INTEGER ,
	PassTypes_FK INTEGER ,
	PassTypes_TB INTEGER ,
	PassTypes_Sw INTEGER ,
	PassTypes_Crs INTEGER ,
	PassTypes_TI INTEGER ,
	PassTypes_CK INTEGER ,
	CornerKicks_In INTEGER ,
	CornerKicks_Out INTEGER ,
	CornerKicks_Str INTEGER ,
	Outcomes_Cmp INTEGER ,
	Outcomes_Off INTEGER ,
	Outcomes_Blocks INTEGER ,
	Tackles_Tkl INTEGER ,
	Tackles_TklW INTEGER ,
	Tackles_Def_3rd INTEGER ,
	Tackles_Mid_3rd INTEGER ,
	Tackles_Att_3rd INTEGER ,
	VsDribbles_Tkl INTEGER ,
	VsDribbles_Att INTEGER ,
	VsDribbles_Past INTEGER ,
	Blocks_Blocks INTEGER ,
	Blocks_Sh INTEGER ,
	Blocks_Pass INTEGER ,
	Tkl_plus_Intr INTEGER ,
	Clr INTEGER ,
	Err INTEGER ,
	Def_Pen INTEGER ,
	Def_3rd INTEGER ,
	Mid_3rd INTEGER ,
	Att_3rd INTEGER ,
	Att_Pen INTEGER ,
	Live INTEGER ,
	Dribbles_Succ INTEGER ,
	Dribbles_Att INTEGER ,
	Dribbles_Mis INTEGER ,
	Dribbles_Dis INTEGER ,
	Receiving_Rec INTEGER ,
	Receiving_Prog INTEGER ,
	SndCrdY INTEGER ,
	Fls INTEGER ,
	Fld INTEGER ,
	Offs INTEGER ,
	Crs INTEGER ,
	TklW INTEGER ,
	PKwon INTEGER ,
	PKcon INTEGER ,
	OG INTEGER ,
	Recov INTEGER ,
	AerialDuels_Won INTEGER ,
	AerialDuels_Lost INTEGER ,
	MatchID VARCHAR(30) NOT NULL,

	CONSTRAINT PK_PlayerMatchStats PRIMARY KEY (MatchID,Player),
	CONSTRAINT FK_PMS_Match FOREIGN KEY (MatchID) REFERENCES Match(MatchID),
	CONSTRAINT FK_PMS_Player FOREIGN KEY (Player) REFERENCES Player(Player),	
)

CREATE TABLE GkMatchStats(
	Player VARCHAR(50) NOT NULL, 
	Nation VARCHAR(10),
	Age VARCHAR(7),
	Minutes INTEGER, 
	SoTA INTEGER, 
	GA INTEGER, 
	Saves INTEGER, 
	Save_100 FLOAT(4), 
	PSxG FLOAT(4), 
	Launched_Cmp INTEGER, 
	Launched_Att INTEGER, 
	Launched_Cmp_100 FLOAT(4), 
	Passes_Att INTEGER, 
	Passes_Thr INTEGER, 
	Passes_Launch_100 FLOAT(4), 
	Passes_AvgLen FLOAT(4), 
	GoalKicks_Att INTEGER, 
	GoalKicks_Launch_100 FLOAT(4), 
	GoalKicks_AvgLen FLOAT(4), 
	Crosses_Opp INTEGER, 
	Crosses_Stp INTEGER, 
	Crosses_Stp_100 FLOAT(4), 
	Sweeper_#OPA INTEGER, 
	Sweeper_AvgDist FLOAT(4), 
	MatchID VARCHAR(30) NOT NULL,

	CONSTRAINT PK_GKMatchStats PRIMARY KEY (MatchID,Player),
	CONSTRAINT FK_GKMS_Match FOREIGN KEY (MatchID) REFERENCES Match(MatchID),
	CONSTRAINT FK_GKMS_Player FOREIGN KEY (Player) REFERENCES Player(Player),	
)



SELECT * FROM Squad;
SELECT * FROM SquadRecord;
SELECT * FROM Player;
SELECT * FROM Match;
SELECT * FROM Event;
SELECT * FROM Shot;
SELECT * FROM PlayerMatchStats;
SELECT * FROM GkMatchStats;


--DELETE FROM Shot
--DELETE FROM Event
--DELETE FROM PlayerMatchStats
--DELETE FROM GkMatchStats
