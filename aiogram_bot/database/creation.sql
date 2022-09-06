-- Bot users table
create table if not exists User (
    user_id integer primary key not null,
    username text not null,
    last_index integer,
    last_reply_command text
);

-- Actual messages table
create table if not exists Message (
    id integer primary key autoincrement not null,
    user_id integer not null,
    chat_id integer not null,
    message_id integer not null,

    foreign key (user_id) references User(user_id) on delete cascade
);

-- Users favorite designs
create table if not exists User_favorites (
    id integer primary key autoincrement not null,
    user_id integer not null,
    resource text not null
);