-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 11, 2026 at 11:56 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `movie_booking`
--

-- --------------------------------------------------------

--
-- Table structure for table `admins`
--

CREATE TABLE `admins` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admins`
--

INSERT INTO `admins` (`id`, `username`, `password`) VALUES
(1, 'admin', 'admin123');

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

CREATE TABLE `bookings` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `show_id` int(11) DEFAULT NULL,
  `seats` text NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `status` varchar(50) DEFAULT 'Pending',
  `booking_date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bookings`
--


-- --------------------------------------------------------

--
-- Table structure for table `movies`
--

CREATE TABLE `movies` (
  `id` int(11) NOT NULL,
  `title` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `poster_image` varchar(255) DEFAULT NULL,
  `trailer_url` varchar(255) DEFAULT NULL,
  `duration_minutes` int(11) DEFAULT NULL,
  `genre` varchar(50) DEFAULT NULL,
  `rating` float DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `movies`
--

INSERT INTO `movies` (`id`, `title`, `description`, `poster_image`, `trailer_url`, `duration_minutes`, `genre`, `rating`, `created_at`) VALUES
(1, 'Dhurandhar ', 'A mysterious traveler slips into the heart of Karachis underbelly and rises through its ranks with lethal precision, only to tear the notorious ISI-Underworld nexus apart from within.', 'dhurandhar.jpg','https://youtu.be/BKOVzHcjEIo?si=7i6ovNAeEP4OUs2c', 214, 'Action ', 0, '2026-02-09 10:19:59'),
(2, 'Kick', 'An adrenaline junkie walks away from a whirlwind romance and embraces a new life as a thief, though he soon finds himself pursued by veteran police officer and engaged in a turf war with a local gangster.', 'kick.jpg','https://youtu.be/u-j1nx_HY5o?si=YKtY1vw2zn0J7YOB', 150, 'Action ', 0, '2026-02-09 11:05:54'),
(3, 'FS6', 'Hobbs has Dominic and Brian reassemble their crew to take down a team of mercenaries, but Dominic unexpectedly gets sidetracked with facing his presumed deceased girlfriend, Letty.', 'fs6.jpg', 'https://youtu.be/dKi5XoeTN0k?si=ofioZYKL5zXRzhWG', 60, 'Animation', 0, '2026-02-09 13:35:09');

-- Add five more movies (ids 4..8)
INSERT INTO `movies` (`id`, `title`, `description`, `poster_image`, `trailer_url`, `duration_minutes`, `genre`, `rating`, `created_at`) VALUES
(4, 'Baby', 'An elite counter-intelligence unit learns of a plot, masterminded by a maniacal madman. With the clock ticking, its up to them to track the terrorists international tentacles and prevent them from striking at the heart of India.', 'baby.jpg', 'https://youtu.be/-Yu_2nyOP5o?si=zUI3dYDbBsUdlNtA', 142, 'Sci-Fi', 8.3, '2026-02-11 09:00:00'),
(5, 'Holiday', 'A military officer attempts to hunt down a terrorist, destroy a terrorist gang and deactivate the sleeper cells under its command.', 'holiday.jpg', 'https://youtu.be/bXGxcBYeRsw?si=Ko1KqV_QFBR4cUk2', 125, 'Drama', 7.9, '2026-02-11 09:05:00'),
(6, 'OMG: Oh My God!', 'An unhappy civilian asks the court to mandate comprehensive education in schools in a dramatic yet amusing courtroom play.', 'omg.jpg', 'https://youtu.be/eSfJ9NTE0OE?si=rdCY_BdIvbSifxUe', 111, 'Thriller', 7.4, '2026-02-11 09:10:00'),
(7, 'Fukrey 3', 'The paths of four dream-chasing college friends cross with an array of colourful characters, from a tough-talking Punjabi female don to a Jugaad Baaz college watchman. Mayhem ensues.', 'fukray.jpg', 'https://youtu.be/0A6gpPuw9ak?si=ZbKY4id5t48urgyA', 98, 'Romance', 7.1, '2026-02-11 09:15:00'),
(8, 'Mission Impossible', 'Hunt and the IMF pursue a dangerous AI called the Entity thats infiltrated global intelligence. With governments and a figure from his past in pursuit, Hunt races to stop it from forever changing the world.', 'impossible.jpg', 'https://youtu.be/ZBzG3sspBzA?si=mWg36rvoUQ9wh3WT', 104, 'Music', 8.0, '2026-02-11 09:20:00');

-- --------------------------------------------------------

--
-- Table structure for table `shows`
--

CREATE TABLE `shows` (
  `id` int(11) NOT NULL,
  `movie_id` int(11) DEFAULT NULL,
  `screen` varchar(50) NOT NULL,
  `show_time` datetime NOT NULL,
  `price_platinum` decimal(10,2) NOT NULL,
  `price_gold` decimal(10,2) NOT NULL,
  `price_silver` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `shows`
--

INSERT INTO `shows` (`id`, `movie_id`, `screen`, `show_time`, `price_platinum`, `price_gold`, `price_silver`) VALUES
(4, 2, 'Screen 1', '2026-02-10 05:00:00', 300.00, 250.00, 200.00),
(6, 1, 'Screen 1', '2026-02-10 12:00:00', 300.00, 250.00, 200.00),
(7, 3, 'Screen 1', '2026-02-12 05:00:00', 300.00, 250.00, 200.00);

-- Update existing rows with default screen values
UPDATE `shows` SET `screen` = 'Screen 2' WHERE `id` IN (8, 9, 10);
UPDATE `shows` SET `screen` = 'Screen 3' WHERE `id` IN (11, 12, 13);
UPDATE `shows` SET `screen` = 'Screen 4' WHERE `id` IN (14, 15, 16);
UPDATE `shows` SET `screen` = 'Screen 5' WHERE `id` IN (17, 18, 19);
UPDATE `shows` SET `screen` = 'Screen 6' WHERE `id` IN (20, 21, 22);

-- Add shows for newly inserted movies (ids 4..8)
INSERT INTO `shows` (`id`, `movie_id`, `screen`, `show_time`, `price_platinum`, `price_gold`, `price_silver`) VALUES
(8, 4, 'Screen 1', '2026-02-13 12:00:00', 300.00, 250.00, 200.00),
(10, 4, 'Screen 2', '2026-02-13 19:00:00', 300.00, 250.00, 200.00),
(11, 5, 'Screen 3', '2026-02-14 12:00:00', 300.00, 250.00, 200.00),
(12, 5, 'Screen 4', '2026-02-14 16:00:00', 300.00, 250.00, 200.00),
(13, 5, 'Screen 5', '2026-02-14 20:35:48', 300.00, 250.00, 200.00),
(14, 6, 'Screen 4', '2026-02-15 11:38:49', 300.00, 250.00, 200.00),
(15, 6, 'Screen 3', '2026-02-15 14:30:00', 300.00, 250.00, 200.00),
(16, 6, 'Screen 2', '2026-02-15 19:30:00', 300.00, 250.00, 200.00),
(17, 7, 'Screen 1', '2026-02-16 10:30:00', 300.00, 250.00, 200.00),
(18, 7, 'Screen 2', '2026-02-16 14:00:00', 300.00, 250.00, 200.00),
(19, 7, 'Screen 3', '2026-02-16 18:38:49', 300.00, 250.00, 200.00),
(20, 8, 'Screen 4', '2026-02-17 13:00:00', 300.00, 250.00, 200.00),
(21, 8, 'Screen 5', '2026-02-17 17:00:00', 300.00, 250.00, 200.00),
(22, 8, 'Screen 4', '2026-02-17 20:30:00', 300.00, 250.00, 200.00);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `created_at`) VALUES
(1, 'h', 'h@gmail.com', 'scrypt:32768:8:1$t6Ein29H19EIkTHL$042b96e466759d48f5424e4faa75758faf4caa0a5bed513ab552a11480950d3e6724a1cf934c539863df2e66cbd10802acd682ad4610e88c5b15278e0599ae7f', '2026-02-09 10:29:20'),
(2, 'm', 'm@gmail.com', 'scrypt:32768:8:1$4EOLYa5cnxWG7jka$af86fd1423855917fa853b928b7456939c8889995200a1b8d973b0c030bfdf98dc75b47606112240dcbcb4f5f79b2bffbc455a63c8b381157adc80ae11ce842d', '2026-02-09 10:51:15');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admins`
--
ALTER TABLE `admins`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `bookings`
--
ALTER TABLE `bookings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `show_id` (`show_id`);

--
-- Indexes for table `movies`
--
ALTER TABLE `movies`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `shows`
--
ALTER TABLE `shows`
  ADD PRIMARY KEY (`id`),
  ADD KEY `movie_id` (`movie_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admins`
--
ALTER TABLE `admins`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `bookings`
--
ALTER TABLE `bookings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `movies`
--
ALTER TABLE `movies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `shows`
--
ALTER TABLE `shows`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bookings`
--
ALTER TABLE `bookings`
  ADD CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`show_id`) REFERENCES `shows` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `shows`
--
ALTER TABLE `shows`
  ADD CONSTRAINT `shows_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `movies` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
