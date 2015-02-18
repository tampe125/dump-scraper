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

$settings  = json_decode(file_get_contents(__DIR__.'/settings.json'));

if(!$settings->db_host || !$settings->db_user || !$settings->db_pwd || !$settings->db_name)
{
    echo "\nPlease fill the connection details to the database";
    die();
}

// Ok, let's try to connect to the database
$mysql = new \mysqli($settings->db_host, $settings->db_user, $settings->db_pwd, $settings->db_name);
if($mysql->connect_error)
{
    echo "\nFailed to connect to MySQL: ".$mysql->connect_error;
    die();
}

$def_options = array(
    's:' => 'since:',
    'u:' => 'until:',
    'h'  => 'help',
    'f:' => 'file:',
    'k:' => 'skip:'
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

  [-k]        Skip lines    Skip N lines at the beginning
  [--skip]

  [-f]        File          Process a specific file
  [--file]

  [-h]        Help          Show this help
  [--help]

HELP;

    echo $help;
    die();
}

$files = array();
$skip  = (int) $options->skip;

if($options->file)
{
    if(!file_exists(realpath($options->file)))
    {
        echo "\nFile ".$options->file." does not exist";
        die();
    }

    $files[] = $options->file;
}

foreach($files as $file)
{
    $handle = @fopen($file, 'r');

    if ($handle === false)
    {
        return false;
    }

    $prev_data  = '';
    $buffer     = 65536;
    $i          = 0;
    $multiplier = 0;

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

        $lines = explode("\n", $data);

        foreach($lines as $line)
        {
            $i++;

            // Do I have to skip some lines?
            if($i <= $skip)
            {
                continue;
            }

            $line = trim($line);
            $line = $mysql->escape_string($line);

            $query = <<<SQL
INSERT `raw` (`word`, `occurrences`) VALUES ('$line', 1)
ON DUPLICATE KEY UPDATE
`occurrences` = `occurrences` + 1
SQL;
            $mysql->query($query);

            if($mysql->error)
            {
                echo "\n\tAn error occurred while inserting a row: ".$mysql->error;
                echo "\n\tError occurred at line ".$i;
                die();
            }

            if($i % 100 == 0)
            {
                echo '.';
            }

            if($i >= 70 * 100)
            {
                $multiplier += 1;
                echo sprintf('%7s', $i * $multiplier)."\n";
                $i = 0;
            }
        }
    }

    echo "\n\n";

    fclose($handle);
}