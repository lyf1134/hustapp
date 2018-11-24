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
    `created_at` real not null,
    unique key `idx_school_num` (`school_num`),
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
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;