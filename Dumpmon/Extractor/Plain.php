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
}