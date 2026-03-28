BEGIN TRANSACTION;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS "users" (
	"user_id"	INTEGER,
	"username"	TEXT UNIQUE NOT NULL,
	"email"	TEXT UNIQUE NOT NULL,
	"password_hash"	TEXT NOT NULL,
	"first_name" TEXT NOT NULL,
    "last_name" TEXT NOT NULL,
    "age" INTEGER NOT NULL DEFAULT 18,
    "gender" TEXT NOT NULL DEFAULT 'prefer_not_to_say',
    "phone" TEXT,
    "preferences_json" TEXT NOT NULL DEFAULT '{}',
    "last_login" TIMESTAMP,
    "is_active" BOOLEAN NOT NULL DEFAULT 1,
	"role" TEXT NOT NULL DEFAULT 'user',
	"created_at"TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("user_id" AUTOINCREMENT) ON CONFLICT ROLLBACK,
	CHECK("role" = 'admin' OR "role" = 'user' OR "role" = 'medical_student')
);
CREATE TABLE IF NOT EXISTS "user_session" (
	"token"	TEXT PRIMARY KEY NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"expires_at"	TEXT NOT NULL,
	FOREIGN KEY("user_id") REFERENCES "users"("user_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "logs" (
	"log_id"	INTEGER,
	"user_id"	INTEGER,
	"action_type"	TEXT,
	"created_at"	INTEGER DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("log_id" AUTOINCREMENT),
	FOREIGN KEY("user_id") REFERENCES "users"("user_id") ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS "symptoms" (
	"symptom_id"	INTEGER,
	"symptom_name"	TEXT UNIQUE,
	"category"	TEXT,
	PRIMARY KEY("symptom_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "disease" (
	"disease_id"	INTEGER,
	"disease_name"	TEXT UNIQUE,
	"category"	TEXT,
	"severity_level"	TEXT,
	PRIMARY KEY("disease_id" AUTOINCREMENT) ON CONFLICT ROLLBACK,
	CHECK("severity_level" = 'low' OR "severity_level" = 'medium' OR "severity_level" = 'high')
);
CREATE TABLE IF NOT EXISTS "disease_symptoms" (
	"id"	INTEGER,
	"disease_id"	INTEGER,
	"symptom_id"	INTEGER,
	"strength"	REAL, -- strength = P(symptom=1 | disease)
	PRIMARY KEY("id" AUTOINCREMENT) ON CONFLICT ROLLBACK,
	FOREIGN KEY("disease_id") REFERENCES "disease"("disease_id") ON DELETE CASCADE,
	FOREIGN KEY("symptom_id") REFERENCES "symptoms"("symptom_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "symptom_inputs" (
	"input_id"	INTEGER,
	"user_id"	INTEGER,
	"input_text"	BLOB,
	"created_at"	INTEGER DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("input_id" AUTOINCREMENT) ON CONFLICT ROLLBACK,
	FOREIGN KEY("user_id") REFERENCES "users"("user_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "extracted_symptoms" (
	"extracted_id"	INTEGER,
	"input_id"	INTEGER,
	"symptom_id"	INTEGER,
	"confidance_score"	REAL,
	PRIMARY KEY("extracted_id" AUTOINCREMENT) ON CONFLICT ROLLBACK,
	FOREIGN KEY("input_id") REFERENCES "symptom_inputs"("input_id") ON DELETE CASCADE,
	FOREIGN KEY("symptom_id") REFERENCES "symptoms"("symptom_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "predictions" (
	"prediction_id"	INTEGER,
	"input_id"	INTEGER,
	"disease_id"	INTEGER,
	"confidance_score"	REAL, -- confidance_score = P(disease | symptoms)
	PRIMARY KEY("prediction_id" AUTOINCREMENT) ON CONFLICT ROLLBACK,
	FOREIGN KEY("disease_id") REFERENCES "disease"("disease_id") ON DELETE CASCADE,
	FOREIGN KEY("input_id") REFERENCES "symptom_inputs"("input_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "educational_content" (
	"content_id"	INTEGER,
	"disease_id"	INTEGER,
	"title"	TEXT UNIQUE,
	"content_text"	BLOB,
	"is_verified"	INTEGER CHECK(is_verified IN (0, 1)),
	PRIMARY KEY("content_id" AUTOINCREMENT),
	FOREIGN KEY("disease_id") REFERENCES "disease"("disease_id") ON DELETE CASCADE
);





CREATE TABLE IF NOT EXISTS chat_sessions (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_activity TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        state TEXT NOT NULL DEFAULT 'welcome',
        symptoms_json TEXT NOT NULL DEFAULT '[]',
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );

CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        data_json TEXT,
        FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
    );


CREATE TABLE IF NOT EXISTS chat_history (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        ended_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        duration TEXT NOT NULL DEFAULT 'N/A',
        symptoms_json TEXT NOT NULL DEFAULT '[]',
        predictions_json TEXT NOT NULL DEFAULT '[]',
        messages_json TEXT NOT NULL DEFAULT '[]',
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );

COMMIT;
