CREATE TABLE Squad(
	SquadID VARCHAR(10) PRIMARY KEY NOT NULL,
	Squad VARCHAR(20) NOT NULL,
	URL VARCHAR(100) NOT NULL
)
SELECT * FROM Squad;

-- 'Rk', 'Squad', 'H/A', 'D', 'GA', 'GD', 'GF', 'L', 'MP', 'Pts', 'Pts/MP', 'W', 'xG', 'xGA', 'xGD', 'xGD/90'
CREATE TABLE SquadRecord(
	SquadID VARCHAR(10) NOT NULL,
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
	Pts_MP DECIMAL(6,3) NOT NULL,
	xG DECIMAL(6,3) NOT NULL,
	xGA DECIMAL(6,3) NOT NULL,
	xGD DECIMAL(6,3) NOT NULL,
	xGD_90 DECIMAL(6,3) NOT NULL,

	CONSTRAINT PK_Squad_Record PRIMARY KEY (SquadID,H_A),
	CONSTRAINT FK_Record_Squad FOREIGN KEY (SquadID) REFERENCES Squad(SquadID)
)
SELECT * FROM SquadRecord;

CREATE TABLE Player(
	PlayerID VARCHAR(10) PRIMARY KEY NOT NULL,
	Player VARCHAR(50) NOT NULL,
	Nation VARCHAR(10),
	Pos VARCHAR(10) NOT NULL,
	Squad VARCHAR(10) NOT NULL,
	Age VARCHAR(7) ,
	Born VARCHAR(5),

	CONSTRAINT FK_Player_Squad FOREIGN KEY (Squad) REFERENCES Squad(SquadID)
)
SELECT * FROM Player;

-- 'Wk', 'Day', 'Date', 'Time', 'Home', 'xG_Home', 'Score', 'xG_Away', 'Away', 'Attendance', 'Venue', 'Referee', 'MatchReport', 'Notes', 'MatchID'
CREATE TABLE Match(
	MatchID VARCHAR(10) PRIMARY KEY NOT NULL,
	Wk INTEGER NOT NULL,
	Day VARCHAR(4) NOT NULL,
	Date DATE NOT NULL,
	Time TIME NOT NULL,
	Home VARCHAR(10) NOT NULL,
	xG_Home DECIMAL(6,3) NOT NULL,
	Score VARCHAR(5) NOT NULL,
	xG_Away DECIMAL(6,3) NOT NULL,
	Away VARCHAR(10) NOT NULL,
	Attendance VARCHAR(10),
	Venue VARCHAR(50),
	Referee VARCHAR(40),
	Notes VARCHAR(10),

	CONSTRAINT FK_Match_Home FOREIGN KEY (Home) REFERENCES Squad(SquadID),
	CONSTRAINT FK_Match_Away FOREIGN KEY (Away) REFERENCES Squad(SquadID)
)
SELECT * FROM Match;



CREATE TABLE Event(
	MatchID VARCHAR(10) NOT NULL,
	SquadID VARCHAR(10) NOT NULL,
	Minute VARCHAR(5) NOT NULL,
	Score VARCHAR(5) NOT NULL,
	Player1 VARCHAR(10) NOT NULL,
	Player2 VARCHAR(10),
	Event VARCHAR(25) NOT NULL,

	CONSTRAINT FK_Event_Match FOREIGN KEY (MatchID) REFERENCES Match(MatchID),
	CONSTRAINT FK_Event_Squad FOREIGN KEY (SquadID) REFERENCES Squad(SquadID)
)

SELECT * FROM Event;

CREATE TABLE Shot(
	Minute VARCHAR(5) NOT NULL, 
	Player VARCHAR(10) NOT NULL,
	Squad VARCHAR(10) NOT NULL, 
	xG DECIMAL(6,3) NOT NULL, 
	PSxG DECIMAL(6,3), 
	Outcome VARCHAR(20) NOT NULL, 
	Distance INTEGER NOT NULL, 
	Body_Part VARCHAR(20) NOT NULL, 
	Notes VARCHAR(20), 
	SCA1_Player VARCHAR(10)NULL, 
	SCA1_Event VARCHAR(20), 
	SCA2_Player VARCHAR(10) NULL, 
	SCA2_Event VARCHAR(20), 
	MatchID VARCHAR(10) NOT NULL,

	CONSTRAINT PK_Shot PRIMARY KEY (MatchID,Squad,Player,Minute,xG,Distance),
	CONSTRAINT FK_Shot_Player FOREIGN KEY (Player) REFERENCES Player(PlayerID),
	CONSTRAINT FK_Shot_Squad FOREIGN KEY (Squad) REFERENCES Squad(SquadID),
	--CONSTRAINT FK_Shot_Player1 FOREIGN KEY (SCA1_Player,Squad) REFERENCES Player(Player,Squad),
	--CONSTRAINT FK_Shot_Player2 FOREIGN KEY (SCA2_Player,Squad) REFERENCES Player(Player,Squad),
	CONSTRAINT FK_Shot_Match FOREIGN KEY (MatchID) REFERENCES Match(MatchID)
)

SELECT * FROM Shot;

