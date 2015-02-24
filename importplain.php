<?php
/**
 * @package     Dumpmon Scraper
 * @copyright   2015 Davide Tampellini - FabbricaBinaria
 * @license     GNU GPL version 3 or later
 */

namespace Dumpmon;

use Dumpmon\Utils\Clioptions;

error_reporting(E_ALL);
ini_set('display_errors', 1);

require_once __DIR__.'/autoloader.php';

\Autoloader::getInstance()->addMap('Dumpmon\\', __DIR__ . '/Dumpmon');

$banner  = <<<BANNER
Dump Scraper - Plain password importer
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

$def_options = array(
    's:' => 'since:',
    'u:' => 'until:',
    'h'  => 'help',
    'f:' => 'file:'
);

$cli_options = getopt(implode(array_keys($def_options)), array_values($def_options));

$options = new Clioptions($cli_options, $def_options);

// Not enough data or the help is asked
if((!$options->since && !$options->file) || $options->help)
{
    $help = <<<HELP
  [-s]        Since date    Start date for processing file dump, format YYYY-MM-DD
  [--since]                 If an "until" date is not provided only this day is processed

  [-u]        Until date    Stop date for processing file dump, format YYYY-MM-DD
  [--until]

  [-f]        File          Process a specific file
  [--file]

  [-h]        Help          Show this help
  [--help]

HELP;

    echo $help;
    die();
}

$files = array();

if($options->file)
{
    if(!file_exists(realpath($options->file)))
    {
        echo "\nFile ".$options->file." does not exist";
        die();
    }

    $files[] = $options->file;
}
else
{
    $baseDir = __DIR__.'/data/processed/plain/';
    $folders[] = $baseDir.trim(($options->since));

    if($options->until)
    {
        $date = strtotime(trim($options->since));
        $end  = strtotime(trim($options->until));

        $date = strtotime('+1 day', $date);

        while($end >= $date)
        {
            $folders[] = $baseDir.date('Y-m-d', $date);
            $date = strtotime('+1 day', $date);
        }
    }

    // Ok, now that I have all the folders I can start extracting the single files
    foreach($folders as $folder)
    {
        if(!is_dir($folder))
        {
            continue;
        }

        $directory = new \DirectoryIterator($folder);

        foreach($directory as $fileInfo)
        {
            if($fileInfo->isDot() || $fileInfo->getFilename() == '.DS_Store')
            {
                continue;
            }

            $files[] = $fileInfo->getPathname();
        }
    }
}

$wordlist_temp = fopen(__DIR__.'/wordlists/temp.txt', 'w');
$i = 0;
$multiplier = 0;

foreach($files as $file)
{
    $handle = @fopen($file, 'r');

    if ($handle === false)
    {
        return false;
    }

    $prev_data  = '';
    $buffer     = 65536;

    while ( !feof($handle))
    {
        $data = $prev_data . fread($handle, $buffer);

        // Let's find the last occurrence of a new line
        $newLine = strrpos($data, "\n");

        // I didn't hit any EOL char, let's keep reading
        if ($newLine === false)
        {
            $prev_data = $data;
            continue;
        }
        else
        {
            // Gotcha! Let's roll back to its position
            $prev_data = '';
            $rollback  = strlen($data) - $newLine + 1;
            $len       = strlen($data);

            $data = substr($data, 0, $newLine);

            // I have to rollback only if I read the whole buffer (ie I'm not at the end of the file)
            // Using this trick should be much more faster than calling ftell to know where we are
            if ($len == $buffer)
            {
                fseek($handle, -$rollback, SEEK_CUR);
            }
        }

        fwrite($wordlist_temp, $data);
    }

    echo '.';
    $i++;

    if($i >= 75)
    {
        $multiplier += 1;
        echo sprintf('%8s', $i * $multiplier)."\n";
        $i = 0;
    }

    fclose($handle);
}

echo "\n";

fclose($wordlist_temp);