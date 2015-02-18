<?php
/**
 * @package     Dumpmon Scraper
 * @copyright   2015 Davide Tampellini - FabbricaBinaria
 * @license     GNU GPL version 3 or later
 */

require_once "vendor/autoload.php";

use Abraham\TwitterOAuth\TwitterOAuth;

$banner  = <<<BANNER
Dump Scraper - Twitter scraper
Copyright (C) 2015 FabbricaBinaria - Davide Tampellini
===============================================================================
Dump Scraper is Free Software, distributed under the terms of the GNU General
Public License version 3 or, at your option, any later version.
This program comes with ABSOLUTELY NO WARRANTY as per sections 15 & 16 of the
license. See http://www.gnu.org/licenses/gpl-3.0.html for details.
===============================================================================
BANNER;

echo "\n".$banner."\n";

if(!file_exists(__DIR__.'/settings.json'))
{
    echo "\nPlease rename the file settings-dist.json to settings.json and fill the required info\n";
    die();
}

$settings  = json_decode(file_get_contents(__DIR__.'/settings.json'));

if(!$settings->app_key || !$settings->app_secret || !$settings->token || !$settings->token_secret)
{
    echo "\nPlease fill the required info before continuing";
    die();
}

error_reporting(E_ALL);
ini_set('display_errors', 1);

// Ordinato dal più frequente al meno frequente
$ignore_list = array('has been removed');

$prev_day  = '1970-05-01';
$since_id  = $settings->last_id;
$max_id    = $settings->max_id;
$processed = 0;
$ch        = curl_init();

curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$connection = new TwitterOAuth($settings->app_key, $settings->app_secret, $settings->token, $settings->token_secret);

$params = array(
    'user_id'     => 'dumpmon',
    'screen_name' => 'dumpmon',
    'exclude_replies' => true,
    'include_rts '    => false,
    'count'       => $settings->limit
);

if($since_id)
{
    $params['since_id'] = $since_id;
}

// Let's fetch 500 tweets at maximum
while($processed <= $settings->processing_limit)
{
    if(!is_null($max_id))
    {
        $params['max_id'] = $max_id;
    }

    try
    {
        $tweets     = $connection->get("statuses/user_timeline", $params);
    }
    catch(\Exception $e)
    {
        echo "    Error while fetching tweets: ".$e->getMessage()."\n";
        echo "    Trying again in few moments\n";

        continue;
    }

    // No more tweets to process
    if(!$tweets)
    {
        break;
    }

    $garbage    = 0;
    $processed += count($tweets);

    foreach($tweets as $tweet)
    {
        $max_id  = is_null($max_id) ? $tweet->id : min($max_id, $tweet->id);
        $max_id -= 1;

        $since_id = max($since_id, $tweet->id);

        // No url? I'm not interested into
        if(!$tweet->entities->urls)
        {
            continue;
        }

        $link   = $tweet->entities->urls[0]->expanded_url;

        $day = date('Y-m-d', strtotime($tweet->created_at));

        if($day != $prev_day)
        {
            $prev_day = $day;
            echo "Processing day: ".$day."\n";
        }

        $folder = $day;

        if(!is_dir(__DIR__.'/data/raw/'.$folder))
        {
            mkdir(__DIR__.'/data/raw/'.$folder);
        }

        sleep($settings->delay);

        curl_setopt($ch, CURLOPT_URL, $link);

        $data = curl_exec($ch);

        if(!$data)
        {
            continue;
        }

        if(stripos($data, 'Pastebin.com has blocked your IP') !== false)
        {
            echo "IP blocked!!!\n";
            break 2;
        }

        // Ignore garbage as much as possible
        foreach($ignore_list as $ignore)
        {
            if(stripos($data, $ignore) !== false)
            {
                $garbage++;
                continue 2;
            }
        }

        file_put_contents(__DIR__.'/data/raw/'.$folder.'/'.$tweet->id.'.txt', $data);
    }

    echo "    ...processed ".$processed." tweets\n";
    echo "      Found ".$garbage." garbage tweets in this batch\n";
}

echo "\nTotal processed tweets: ".$processed."\n";

$settings->last_id = $since_id;
file_put_contents(__DIR__.'/settings.json', json_encode($settings, JSON_PRETTY_PRINT));