CREATE TABLE PlayerMatchStats(
	PlayerID VARCHAR(10) NOT NULL, 
    #       INTEGER,
	Nation  VARCHAR(10),
    Pos     VARCHAR(10),
    Age     VARCHAR(10),
    Min     INTEGER,
    Gls     INTEGER,
    Ast     INTEGER,
    PK      INTEGER,
    PKatt   INTEGER,
    Sh      INTEGER,
    SoT     INTEGER,
    CrdY    INTEGER,
    CrdR    INTEGER,
    Touches INTEGER,
    Tkl     INTEGER,
    Int     INTEGER,
    Blocks  INTEGER,
    xG      DECIMAL(6,3),
    npxG    DECIMAL(6,3),
    xAG     DECIMAL(6,3),
    SCA     INTEGER,
    GCA     INTEGER,
    Passes_Cmp      INTEGER,
    Passes_Att      INTEGER,
    Passes_Cmp_100  DECIMAL(6,3),
    Passes_Prog     INTEGER,
    Dribbles_Succ   INTEGER,
    Dribbles_Att    INTEGER,
    Total_Cmp       INTEGER,
    Total_Att       INTEGER,
    Total_Cmp_100   DECIMAL(6,3),
    Total_TotDist   INTEGER,
    Total_PrgDist   INTEGER,
    Short_Cmp       INTEGER,
    Short_Att       INTEGER,
    Short_Cmp_100   DECIMAL(6,3),
    Medium_Cmp      INTEGER,
    Medium_Att      INTEGER,
    Medium_Cmp_100  DECIMAL(6,3),
    Long_Cmp    INTEGER,
    Long_Att    INTEGER,
    Long_Cmp_100    DECIMAL(6,3),
    xA      DECIMAL(6,3),
    KP      INTEGER,
    Third     INTEGER,
    PPA     INTEGER,
    CrsPA   INTEGER,
    Prog    INTEGER,
    Att     INTEGER,
    PassTypes_Live  INTEGER,
    PassTypes_Dead  INTEGER,
    PassTypes_FK    INTEGER,
    PassTypes_TB    INTEGER,
    PassTypes_Sw    INTEGER,
    PassTypes_Crs   INTEGER,
    PassTypes_TI    INTEGER,
    PassTypes_CK    INTEGER,
    CornerKicks_In  INTEGER,
    CornerKicks_Out INTEGER,
    CornerKicks_Str INTEGER,
    Outcomes_Cmp    INTEGER,
    Outcomes_Offs    INTEGER,
    Outcomes_Blocks INTEGER,
    Tackles_Tkl     INTEGER,
    Tackles_TklW    INTEGER,
    Tackles_Def3rd  INTEGER,
    Tackles_Mid3rd  INTEGER,
    Tackles_Att3rd  INTEGER,
    VsDribbles_Tkl  INTEGER,
    VsDribbles_Att  INTEGER,
    VsDribbles_Tkl_100      DECIMAL(6,3),
    VsDribbles_Past INTEGER,
    Blocks_Blocks   INTEGER,
    Blocks_Sh       INTEGER,
    Blocks_Pass     INTEGER,
    Tkl_plus_Int    INTEGER,
    Clr     INTEGER,
    Err     INTEGER,
    Touches_Touches INTEGER,
    Touches_DefPen  INTEGER,
    Touches_Def3rd  INTEGER,
    Touches_Mid3rd  INTEGER,
    Touches_Att3rd  INTEGER,
    Touches_AttPen  INTEGER,
    Touches_Live    INTEGER,
    Dribbles_Succ_100       DECIMAL(6,3),
    Dribbles_Mis    INTEGER,
    Dribbles_Dis    INTEGER,
    Receiving_Rec   INTEGER,
    Receiving_Prog  INTEGER,
    SndCardY    INTEGER,
    Fls     INTEGER,
    Fld     INTEGER,
    Offs     INTEGER,
    Crs     INTEGER,
    TklW    INTEGER,
    PKwon   INTEGER,
    PKcon   INTEGER,
    OG      INTEGER,
    Recov   INTEGER,
    AerialDuels_Won INTEGER,
    AerialDuels_Lost    INTEGER,
    AerialDuels_Won_100     DECIMAL(6,3),
    SquadID VARCHAR(10) NOT NULL,
    MatchID VARCHAR(10) NOT NULL,

	CONSTRAINT PK_PlayerMatchStats PRIMARY KEY (MatchID,PlayerID),
	CONSTRAINT FK_PMS_Match FOREIGN KEY (MatchID) REFERENCES Match(MatchID),
	CONSTRAINT FK_PMS_Player FOREIGN KEY (PlayerID) REFERENCES Player(PlayerID)	

)


CREATE TABLE GkMatchStats(
	PlayerID VARCHAR(10) NOT NULL,
    Nation VARCHAR(6),
    Age VARCHAR(6),
    Min INTEGER,
    SoTA INTEGER,
    GA INTEGER,
    Saves INTEGER,
    Save_100 DECIMAL(6,3),
    PSxG DECIMAL(6,3),
    Launched_Cmp INTEGER,
    Launched_Att INTEGER,
    Launched_Cmp_100 DECIMAL(6,3),
    Passes_Att INTEGER,
    Passes_Thr INTEGER,
    Passes_Launch_100 DECIMAL(6,3),
    Passes_AvgLen DECIMAL(6,3),
    GoalKicks_Att INTEGER,
    GoalKicks_Launch_100 DECIMAL(6,3),
    GoalKicks_AvgLen DECIMAL(6,3),
    Crosses_Opp INTEGER,
    Crosses_Stp INTEGER,
    Crosses_Stp_100 DECIMAL(6,3),
    Sweeper_#OPA INTEGER,
    Sweeper_AvgDist DECIMAL(6,3),
    SquadID VARCHAR(10) NOT NULL,
    MatchID VARCHAR(10) NOT NULL,

	CONSTRAINT PK_GKMatchStats PRIMARY KEY (MatchID,PlayerID),
	CONSTRAINT FK_GKMS_Match FOREIGN KEY (MatchID) REFERENCES Match(MatchID),
	CONSTRAINT FK_GKMS_Player FOREIGN KEY (PlayerID) REFERENCES Player(PlayerID)
)


SELECT * FROM PlayerMatchStats;
SELECT * FROM GkMatchStats;

DELETE FROM Event
