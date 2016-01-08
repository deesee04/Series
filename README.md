[![Build Status](https://travis-ci.org/reticulatingspline/Series.svg?branch=master)](https://travis-ci.org/reticulatingspline/Series)

// dc

// some things were broken, so i swapped some services and made the functions do what they said they would do. nothing fancy. 

// TODO: replace tv function

# Supybot / Limnoria plugin for displaying TV / movie / IMDB information

## Introduction

This is based off of Hoaas' [plugin](https://github.com/Hoaas/Supybot-plugins/tree/master/Series) of the same name.

I rewrote a bit of it but it largely maintains the same functionality to display information about TV and Movie information.

## Install

You will need a working Limnoria bot on Python 2.7 for this to work.

Go into your Limnoria plugin dir, usually ~/supybot/plugins and run:

```
git clone https://github.com/reticulatingspline/Series
```

To install additional requirements, run:

```
pip install -r requirements.txt 
```

Next, load the plugin:

```
/msg bot load Series
```

You're done.

## Example Usage

```
<spline> @ep Breaking Bad
<myybot> Breaking Bad :: Previous: 5x16 Name: Felina Date: 2013-09-29 :: Next:  Name:  Date:
<spline> @movie Batman
<myybot> Batman (1989) || 126 min || 7.6 || tt0096895
<myybot> Director: Tim Burton || Actors: Michael Keaton, Jack Nicholson, Kim Basinger, Robert Wuhl
<myybot> Gotham City: dark, dangerous, 'protected' only by a mostly corrupt police department. Despite the best efforts of D.A. Harvey Dent and police commissioner Jim Gordon,
the city becomes increasingly unsafe...until a Dark Knight arises. We all know criminals are a superstitious, cowardly lot...so his disguise must be able to strike
terror into their hearts. He becomes a bat. Enter Vicky Vale, a prize-winning (2 more messages)
<spline> @tv Breaking Bad
<myybot> [ Showname ] - Breaking Bad [ Status ] - Ended
<myybot> [ Started ] - Jan/20/2008 [ Ended ] - Sep/29/2013
<myybot> [ Genres ] - Crime | Drama | Thriller [ URL ] - http://www.tvrage.com/Breaking_Bad
```

## About

All of my plugins are free and open source. When I first started out, one of the main reasons I was
able to learn was due to other code out there. If you find a bug or would like an improvement, feel
free to give me a message on IRC or fork and submit a pull request. Many hours do go into each plugin,
so, if you're feeling generous, I do accept donations via Amazon or browse my [wish list](http://amzn.com/w/380JKXY7P5IKE).

I'm always looking for work, so if you are in need of a custom feature, plugin or something bigger, contact me via GitHub or IRC.