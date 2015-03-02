<?php
/**
 * @package     Dumpmon Scraper
 * @copyright   2015 Davide Tampellini - FabbricaBinaria
 * @license     GNU GPL version 3 or later
 */

namespace Dumpmon\Extractor;

class Hash extends Extractor
{
    public function __construct()
    {
        $this->regex = array(
            // generic phpass hash
            '/(\$P\$.{31})/im',
            // md5 crypt
            '/(\$1\$.{8}\$.{22})/im',
            // phpass md5
            '/(\$H\$9.{30})/m',
            // Drupal
            '/(\$S\$.{52})/m',
            // mysql
            '/(\*[a-f0-9]{40})/im',
            // raw md5
            '/([a-f0-9]{32})/im',
            // generic crpyt
            '/([a-z0-9\/\.]{13})[,\s\n]?$/im',
            // sha1
            '/(\b[0-9a-f]{40}\b)/im',
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

    /**
     * Overwrites the parent function, so we can perform some sanity checks on the matched string
     *
     * @param array $matches
     *
     * @return string
     */
    protected function replaceMatches($matches)
    {
        if(isset($matches[1]))
        {
            // Let's perform some sanity checks on the matched string
            $string = trim($matches[1]);

            // Is this a debug string?
            $skip = (strpos($string, '000') !== false);

            // If the skip flag is not set, let's add the string to the matches
            if(!$skip)
            {
                $this->matches[] = $string;
            }
        }

        return '';
    }
}