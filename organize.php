<?php

namespace Dumpmon;

error_reporting(E_ALL);
ini_set('display_errors', 1);

use Dumpmon\Organizer\Hash;
use Dumpmon\Organizer\Plain;
use Dumpmon\Organizer\Trash;

require_once __DIR__.'/autoloader.php';

\Autoloader::getInstance()->addMap('Dumpmon\\', __DIR__ . '/Dumpmon');

$options = getopt('fd:', array('dir:', 'force'));

$directory = 'training';
$csvDir    = 'training';
$mode      = 'wb';

if(isset($options['d']) || $options['dir'])
{
    $directory = 'data/'.(isset($options['d']) ? $options['d'] : $options['dir']);
    $csvDir    = 'data';
}

if(isset($options['f']) || $options['force'])
{
    $mode = 'ab';
}

$source = __DIR__.'/'.$directory;
$csv    = __DIR__.'/'.$csvDir.'/features.csv';

if(!is_dir($source))
{
    echo "\nDirectory ".$source." does not exist!";
    die();
}

echo "\nProcessing directory: ".$source."\n";

$features = fopen($csv, $mode);
fputcsv($features, array('Trash score', 'Plain score', 'Hash score', 'Label', 'Filename'));

$organizers = array(
    'trash' => new Trash(),
    'plain' => new Plain(),
    'hash'  => new Hash(),
);

echo "Memory usage: ". memory_convert(memory_get_usage())."\n";

$i        = 0;
$iterator = new \RecursiveIteratorIterator(new \RecursiveDirectoryIterator($source, \RecursiveDirectoryIterator::SKIP_DOTS));

/** @var \SplFileInfo $file */
foreach($iterator as $file)
{
    if($file->getFilename() == '.DS_Store' || $file->getFilename() == 'features.csv')
    {
        continue;
    }

    $i++;

    if($i >= 50)
    {
        $i = 0;

        echo "Memory usage: ". memory_convert(memory_get_usage())."\n";
    }

    /*if($file->getFilename() == '565184679196631041.txt')
    {
        $x = 1;
    }*/

    $data  = file_get_contents($file->getPathname());

    // Remove /r since they could mess up regex
    $data = str_replace("\r", '', $data);

    $info = array(
        'data'  => $data,
        'lines' => max(substr_count($data, "\n"), 1)
    );

    $line = array();

    foreach($organizers as $key => $organizer)
    {
        $organizer->reset();
        $organizer->setInfo($info);
        $organizer->analyze();

        $score = min($organizer->getScore(), 3);

        $line[$key] = round($score, 4);
    }

    switch(basename($file->getPath()))
    {
        case 'hash':
            $label = 1;
            break;
        case 'plain':
            $label = 2;
            break;
        case 'trash':
            $label = 0;
            break;
        default:
            $label = '';
            break;
    }

    $line['label'] = $label;
    $line['id']    = basename($file->getPath()).'/'.$file->getFilename();

    fputcsv($features, $line);
}

fclose($features);

function memory_convert($size)
{
    $unit = array('b','kb','mb','gb','tb','pb');

    return @round($size/pow(1024,($i=floor(log($size,1024)))),2).' '.$unit[$i];
}
