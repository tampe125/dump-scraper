<?php

error_reporting(E_ALL);
ini_set('display_errors', 1);

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