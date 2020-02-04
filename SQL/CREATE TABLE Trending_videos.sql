CREATE TABLE `Trending_videos` (
	`video_id` CHAR(11) NOT NULL,
	`title` VARCHAR(100) NOT NULL,
	`publishedAt` CHAR(24) NOT NULL,
	`channelId` CHAR(24) NOT NULL,
	`channelTitle` VARCHAR(100) NOT NULL,
	`categoryId` INT(11) NOT NULL,
	`trending_date` CHAR(8) NOT NULL,
	`tags` TEXT NOT NULL,
	`view_count` INT(11) NOT NULL,
	`likes` INT(11) NOT NULL,
	`dislikes` INT(11) NOT NULL,
	`comment_count` INT(11) NOT NULL,
	`thumbnail_link` CHAR(46) NOT NULL,
	`comments_disabled` VARCHAR(5) NOT NULL,
	`ratings_disabled` VARCHAR(5) NOT NULL,
	`description` TEXT NOT NULL,
	`duration` VARCHAR(11) NOT NULL,
	`country` CHAR(2) NOT NULL,
	`subscriptions` INT(11) NOT NULL,
	`NumeroVideosCanal` INT(11) NOT NULL
)
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
;
