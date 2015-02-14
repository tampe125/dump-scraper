<?php

namespace Dumpmon\Extractor;

class Hash extends Extractor
{
    public function __construct()
    {
        $this->regex = array(
            // generic phpass hash
            '/(\$P\$.{31})/im',
            // raw md5
            '/([a-f0-9]{32})/im',
            // generic crpyt
            '/([a-z0-9\/\.]{13})[,\s\n]?$/im',
        );
    }

    public function analyze()
    {
        $data  = '';

        foreach($this->regex as $regex)
        {
            $data .= $this->extractData($regex)."\n";
        }

        $this->extracted = $data;
    }
}