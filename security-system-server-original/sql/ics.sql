-- MySQL dump 10.13  Distrib 5.5.49, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: ics
-- ------------------------------------------------------
-- Server version	5.5.49-0+deb7u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `attackmap`
--

DROP TABLE IF EXISTS `attackmap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attackmap` (
  `time` varchar(30) CHARACTER SET utf8 DEFAULT NULL,
  `attacker` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `attackIP` varchar(30) CHARACTER SET utf8 DEFAULT NULL,
  `attackerGeo` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `targetGeo` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `attackType` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `port` int(11) DEFAULT NULL,
  `type` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attackmap`
--

LOCK TABLES `attackmap` WRITE;
/*!40000 ALTER TABLE `attackmap` DISABLE KEYS */;
/*!40000 ALTER TABLE `attackmap` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `location`
--

DROP TABLE IF EXISTS `location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `location` (
  `place` varchar(30) CHARACTER SET utf8 NOT NULL,
  `latitude` float(255,7) DEFAULT NULL,
  `longitude` float(255,7) DEFAULT NULL,
  PRIMARY KEY (`place`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `location`
--

LOCK TABLES `location` WRITE;
/*!40000 ALTER TABLE `location` DISABLE KEYS */;
/*!40000 ALTER TABLE `location` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `news`
--

DROP TABLE IF EXISTS `news`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news` (
  `id` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `time` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `con` longtext CHARACTER SET utf8,
  `title` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `url` varchar(255) CHARACTER SET utf8 NOT NULL,
  `source` varchar(25) CHARACTER SET utf8 DEFAULT NULL,
  `type` varchar(50) CHARACTER SET utf8 NOT NULL,
  PRIMARY KEY (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `news`
--

LOCK TABLES `news` WRITE;
/*!40000 ALTER TABLE `news` DISABLE KEYS */;
/*!40000 ALTER TABLE `news` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scadablog`
--

DROP TABLE IF EXISTS `scadablog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scadablog` (
  `time` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `title` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `content` mediumtext CHARACTER SET utf8,
  `author` varchar(20) CHARACTER SET utf8 DEFAULT NULL,
  `url` varchar(100) CHARACTER SET utf8 DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scadablog`
--

LOCK TABLES `scadablog` WRITE;
/*!40000 ALTER TABLE `scadablog` DISABLE KEYS */;
/*!40000 ALTER TABLE `scadablog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scadanews`
--

DROP TABLE IF EXISTS `scadanews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scadanews` (
  `title` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `source` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `sourceurl` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `type` varchar(20) CHARACTER SET utf8 DEFAULT NULL,
  `text1` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `fulltext` mediumtext CHARACTER SET utf8,
  `time` varchar(50) CHARACTER SET utf8 DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scadanews`
--

LOCK TABLES `scadanews` WRITE;
/*!40000 ALTER TABLE `scadanews` DISABLE KEYS */;
/*!40000 ALTER TABLE `scadanews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `weibo`
--

DROP TABLE IF EXISTS `weibo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `weibo` (
  `id` bigint(20) DEFAULT NULL,
  `classify` int(11) DEFAULT NULL,
  `con` varchar(300) CHARACTER SET utf8 DEFAULT NULL,
  `date` varchar(20) CHARACTER SET utf8 DEFAULT NULL,
  `fans` int(11) DEFAULT NULL,
  `following` int(11) DEFAULT NULL,
  `location` varchar(20) CHARACTER SET utf8 DEFAULT NULL,
  `uid` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `headpic` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `repostcount` int(11) DEFAULT NULL,
  `username` varchar(50) CHARACTER SET utf8 DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `weibo`
--

LOCK TABLES `weibo` WRITE;
/*!40000 ALTER TABLE `weibo` DISABLE KEYS */;
/*!40000 ALTER TABLE `weibo` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-08-08 20:58:31
