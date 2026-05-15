PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS students (
  id TEXT PRIMARY KEY,
  student_code TEXT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  github_username TEXT,
  linkedin_url TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS session_content (
  id TEXT PRIMARY KEY,
  course_code TEXT NOT NULL,
  session_title TEXT NOT NULL,
  session_topic TEXT NOT NULL,
  session_transcript TEXT,
  concepts_json TEXT NOT NULL CHECK (json_valid(concepts_json)),
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS assignment_requirement (
  id TEXT PRIMARY KEY,
  session_content_id TEXT NOT NULL,
  assignment_title TEXT NOT NULL,
  assignment_description TEXT NOT NULL,
  required_deliverables_json TEXT NOT NULL CHECK (json_valid(required_deliverables_json)),
  rubric_json TEXT NOT NULL CHECK (json_valid(rubric_json)),
  due_at TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (session_content_id) REFERENCES session_content(id)
);

CREATE TABLE IF NOT EXISTS assignment_submissions (
  id TEXT PRIMARY KEY,
  assignment_requirement_id TEXT NOT NULL,
  student_id TEXT NOT NULL,
  source_type TEXT NOT NULL CHECK (source_type IN ('github_pr', 'local_folder', 'zip_upload')),
  repo_url TEXT,
  local_path TEXT,
  zip_path TEXT,
  youtube_demo_url TEXT,
  linkedin_url TEXT,
  submitted_at TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'submitted'
    CHECK (status IN ('submitted', 'under_review', 'reviewed', 'needs_resubmission')),
  CHECK (
    (source_type = 'github_pr' AND repo_url IS NOT NULL) OR
    (source_type = 'local_folder' AND local_path IS NOT NULL) OR
    (source_type = 'zip_upload' AND zip_path IS NOT NULL)
  ),
  FOREIGN KEY (assignment_requirement_id) REFERENCES assignment_requirement(id),
  FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE INDEX IF NOT EXISTS idx_assignment_requirement_session_content_id
  ON assignment_requirement (session_content_id);

CREATE INDEX IF NOT EXISTS idx_assignment_submissions_assignment_requirement_id
  ON assignment_submissions (assignment_requirement_id);

CREATE INDEX IF NOT EXISTS idx_assignment_submissions_student_id
  ON assignment_submissions (student_id);

CREATE INDEX IF NOT EXISTS idx_assignment_submissions_status
  ON assignment_submissions (status);

CREATE INDEX IF NOT EXISTS idx_assignment_submissions_submitted_at
  ON assignment_submissions (submitted_at);
