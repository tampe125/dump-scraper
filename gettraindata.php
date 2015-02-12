<?php

error_reporting(E_ALL);
ini_set('display_errors', 1);

$divider = str_repeat('=', 79);
$banner  = <<<BANNER
Dump Scraper - Get train data
Copyright (C) 2015 FabbricaBinaria - Davide Tampellini
$divider
Dump Scraper is Free Software, distributed under the terms of the GNU General
Public License version 3 or, at your option, any later version.
This program comes with ABSOLUTELY NO WARRANTY as per sections 15 & 16 of the
license. See http://www.gnu.org/licenses/gpl-3.0.html for details.
$divider
BANNER;

echo "\n".$banner."\n";

$source = __DIR__.'/data';
$target = __DIR__.'/training';

$iterator = new \RecursiveIteratorIterator(new \RecursiveDirectoryIterator($source, \RecursiveDirectoryIterator::SKIP_DOTS));

/** @var \SplFileInfo $file */
foreach($iterator as $file)
{
    // Prendiamo il 10% dei file come training
    if(rand(1, 10) == 1)
    {
        copy($file->getPathname(), $target.'/'.$file->getFilename());
    }
}