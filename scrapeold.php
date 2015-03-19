<?php
/**
 * @package     Dumpmon Scraper
 * @copyright   2015 Davide Tampellini - FabbricaBinaria
 * @license     GNU GPL version 3 or later
 */

/*
 * https://twitter.com/i/search/timeline?f=realtime
 * &q=from%3Adumpmon%20since%3A2014-12-01%20until%3A2014-12-09
 * &include_available_features=0
 * &include_entities=0
 * &scroll_cursor=TWEET-542101187911499776-541932658931273728
 */

error_reporting(E_ALL);
ini_set('display_errors', 1);

$banner  = <<<BANNER
Dump Scraper - Twitter scraper (old tweets)
Copyright (C) 2015 FabbricaBinaria - Davide Tampellini
===============================================================================
Dump Scraper is Free Software, distributed under the terms of the GNU General
Public License version 3 or, at your option, any later version.
This program comes with ABSOLUTELY NO WARRANTY as per sections 15 & 16 of the
license. See http://www.gnu.org/licenses/gpl-3.0.html for details.
===============================================================================
BANNER;

echo "\n".$banner."\n";

$options = getopt('s:u:', array('since:', 'until:'));

if((!isset($options['s']) && !isset($options['until'])) || (!isset($options['u']) && !isset($options['until'])))
{
    echo "Please provide the `since` and `until` arguments\n";
    exit;
}

echo "\nMemory usage: ". memory_convert(memory_get_usage())."\n";

require_once __DIR__.'/assets/simple_html_dom.php';

$base_url   = 'https://twitter.com/i/search/timeline?f=realtime&q=';
$base_query = 'from:dumpmon since:%s until:%s';
$prev_day   = '1970-05-01';
$garbage    = 0;
$processed  = 0;

$twitter  = curl_init();
$pastebin = curl_init();

curl_setopt($twitter, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($twitter, CURLOPT_RETURNTRANSFER, true);

curl_setopt($pastebin, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($pastebin, CURLOPT_RETURNTRANSFER, true);

$since = isset($options['s']) ? $options['s'] : $options['since'];
$until = isset($options['u']) ? $options['u'] : $options['until'];

$origurl = $base_url.rawurlencode(sprintf($base_query, trim($since), trim($until)));

$processing = true;
$url        = $origurl;

while($processing)
{
    curl_setopt($twitter, CURLOPT_URL, $url);

    $json = json_decode(curl_exec($twitter));
    $html = str_get_html($json->items_html);

    $tweets = $html->find('.original-tweet');

    $garbage = 0;

    foreach ($tweets as $tweet)
    {
        if(!$link = $tweet->find('.twitter-timeline-link', 0))
        {
            continue;
        }

        $processed++;

        $pasteLink = $link->attr['data-expanded-url'];
        $timestamp = $tweet->find('.js-short-timestamp', 0)->attr['data-time'];
        $tweetid   = $tweet->attr['data-tweet-id'];

        $day = date('Y-m-d', $timestamp);

        if($day != $prev_day)
        {
            $prev_day = $day;
            echo "Processing day: ".$day."\n";
        }

        $folder = $day;

        if(!is_dir(__DIR__.'/data/raw/'.$folder))
        {
            mkdir(__DIR__.'/data/raw/'.$folder, 0777, true);
        }

        curl_setopt($pastebin, CURLOPT_URL, $pasteLink);

        sleep(3);

        $data = curl_exec($pastebin);

        if(!$data)
        {
            continue;
        }

        if(stripos($data, 'Pastebin.com has blocked your IP') !== false)
        {
            echo "IP blocked!!!\n";
            break;
        }

        if(stripos($data, 'has been removed') !== false)
        {
            $garbage++;
            continue;
        }

        file_put_contents(__DIR__.'/data/raw/'.$folder.'/'.$tweetid.'.txt', $data);
    }

    $html->clear();
    unset($html);

    // Let's setup the url for the next iteration
    $url = $origurl.'&scroll_cursor='.$json->scroll_cursor;

    $processing = $json->has_more_items;

    echo "    ...processed ".$processed." tweets\n";
    echo "      Found ".$garbage." garbage tweets in this batch\n";
}


echo "\nPeak memory usage: ".memory_convert(memory_get_peak_usage())."\n";
echo "Memory usage: ". memory_convert(memory_get_usage())."\n";

function memory_convert($size)
{
    $unit = array('b','kb','mb','gb','tb','pb');

    return @round($size/pow(1024,($i=floor(log($size,1024)))),2).' '.$unit[$i];
}
