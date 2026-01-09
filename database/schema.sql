BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "users" (
	"user_id"	INTEGER,
	"username"	TEXT UNIQUE NOT NULL,
	"email"	TEXT,
	"password"	TEXT,
	"role"	TEXT DEFAULT 'user',
	"created_at"	NUMERIC DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("user_id" AUTOINCREMENT) ON CONFLICT ROLLBACK,
	CHECK("role" = 'admin' OR "role" = 'user' OR "role" = 'medical_student')
);
CREATE TABLE IF NOT EXISTS "user_session" (
	"session_id"	INTEGER,
	"user_id"	INTEGER NOT NULL,
	"token"	TEXT UNIQUE NOT NULL,
	"expires_at"	INTEGER,
	PRIMARY KEY("session_id" AUTOINCREMENT),
	FOREIGN KEY("user_id") REFERENCES "users"("user_id")
);
CREATE TABLE IF NOT EXISTS "logs" (
	"log_id"	INTEGER,
	"user_id"	INTEGER,
	"action_type"	TEXT,
	"created_at"	INTEGER DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("log_id" AUTOINCREMENT),
	FOREIGN KEY("user_id") REFERENCES "users"("user_id")
);
CREATE TABLE IF NOT EXISTS "symptoms" (
	"symptom_id"	INTEGER,
	"symptom_name"	TEXT,
	"category"	TEXT,
	PRIMARY KEY("symptom_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "disease" (
	"disease_id"	INTEGER,
	"disease_name"	TEXT,
	"category"	TEXT,
	"severity_level"	TEXT,
	PRIMARY KEY("disease_id" AUTOINCREMENT) ON CONFLICT ROLLBACK,
	CHECK("severity_level" = 'low' OR "severity_level" = 'medium' OR "severity_level" = 'high')
);
CREATE TABLE IF NOT EXISTS "disease_symptoms" (
	"id"	INTEGER,
	"disease_id"	INTEGER,
	"symptom_id"	INTEGER,
	"strength"	REAL,
	PRIMARY KEY("id" AUTOINCREMENT) ON CONFLICT ROLLBACK,
	FOREIGN KEY("disease_id") REFERENCES "disease"("disease_id"),
	FOREIGN KEY("symptom_id") REFERENCES "symptoms"("symptom_id")
);
CREATE TABLE IF NOT EXISTS "symptom_inputs" (
	"input_id"	INTEGER,
	"user_id"	INTEGER,
	"input_text"	BLOB,
	"created_at"	INTEGER DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("input_id" AUTOINCREMENT) ON CONFLICT ROLLBACK,
	FOREIGN KEY("user_id") REFERENCES "users"("user_id")
);
CREATE TABLE IF NOT EXISTS "extracted_symptoms" (
	"extracted_id"	INTEGER,
	"input_id"	INTEGER,
	"symptom_id"	INTEGER,
	"confidance_score"	REAL,
	PRIMARY KEY("extracted_id" AUTOINCREMENT) ON CONFLICT ROLLBACK,
	FOREIGN KEY("input_id") REFERENCES "symptom_inputs"("input_id"),
	FOREIGN KEY("symptom_id") REFERENCES "symptoms"("symptom_id")
);
CREATE TABLE IF NOT EXISTS "predictions" (
	"prediction_id"	INTEGER,
	"input_id"	INTEGER,
	"disease_id"	INTEGER,
	"confidance_score"	REAL,
	PRIMARY KEY("prediction_id" AUTOINCREMENT) ON CONFLICT ROLLBACK,
	FOREIGN KEY("disease_id") REFERENCES "disease"("disease_id"),
	FOREIGN KEY("input_id") REFERENCES "symptom_inputs"("input_id")
);
CREATE TABLE IF NOT EXISTS "educational_content" (
	"content_id"	INTEGER,
	"disease_id"	INTEGER,
	"title"	TEXT,
	"content_text"	BLOB,
	"is_verified"	INTEGER CHECK(0 OR 1),
	PRIMARY KEY("content_id" AUTOINCREMENT),
	FOREIGN KEY("disease_id") REFERENCES "disease"("disease_id")
);
COMMIT;
