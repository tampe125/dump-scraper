<?php

namespace Dumpmon\Utils;

class Utils
{
    public static function memory_convert($size)
    {
        $unit = array('b','kb','mb','gb','tb','pb');

        return @round($size/pow(1024,($i=floor(log($size,1024)))),2).' '.$unit[$i];
    }
}