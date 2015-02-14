<?php

namespace Dumpmon;

use Dumpmon\Extractor\Hash;
use Dumpmon\Extractor\Plain;
use Dumpmon\Utils\Utils;

error_reporting(E_ALL);
ini_set('display_errors', 1);

require_once __DIR__.'/autoloader.php';

\Autoloader::getInstance()->addMap('Dumpmon\\', __DIR__ . '/Dumpmon');

$banner  = <<<BANNER
Dump Scraper - Extract info from dump files
Copyright (C) 2015 FabbricaBinaria - Davide Tampellini
===============================================================================
Dump Scraper is Free Software, distributed under the terms of the GNU General
Public License version 3 or, at your option, any later version.
This program comes with ABSOLUTELY NO WARRANTY as per sections 15 & 16 of the
license. See http://www.gnu.org/licenses/gpl-3.0.html for details.
===============================================================================
BANNER;

echo "\n".$banner."\n\n";

$options = getopt('s:u:ht', array('since:', 'until:', 'help', 'train'));

if(isset($options['h']) || isset($options['help']))
{
    $help = <<<HELP
  [-s]        Since date    Start date for processing file dump, format YYYY-MM-DD
  [--since]                 If an "until" date is not provided only this day is processed

  [-u]        Until date    Stop date for processing file dump, format YYYY-MM-DD
  [--until]

  [-h]        Help          Show this help
  [--help]

HELP;
    echo $help;
    die();
}

if(
    (!isset($options['s']) && !isset($options['since'])) &&
    (!isset($options['u']) && !isset($options['until']))
)
{
    echo "Please provide a start/until date\n";
    die();
}

$dates = array();

if(isset($options['s']) || isset($options['since']))
{
    $dates[] = (isset($options['s']) ? $options['s'] : $options['since']);
}

if(isset($options['u']) || isset($options['until']))
{
    $date = strtotime(isset($options['s']) ? $options['s'] : $options['since']);
    $end  = strtotime(isset($options['u']) ? $options['u'] : $options['until']);

    $date = strtotime('+1 day', $date);

    while($end >= $date)
    {
        $dates[] = date('Y-m-d', $date);
        $date = strtotime('+1 day', $date);
    }
}

foreach($dates as $date)
{
    $folders[] = 'hash/'.$date;
    $folders[] = 'plain/'.$date;
}

$extractors = array(
    'plain' => new Plain(),
    'hash'  => new Hash(),
);

foreach($folders as $folder)
{
    $source = __DIR__.'/data/organized/'.$folder;

    if(!is_dir($source))
    {
        continue;
    }

    echo "Directory    : ".$folder."\n";
    echo "Memory usage : ". Utils::memory_convert(memory_get_usage())."\n\n";

    $iterator = new \RecursiveIteratorIterator(new \RecursiveDirectoryIterator($source, \RecursiveDirectoryIterator::SKIP_DOTS));

    /** @var \SplFileInfo $file */
    foreach($iterator as $file)
    {
        if($file->getFilename() == '.DS_Store' || $file->getFilename() == 'features.csv')
        {
            continue;
        }

        /*if($file->getFilename() == '564938346234142721.txt')
        {
            $x = 1;
        }*/

        $data  = file_get_contents($file->getPathname());

        // Remove /r since they could mess up regex
        $data = str_replace("\r", '', $data);

        $info = array(
            'data' => $data,
        );

        $parts = explode('/', $file->getPath());
        $label = array_slice($parts, -2, 1);
        $label = $label[0];

        if(!isset($extractors[$label]))
        {
            continue;
        }

        /** @var \Dumpmon\Extractor\Extractor $extractor */
        $extractor = $extractors[$label];

        $extractor->reset();
        $extractor->setInfo($info);
        $extractor->analyze();

        $extracted = $extractor->getExtractedData();

        if($extracted)
        {
            $destination = __DIR__.'/data/processed/'.$label.'/'.basename($file->getPath());

            if(!is_dir($destination))
            {
                mkdir($destination, 0777, true);
            }

            file_put_contents($destination.'/'.$file->getFilename(), $extracted);
        }
    }
}