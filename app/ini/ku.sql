drop database if exists hustapp;
create database hustapp;
use hustapp;
create user 'www-data'@'localhost' Identified by 'www-data';
grant select, insert, update, delete on hustapp.* to 'www-data'@'localhost';

create table users (
    `id` varchar(50) not null,
    `school_num` varchar(50) not null,
    `passwd` varchar(50) not null,
    `admin` bool not null,
    `name` varchar(50) not null,
    `image` varchar(500) not null,
	`message` mediumtext not null,
    `created_at` real not null,
	`content` varchar(100) not null,
    unique key `idx_school_num` (`school_num`),
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table comments (
    `id` varchar(50) not null,
	`ku` varchar(50) not null,
    `xinxi_id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `content` mediumtext not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table jwc (
    `id` varchar(50) not null,
    `title` varchar(100) not null,
    `tim` varchar(50) not null,
    `place` varchar(50) not null,
    `url` varchar(60) not null,
    `content` varchar(10000) not null,
	`likes` mediumtext,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table zph (
    `id` varchar(50) not null,
    `title` varchar(100) not null,
    `tim` varchar(50) not null,
    `place` varchar(50) not null,
    `url` varchar(60) not null,
    `content` varchar(10000) not null,
	`likes` mediumtext,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table inter (
    `id` varchar(50) not null,
    `title` varchar(100) not null,
    `tim` varchar(50) not null,
    `place` varchar(50) not null,
    `url` varchar(100) not null,
    `content` varchar(10000) not null,
	`likes` mediumtext,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table lecture (
    `id` varchar(50) not null,
    `title` varchar(100) not null,
    `tim` varchar(50) not null,
    `place` varchar(50) not null,
    `url` varchar(100) not null,
    `content` varchar(10000) not null,
	`likes` mediumtext,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table info (
    `id` varchar(50) not null,
    `title` varchar(100) not null,
    `_type_` varchar(10) not null,
    `content` varchar(10000) not null,
	`likes` mediumtext,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table question (
    `id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `content` mediumtext not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;