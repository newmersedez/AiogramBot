-- Actual messages table
create table if not exists message (
    user_id integer primary key not null,
    message_id integer not null
);

-- Bot users table
create table if not exists user (
    user_id integer primary key not null,
    username text not null,
    fullname text not null
);

-- Users favorite designs
create table if not exists user_favorites (
    id integer primary key not null,
    user_id integer not null,
    resource text not null,

    foreign key (user_id) references user (user_id) on delete cascade
);
