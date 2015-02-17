<?php

namespace Dumpmon\Extractor;

class Plain extends Extractor
{
    protected $emailRegex = "[a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}";

    public function __construct()
    {
        $this->regex = array(
            // URL with passwords
            '/[ht|f]tp[s]*:\/\/\w+\:(.*)\@\w*\.\w*/',
            // Extracts data displayed in columns: Davison 	Yvonne 	library
            '/^'.$this->emailRegex.'\s?\t.*?\t.*?\t(.*?)$/im',
            // Standalone passwords
            '/pass(?:word)?\s*?[:|=](.*?$)/im',
            // email - password
            '/^"?'.$this->emailRegex."\s?[\/|;|:|\||,|".'\t'."]\s?(.*?)[:".'\n"'."]/im",
            // password email
            "/(?:.*?:)?(.*?)[\s|\/|;|:|\||,|".'\t'."]".$this->emailRegex."\s*?$/im",
            // username - password
            '/^[a-z0-9\-]{5,15}:(.*?)$/im'
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

            // Is it too long?
            $skip = strlen($string) > 20;

            if(!$skip)
            {
                // Does it contain some wrong character?
                $chars = array(' ', "\t", "\n");

                foreach($chars as $char)
                {
                    if(strpos($string, $char) !== false)
                    {
                        $skip = true;
                        break;
                    }
                }
            }

            // If the skip flag is not set, let's add the string to the matches
            if(!$skip)
            {
                $this->matches[] = $string;
            }
        }

        return '';
    }
}