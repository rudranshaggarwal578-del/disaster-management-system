-- DISASTER MANAGEMENT SYSTEM DATABASE

PRAGMA foreign_keys = ON;

-- USERS

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('citizen', 'volunteer', 'authority', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DISASTER REPORTS

CREATE TABLE IF NOT EXISTS disasters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    reported_by INTEGER,

    disaster_type TEXT NOT NULL,

    description TEXT,

    location TEXT NOT NULL,

    latitude REAL,

    longitude REAL,

    severity TEXT DEFAULT 'Medium'
        CHECK(severity IN ('Low', 'Medium', 'High', 'Critical')),

    status TEXT DEFAULT 'Reported'
        CHECK(status IN (
            'Reported',
            'Verified',
            'Assigned',
            'Responding',
            'Resolved',
            'Rejected'
        )),

    people_affected INTEGER DEFAULT 0,

    infrastructure_damage INTEGER DEFAULT 0,

    image_path TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    verified_at TIMESTAMP,

    resolved_at TIMESTAMP,

    FOREIGN KEY (reported_by)
        REFERENCES users(id)
        ON DELETE SET NULL
);


-- RESOURCES

CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    resource_type TEXT NOT NULL,

    quantity INTEGER DEFAULT 0,

    location TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RESOURCE REQUESTS

CREATE TABLE IF NOT EXISTS resource_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    disaster_id INTEGER,

    resource_id INTEGER,

    requested_quantity INTEGER NOT NULL,

    status TEXT DEFAULT 'Pending'
        CHECK(status IN ('Pending', 'Approved', 'Rejected', 'Delivered')),

    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (disaster_id)
        REFERENCES disasters(id)
        ON DELETE CASCADE,

    FOREIGN KEY (resource_id)
        REFERENCES resources(id)
        ON DELETE CASCADE
);

-- VOLUNTEERS

CREATE TABLE IF NOT EXISTS volunteers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER UNIQUE,

    skills TEXT,

    availability TEXT DEFAULT 'Available',

    current_location TEXT,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- DISASTER ASSIGNMENTS

CREATE TABLE IF NOT EXISTS disaster_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    disaster_id INTEGER,

    volunteer_id INTEGER,

    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    arrived_at TIMESTAMP,

    completed_at TIMESTAMP,

    FOREIGN KEY (disaster_id)
        REFERENCES disasters(id)
        ON DELETE CASCADE,

    FOREIGN KEY (volunteer_id)
        REFERENCES volunteers(id)
        ON DELETE CASCADE
);