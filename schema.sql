CREATE TABLE dm_modmail (
    user_id BIGINT UNIQUE,
    thread_id BIGINT UNIQUE
);

CREATE TABLE cotd (
    color_int INTEGER,
    added_at TIMESTAMP WITH TIME ZONE
);